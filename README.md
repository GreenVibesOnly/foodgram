#  Фудграм - сервис для публикации рецептов любимых блюд ❤
Фудграм - сайт, на котором пользователи могут делиться рецептами своих блюд, искать новые для себя блюда, подписываться на других пользователей, сохранять рецепты, получать готовый список покупок и вдохновляться рецептами домашней кухни.


## Возможности проекта:
Пользователи могут:
- Создавать свой профиль, наполнять его рецептами, добавлять аватар, менять пароль от аккунта.
- Просматривать профили других пользователей и подписываться на них.
- Создавать рецепты, добавлять к ним фотографию, подробное описание с ингредиентами и теги.
- Добавлять рецепты в избранное и корзину покупок.
- Сортировать рецепты по тегам.
- Скачивать список ингредиентов для рецептов, сохраненных в корзину покупок.
- Сохранять короткую ссылку на рецепт. 

Пользователи не могут:
- Изменять информацию и рецепты других пользователей.
- Самостоятельно добавлять новые теги и ингредиенты.

В проекте реализована админ-зона с полным набором функций для модерации контента.


## Технологии

- Python
- Django
- Djangorestframework
- React
- Djoser
- Gunicorn
- pytest
- Docker
- PostgreSQL

В проекте предусмотрена автоматическая упаковка частей проекта в образы с помощью Docker и размещение их 
в удаленном репозитории на DockerHub, а также автоматизация деплоя на удаленный сервер с помощью GitHub actions. На удаленном сервере установлена операционная система Ubuntu.
Перед деплоем предусмотрено автоматическое тестирование проекта.


## Запуск проекта на удалённом сервере:

Выполнить вход на удаленный сервер.

Установить Docker Compose на сервер:
```
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt-get install docker-compose-plugin
```

Создать папку kittygram:
```
sudo mkdir kittygram
```

В папке kittygram создать файл docker-compose.production.yml и скопировать туда содержимое файла docker-compose.production.yml из проекта:
```
cd kittygram
sudo nano docker-compose.production.yml
```
Таким же образом создать файлы .env и nginx.conf из скопировать в них содержимое файлов .env.example и infra/nginx.conf соответственно.

В файл настроек nginx добавить домен сайта:
```
sudo nano /etc/nginx/sites-enabled/default
```

Из дирректории kittygram выполнить команды:
```
sudo docker compose -f docker-compose.production.yml pull
sudo docker compose -f docker-compose.production.yml down
sudo docker compose -f docker-compose.production.yml up -d
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic --noinput
```
Проект будет доступен по адресу домена.


## Просмотр спецификации API:
Доступен при локальном разворачивании проекта.

Необходимо клонировать репозиторий и перейти в командной строке в папку разворачивания проекта в докере:

```
git clone <SSH Key>
```

```
cd foodgram/infra
```
Выполнить команду разворачивания проекта:

```
docker-compose up
```

Спецификация API будет доступна по адресу: [http://localhost/api/docs/](http://localhost/api/docs/)



## Автор проекта:

[Ксения Тетерчева](https://github.com/GreenVibesOnly)

Всем приятного аппетита :Р