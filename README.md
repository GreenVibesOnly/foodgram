Находясь в папке infra, выполните команду docker-compose up. При выполнении этой команды контейнер frontend, описанный в docker-compose.yml, подготовит файлы, необходимые для работы фронтенд-приложения, а затем прекратит свою работу.

По адресу http://localhost изучите фронтенд веб-приложения, а по адресу http://localhost/api/docs/ — спецификацию API.

Копирование статики после запуска контейнера:
docker compose exec backend python manage.py collectstatic
docker exec -it <код или имя back контейнера> sh
cp -r /app/collected_static/. /backend_static/static/