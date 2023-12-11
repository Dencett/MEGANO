# Интернет-магазин MEGANO
Владелец торгового центра во время COVID-карантина решил перевести своих арендодателей в онлайн. Сделать это он намерен с помощью создания платформы, на которой продавцы смогут разместить информацию о себе и своём товаре. Онлайновый торговый центр или, другими словами, интернет-магазин, являющийся агрегатором товаров различных продавцов.

## Как установить
Для работы сервиса требуются:
- Python версии не ниже 3.10.
- установленное ПО для контейнеризации - [Docker](https://docs.docker.com/engine/install/).
- Инструмент [poetry](https://python-poetry.org/) для управления зависимостями и сборкой пакетов в Python.

Настройка переменных окружения
1. Скопируйте файл .env.dist в .env
2. Заполните .env файл. Пример:
```yaml
DATABASE_URL = postgresql://skillbox:secret@127.0.0.1:5431/market
REDIS_URL = redis://127.0.0.1:6379/0
SECRET_KEY = "django-insecure-=e-i4dlx_qq&ra7un4)u8bdr#08q)gc_*yyy4@7--kt(0(p#!("
DEBUG = True
ALLOWED_HOSTS = www.allowed.com www.host.com
EMAIL_HOST = "smtp.gmail.com"
EMAIL_HOST_USER = "example@gmail.com"
EMAIL_HOST_PASSWORD = "example password"
```

Запуск СУБД Postgresql
```shell
docker run --name skillbox-db-31 -e POSTGRES_USER=skillbox -e POSTGRES_PASSWORD=secret -e POSTGRES_DB=market -p 5431:5432 -d postgres
```
Запуск брокера сообщений REDIS
```shell
docker run --name redis-db -d -p 6379:6379 redis
```
Установка и активация виртуального окружения
```shell
poetry install  ; установка пакетов
poetry shell  ; активация виртуального окружения
pre-commit install  ; установка pre-commit для проверки форматирования кода, см. .pre-commit-config.yaml
```
Запуск менеджера задач Celery, планировщика задач Celery-beat и плагина Flower для мониторинга задач в режиме реального времени
```shell
celery -A config worker --loglevel=INFO

# ОС Windows
celery -A config worker --loglevel=INFO --pool=solo

celery -A config beat -l INFO

celery -A config flower --loglevel=INFO
```
### Как удалить контейнеры
СУБД Postgres
```shell
docker rm -f -v skillbox-db-31
```

Брокер сообщений REDIS
```shell
docker rm -f -v redis-db
```

## Проверка форматирования кода
Проверка кода выполняется из корневой папки репозитория.
* Анализатор кода flake8
```shell
flake8 market
```
* Линтер pylint
```shell
pylint --rcfile=.pylintrc market/*
```
* Линтер black
```shell
black market
```

## Как запустить web-сервер
Запуск сервера производится в активированном локальном окружение из папки `market/`
```shell
python manage.py runserver 0.0.0.0:8000
```

# Цели проекта

Код написан в учебных целях — это курс по Джанго на сайте [Skillbox](https://go.skillbox.ru/education/course/django-framework).
