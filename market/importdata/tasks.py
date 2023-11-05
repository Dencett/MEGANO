# import time
import os
import json

from django.conf import settings
from django.db import transaction, DatabaseError, IntegrityError
from config.celery import app
from celery.utils.log import get_task_logger
from pydantic import ValidationError
from json.decoder import JSONDecodeError

from products.models import Product, ProductDetail, Detail, Manufacturer, Category
from shops.models import Offer, Shop
from importdata.services import ProductPydantic


logger = get_task_logger(__name__)


@app.task(bind=True)
def load_files(self, files, email):
    # A task being bound means the first argument to the task will
    # always be the task instance (self), just like Python bound methods:
    """
    Задача Сelery. Импорт файлов.
    :param self:
    :param files:
    :param email:
    :return:
    """
    file_total = 0
    failed_file = 0
    successed_file = 0
    total_product = 0
    total_loaded_product = 0
    total_failed_product = 0
    formats = ["json"]
    folder_name = settings.IMPORT_FOLDER

    try:
        folder_path, dir_files = get_folder_path_and_files(folder_name)
    except FileNotFoundError as e:
        logger.critical(e)
    else:
        if not files:
            files = dir_files
            logger.critical("Файлы не выбраны, импорт инициирован из всех файлов находящихся в '%s'." % folder_name)
            # print("Файлы не выбраны, импорт инициирован из всех файлов находящихся в '%s'." % folder_name)

        for file in files:
            logger.info("Импорт файла %s..." % file)
            # print("Импорт файла %s..." % file)
            file_total += 1

            try:
                file_name, fmt = parse_name(file_name=file, formats=formats)
                file_path = os.path.abspath(os.path.join(folder_name, file))

                if file in dir_files:
                    with open(file_path, "r", encoding="utf-8") as f:
                        products = json.load(f)

                        l, f, t = load(products)

                else:
                    raise OSError("Файла нет папке '%s'" % folder_name)

            except (DatabaseError, JSONDecodeError, OSError) as e:
                failed_file += 1
                os.rename(
                    os.path.abspath(os.path.join(folder_name, file)),
                    os.path.join(folder_path, "failed_import_files", file),
                )
                logger.critical("Файл '%s' не импортирован. %s: %s" % (file, type(e), e))
                # print("Файл '%s' не импортирован: %s: %s" % (file, type(e), e))

            else:
                total_loaded_product += l
                total_failed_product += f
                total_product += t
                successed_file += 1
                os.rename(file_path, os.path.join(folder_path, "success_import_files", file_name))

                if f > 0:
                    logger.warning(
                        "Файл %s импортирован не полностью. Импортировано %d из %d продуктов." % (file, l, t)
                    )
                    # print("Файл %s импортирован не полностью. Импортировано %d из %d продуктов." % (file, l, t))
                else:
                    logger.info("Импорт файла '%s' завершен. Импортировано %d из %d продуктов." % (file, l, t))
                    # print("Импорт файла '%s' завершен. Импортировано %d из %d продуктов." % (file, l, t))

        logger.info("Импортированно %d файлов из %d" % (successed_file, file_total))
        logger.info(
            "Импортированно %d из %d продуктов из %d файлов" % (total_loaded_product, total_product, successed_file)
        )
        # print("Импортированно %d файлов из %d" % (successed_file, file_total))
        # print("Импортированно %d из %d продуктов из %d файлов" %
        #       (total_loaded_product, total_product, successed_file)
        #       )
        # mail_import_report(email)


def load(products):
    """
    Импорт проудктов из файла.
    :param products:
    :return:
    """
    total_objects = 0
    loaded_object_count = 0
    failed_object_count = 0
    obj_count = 0

    for product_data in products:
        total_objects += 1
        obj_count += 1
        logger.info("Импорт продукта №%d..." % obj_count)
        # print("Импорт продукта №%d..." % obj_count)
        try:
            obj = ProductPydantic(**product_data)

            with transaction.atomic():
                shop = get_and_validate_shop(obj)
                manufacturer = get_or_create_manufacturer(obj)

                try:
                    product = Product.objects.get(name=obj.name)

                except Product.DoesNotExist:
                    create_product(obj, manufacturer, shop)
                    logger.info("Продукт №%d(%s) импортирован успешно" % (obj_count, obj.name))
                    # print("Продукт №%d(%s) импортирован успешно" % (obj_count, obj.name))
                else:
                    update_product(obj, manufacturer, product, shop)
                    logger.info("Продукт №%d(%s) обновлен успешно" % (obj_count, obj.name))
                    # print("Продукт №%d(%s) обновлен успешно" % (obj_count, obj.name))

                loaded_object_count += 1

        except DatabaseError:
            raise

        except ValidationError as e:
            failed_object_count += 1
            logger.error(
                "Продукт №%d не импортирован. %s: продукт содержит ошибки валидации в кол-ве: %s шт"
                % (obj_count, type(e), e.error_count())
            )
            # print("Продукт №%d не импортирован. %s: продукт содержит %s ошибки валидации" %
            #       (obj_count, type(e), e.error_count())
            #       )

        except (ValueError, FileNotFoundError, IntegrityError) as e:
            failed_object_count += 1
            logger.error("Продукт №%d(%s) не импортирован: %s %s" % (obj_count, product_data["name"], type(e), e))
            # print("Продукт №%d(%s) не импортирован: %s %s" % (obj_count, product_data['name'], type(e), e))

        except Exception as e:
            failed_object_count += 1
            logger.warning(
                "Продукт №%d(%s) не импортирован, необработаная ошибка: %s %s"
                % (obj_count, product_data["name"], type(e), e)
            )
            # print("Продукт №%d(%s) не импортирован, необработаная ошибка: %s %s" %
            #       (obj_count, product_data['name'], type(e), e)
            #       )

    return loaded_object_count, failed_object_count, total_objects


def create_product(obj, manufacturer, shop):
    """
    Создание сущности Продукт.
    :param obj:
    :param manufacturer:
    :param shop:
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

    img_name, img_path = parse_img_name_and_validate(obj.preview)
    # add image
    with open(img_path, "rb") as f:
        product.preview.save(img_name, f, save=True)

    # get or create details and create product_details
    product_details_create_or_update(obj, product)

    # create offer
    offer = Offer(product=product, shop=shop, price=obj.offer.price, remains=obj.offer.quantity)

    offer.save()


def update_product(obj, manufacturer, product, shop):
    """
    Обнавление сущности Продукт.
    :param obj:
    :param manufacturer:
    :param product:
    :param shop:
    :return:
    """
    # update_product
    product.category = category_create(obj)
    product.manufacturer = manufacturer
    product.about = obj.about
    product.description = obj.description
    product.save()

    # delete if image
    product.preview.delete(save=True)

    img_name, img_path = parse_img_name_and_validate(obj.preview)
    # add image
    with open(img_path, "rb") as f:
        product.preview.save(img_name, f, save=True)

    product_details_create_or_update(obj, product, update=True)

    try:
        offer = Offer.objects.get(product=product, shop=shop)
        # update offer
        offer.price = obj.offer.price
        offer.remains += obj.offer.quantity
    except Offer.DoesNotExist:
        # create new offer
        Offer(product=product, shop=shop, price=obj.offer.price, remains=obj.offer.quantity)


def get_and_validate_shop(obj):
    """Получение сущности Магазин."""
    try:
        shop = Shop.objects.get(name=obj.shop)
    except Shop.DoesNotExist:
        raise ValueError("Магазина '%s' нет базе данных" % obj.shop)
    else:
        return shop


def get_or_create_manufacturer(obj):
    """
    Получении или создание сущности Производитель.
    :param obj:
    :return:
    """
    try:
        manufacturer = Manufacturer.objects.get(name=obj.manufacturer.name)
    except Manufacturer.DoesNotExist:
        manufacturer = Manufacturer.objects.create(name=obj.manufacturer.name, slug=obj.manufacturer.slug)

    return manufacturer


def category_create(obj):
    """
    Получения или создание сущности Категория с попутным созданием подкатегории.
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


def product_details_create_or_update(obj, product, update=False):
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


def detail_must_be_unique_validator(v):
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


def parse_img_name_and_validate(file_path):
    """
    Получение названия изображения, валидация формата изображения и его пути.
    :param file_path:
    :return:
    """
    # allowed_extensions = validators.get_available_image_extensions()
    allowed_extensions = ["jpg", "jpeg", "img", "webp", "png", "gif", "svg", "bmp"]

    # Валидация пути
    if len(file_path) == 0:
        raise ValueError("Не задан путь к изображению.")
    if len(file_path) < 5:
        raise ValueError("Путь '%s' к изображению короче 4 символов." % file_path)

    file_path = settings.MEDIA_ROOT + os.path.join(os.sep, file_path)

    if os.path.isfile(file_path):
        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension[1:] in allowed_extensions:
            file_name = os.path.basename(file_path)
            return file_name, file_path
        else:
            raise ValueError("Формат изображения '%s' не поддерживается." % file_extension)
    else:
        raise FileNotFoundError("Файла изображения не существует или путь '%s' недействителен." % file_path)


def parse_name(file_name, formats):
    """
    Получения названия и формата файла с валидацией.
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


def get_folder_path_and_files(folder_name: str):
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


# @app.task(bind=True)
# def mail_import_report(self, errors, email):
#     subject = 'Report from file importing service'
#     html_content = '<h1>Отчет"</h1><p>Импортированно
#     {successed_file} файла из {file_total}.</p>'.
#     format(successed_file, file_total)
#     if len(failed_file)>0:
#         content = ''
#     email_from = settings.EMAIL_HOST_USER
#     recipient_list = [settings.EMAIL_HOST_USER, ]
#     msg = EmailMessage(subject, html_content, email_from, recipient_list)
#     msg.content_subtype = 'html'
#     msg.send()
#     res = celery_test.delay()
#     time.sleep(5)
#     print(res.id)
#     print(res.status)
