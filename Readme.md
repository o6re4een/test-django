# Env файл

```
DB_NAME=""
DB_USER=""
DB_PASSWORD=""
DB_HOST=""
DB_PORT="5432"
DJANGO_SECRET_KEY=""

```

#Запуск приложения

```
docker-compose up --build
```

## Накатить миграции

```
docker-compose exec web python manage.py migrate
```

## Routes

/ страница с почтами
/messages/:id - письма с почты
