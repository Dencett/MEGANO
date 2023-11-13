import os
import json
import time

from typing import List, Dict, Optional, Tuple, Union
from django.core.mail import EmailMessage
from django.conf import settings
from django.core.cache import cache
from django.db import transaction, DatabaseError, IntegrityError
from config.celery import app
from celery.utils.log import get_task_logger
from pydantic import ValidationError
from json.decoder import JSONDecodeError

from products.models import Product, ProductDetail, Detail, Manufacturer, Category, Tag
from shops.models import Offer, Shop
from importdata.services import ProductPydantic, DetailsPydantic


logger = get_task_logger(__name__)


# noqa: C901
@app.task(ignore_result=True, name="importdata.tasks.load_files")
def load_files(files: Tuple[Optional[str]], email_to: Optional[str]) -> None:  # noqa: C901
    """
    Задача Сelery. Импорт файлов.
    :param files:
    :param email_to:
    :return:
    """
    file_total: int = 0
    failed_file: int = 0
    successed_file: int = 0
    total_product: int = 0
    total_loaded_product: int = 0
    total_failed_product: int = 0
    formats: List[str] = ["json"]
    folder_name: str = settings.IMPORT_FOLDER
    excp: Optional[Dict] = {}

    cache_key = "import_is_running"
    cache.set(key=cache_key, value=True)

    # set delay to imitate a complicated task
    time.sleep(20)

    try:
        folder_path, dir_files = get_folder_path_and_files(folder_name)
    except FileNotFoundError as e:
        logger.critical(e)
    else:
        if not files:
            files = dir_files
            logger.warning("Файлы не выбраны, импорт инициирован из всех файлов находящихся в '%s'." % folder_name)

        for file in files:
            logger.info("Импорт файла %s..." % file)
            file_total += 1

            try:
                file_name, fmt = parse_name(file_name=file, formats=formats)
                file_path = os.path.abspath(os.path.join(folder_name, file))

                if file in dir_files:
                    with open(file_path, "r", encoding="utf-8") as f:
                        products = json.load(f)

                        l, f, t, e = load(products)

                else:
                    raise FileNotFoundError("Файла нет папке '%s'" % folder_name)

            except (DatabaseError, JSONDecodeError, FileNotFoundError, BaseException) as e:
                failed_file += 1
                excp[file] = [e]
                if not isinstance(e, FileNotFoundError):
                    os.rename(
                        os.path.abspath(os.path.join(folder_name, file)),
                        os.path.join(folder_path, "failed_import_files", file),
                    )
                logger.critical("Файл '%s' не импортирован. %s: %s" % (file, type(e), e))

            else:
                total_loaded_product += l
                total_failed_product += f
                total_product += t
                successed_file += 1
                os.rename(file_path, os.path.join(folder_path, "success_import_files", file_name))

                if f > 0:
                    excp[file] = e
                    logger.warning(
                        "Файл %s импортирован не полностью. Импортировано %d из %d продуктов." % (file, l, t)
                    )
                else:
                    logger.info("Импорт файла '%s' завершен. Импортировано %d из %d продуктов." % (file, l, t))

        logger.info("Всего импортированно %d файлов из %d" % (successed_file, file_total))
        logger.info(
            "Всего импортированно %d из %d продуктов из %d файлов"
            % (total_loaded_product, total_product, successed_file)
        )

        if email_to:
            mail_report(files, file_total, successed_file, excp, email_to)
            logger.info("Отчет отправлен на слeдующий адреc: %s" % email_to)

        else:
            logger.info("Отчет не отправлен. Адрес для отправки отчета не указан")

        cache.set(key=cache_key, value=False)


def load(products) -> tuple[int, int, int, List[Optional[Exception]]]:
    """
    Импорт проудктов из файла.
    :param products:
    :return:
    """
    total_objects: int = 0
    loaded_object_count: int = 0
    failed_object_count: int = 0
    obj_count: int = 0
    excp: List[Union[Exception]] = []

    for product_data in products:
        total_objects += 1
        obj_count += 1
        logger.info("Импорт продукта №%d..." % obj_count)
        try:
            obj: ProductPydantic = ProductPydantic(**product_data)

            with transaction.atomic():
                shop = get_and_validate_shop(obj)
                manufacturer = get_or_create_manufacturer(obj)
                tags = get_or_create_tag(obj)

                try:
                    product = (
                        Product.objects.select_related("manufacturer", "category")
                        .prefetch_related("details", "tags")
                        .get(name=obj.name)
                    )

                except Product.DoesNotExist:
                    create_product(obj, manufacturer, shop, tags)
                    logger.info("Продукт №%d(%s) импортирован успешно" % (obj_count, obj.name))
                else:
                    update_product(obj, manufacturer, product, shop, tags)
                    logger.info("Продукт №%d(%s) обновлен успешно" % (obj_count, obj.name))

                loaded_object_count += 1

        except DatabaseError:
            raise

        except ValidationError as e:
            failed_object_count += 1
            excp.append(e)
            logger.error(
                "Продукт №%d не импортирован. %s: продукт содержит ошибки валидации в кол-ве: %s шт"
                % (obj_count, type(e), e.error_count())
            )

        except (ValueError, FileNotFoundError, IntegrityError) as e:
            failed_object_count += 1
            excp.append(e)
            logger.error("Продукт №%d(%s) не импортирован: %s %s" % (obj_count, product_data["name"], type(e), e))

        except Exception as e:
            failed_object_count += 1
            excp.append(e)
            logger.warning(
                "Продукт №%d(%s) не импортирован, необработаная ошибка: %s %s"
                % (obj_count, product_data["name"], type(e), e)
            )

    return loaded_object_count, failed_object_count, total_objects, excp


def create_product(obj: ProductPydantic, manufacturer: Manufacturer, shop: Shop, tags: Optional[List[Tag]]) -> None:
    """
    Создание сущности Продукт.
    :param obj:
    :param manufacturer:
    :param shop:
    :param tags:
    :return:
    """
    # create product
    product = Product.objects.create(
        name=obj.name,
        category=category_create(obj),
        about=obj.about,
        description=obj.description,
        manufacturer=manufacturer,
    )
    # add tags if any
    product.tags.add(*tags)
    product.save()

    img_name, img_path = parse_img_name_and_validate(obj.preview)
    # add image
    with open(img_path, "rb") as f:
        product.preview.save(img_name, f, save=True)

    # get or create details and create product_details
    product_details_create_or_update(obj, product)

    # create offer
    offer = Offer(product=product, shop=shop, price=obj.offer.price, remains=obj.offer.quantity)
    offer.save()


def update_product(obj: ProductPydantic, manufacturer: Manufacturer, product: Product, shop: Shop, tags) -> None:
    """
    Обнавление сущности Продукт.
    :param obj:
    :param manufacturer:
    :param product:
    :param shop:
    :param tags:
    :return:
    """
    # update_product
    product.category = category_create(obj)
    product.manufacturer = manufacturer
    product.about = obj.about
    product.description = obj.description
    # clear current tags if any and add new if any
    product.tags.clear()
    product.tags.add(*tags)
    product.save()

    # delete image if any
    product.preview.delete(save=True)

    img_name, img_path = parse_img_name_and_validate(obj.preview)
    # add image
    with open(img_path, "rb") as f:
        product.preview.save(img_name, f, save=True)

    product_details_create_or_update(obj, product, update=True)

    try:
        offer = Offer.objects.select_related("shop", "product").get(product=product, shop=shop)
        # update offer
        offer.price = obj.offer.price
        offer.remains += obj.offer.quantity
        offer.save()
    except Offer.DoesNotExist:
        # create new offer
        Offer(product=product, shop=shop, price=obj.offer.price, remains=obj.offer.quantity)


def get_and_validate_shop(obj: ProductPydantic) -> Shop:
    """Получение сущности Магазин."""
    try:
        shop = Shop.objects.get(name=obj.shop)
    except Shop.DoesNotExist:
        raise ValueError("Магазина '%s' нет базе данных" % obj.shop)
    else:
        return shop


def get_or_create_manufacturer(obj: ProductPydantic) -> Manufacturer:
    """
    Получение или создание сущности Производитель.
    :param obj:
    :return:
    """
    try:
        manufacturer = Manufacturer.objects.get(name=obj.manufacturer.name)
    except Manufacturer.DoesNotExist:
        manufacturer = Manufacturer.objects.create(name=obj.manufacturer.name, slug=obj.manufacturer.slug)

    return manufacturer


def get_or_create_tag(obj: ProductPydantic) -> Optional[List[Tag]]:
    """
    Получение списка сущностей Тag.
    :param obj:
    :return:
    """
    tags = []
    for tag_name in obj.tags:
        tag, created = Tag.objects.get_or_create(name=tag_name)
        tags.append(tag)

    return tags


def category_create(obj: ProductPydantic) -> Category:
    """
    Получение или создание сущности Категория с попутным созданием подкатегории.
    :param obj:
    :return:
    """
    if obj.category.parent:
        # create parent category
        parent, created = Category.objects.get_or_create(name=obj.category.parent)
        parent.slug = obj.category.par_slug
        parent.save()
        # get or create main category if it needs
        category, created = Category.objects.get_or_create(name=obj.category.name)
        category.parent = parent
        category.slug = obj.category.cat_slug
        category.save()

    else:
        # get or create main category with Null parent
        category, created = Category.objects.get_or_create(name=obj.category.name, parent=None)
        category.slug = obj.category.cat_slug
        category.save()

    return category


def product_details_create_or_update(obj: ProductPydantic, product: Product, update=False) -> None:
    """
    Создание или обновление свойств продукта и его характеристик.
    :param obj:
    :param product:
    :param update:
    :return:
    """
    detail_must_be_unique_validator(obj.details)

    if update:
        ProductDetail.objects.filter(product=product).delete()

    for item in obj.details:
        detail, created = Detail.objects.get_or_create(name=item.name)
        product_detail = ProductDetail(product=product, detail=detail, value=item.value)
        product_detail.save()


def detail_must_be_unique_validator(v: List[Optional[DetailsPydantic]]) -> None:
    """
    Валидация параметров продукта по уникальности.
    :param v:
    :return:
    """
    details = []
    for item in v:
        if item.name not in details:
            details.append(item.name)
        else:
            raise ValueError("Свойство продукта '%s' дублируется" % item.name)


def parse_img_name_and_validate(file_path: str) -> tuple[str, str]:
    """
    Получение названия изображения, валидация формата изображения и его пути.
    :param file_path:
    :return:
    """
    allowed_extensions: List[str] = ["jpg", "jpeg", "img", "webp", "png", "gif", "svg", "bmp"]

    # Валидация пути
    if len(file_path) == 0:
        raise ValueError("Не задан путь к изображению.")
    if len(file_path) < 5:
        raise ValueError("Путь '%s' к изображению короче 4 символов." % file_path)

    if os.path.isfile(file_path):
        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension[1:] in allowed_extensions:
            file_name = os.path.basename(file_path)
            return file_name, file_path
        else:
            raise ValueError("Формат изображения '%s' не поддерживается." % file_extension)
    else:
        raise FileNotFoundError("Файл изображения не существует или путь '%s' недействителен." % file_path)


def parse_name(file_name: str, formats: List[str]) -> tuple[str, str]:
    """
    Получение названия и формата файла с валидацией.
    """
    parts = file_name.rsplit(".", 2)

    if len(parts) > 1:
        if parts[-1] in formats:
            fmt = parts[-1]
        else:
            raise OSError("Формат файла '%s' не поддерживается." % parts[-1])
    else:
        raise OSError("Формат файла не задан")

    return file_name, fmt


def get_folder_path_and_files(folder_name: str) -> tuple[str, List[Optional[str]]]:
    """
    Получение файлов из папки для импорта продуктов.
    :param folder_name:
    :return:
    """
    folder_path = os.path.abspath(folder_name)

    if not os.path.exists(folder_path):
        raise FileNotFoundError("Директория '%s' не существует." % folder_name)

    files = [file for file in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file))]

    return folder_path, files


def mail_report(
    files: Tuple[Optional[str]], file_total: int, successed_file: int, excp: Dict, email_to: Optional[str]
) -> None:
    """
    Отправка отчета по завершению команды ипорта продуктов.
    :param files:
    :param file_total:
    :param successed_file:
    :param excp:
    :param email_to:
    :return:
    """
    subject: str = "Отчет по заврешнению команды импорта продутков"
    html_content = html_content_maker(files, file_total, successed_file, excp)
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email_to]
    msg = EmailMessage(subject, html_content, email_from, recipient_list)
    msg.content_subtype = "html"
    msg.send()


def html_content_maker(files: Tuple[Optional[str]], file_total: int, successed_file: int, excp: Dict) -> str:
    """
    Получения контента собщения в html.
    :param files:
    :param file_total:
    :param successed_file:
    :param excp:
    :return:
    """
    html_content = "<h1>Отчет:</h1><p>Импортированно %d файлов из %d.</p>" % (successed_file, file_total)

    if excp:
        html_content += "<h2>Ошибки в следующих файлах: </h2>"
        for file in files:
            errors = excp.get(file)
            if errors:
                html_content += "<h3><b>'%s':</b></h3>" % file
                errors_count = 0
                for error in errors:
                    errors_count += 1
                    html_content += "<p>%d) %s</p>" % (errors_count, error)

    else:
        html_content += "<h2>Ошибкок не выявлено.</h2>"

    return html_content
