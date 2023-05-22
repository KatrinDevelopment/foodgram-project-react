# praktikum_new_diplom

![Status](https://github.com/KatrinDevelopment/foodgram-project-react/actions/workflows/yamdb_workflow.yml/badge.svg)

Foodgram: [http://foodka.servepics.com/](http://foodka.servepics.com/)
Email админки: admin@gmail.com
Пароль админки: 1234

## Описание проекта

Foodgram — это идеальное место для всех любителей еды, которые хотят делиться
своими рецептами, находить новые блюда и общаться с единомышленниками!

Сайт продуктовый помощник позволяет настроить персонализированную ленту
контента, формировать список покупок и искать подходящие рецепты. Разработчики
могут использовать API Foodgram для создания собственных клиентских приложений
или интеграций.

Важно отметить, что Foodgram стремится предоставить простой и интуитивно
понятный интерфейс, чтобы пользователи могли легко найти нужную информацию,
подписываться на рецепты и использовать функциональность сервиса без затруднений.

Проект разрабатывается с использованием современных веб-технологий и лучших
практик разработки. Документация API и инструкции по развертыванию будут
предоставлены разработчикам, чтобы облегчить интеграцию с платформой.

Мы надеемся, что наш сервис станет вашим незаменимым продуктовым помощником!

## Ресурсы API

Ознакомьтесь с нашей документацией, чтобы узнать, что доступно в API и как его
использовать в репозитории `docs/redoc.yaml` или по адресу:
[redoc](http://foodka.servepics.com/redoc/)

## Как запустить проект

Для запуска приложения необходимо создать файл .env в корневой папке проекта
и заполнить его переменными:

```bash
cp .env.example .env
```

Собрать образы Docker:

```docker
sudo docker build -t yamdb .
```

Запустить контейнеры:

```docker
sudo docker-compose up
```

Выполнить миграции:

```docker
sudo docker-compose exec web python manage.py migrate
```

Создать суперпользователя (для раздачи прав админам):

```docker
sudo docker-compose exec web python manage.py createsuperuser
```

Выполнить команду для заполнения базы ингредиентами(обязательны для создания
рецепта):

```docker
docker-compose exec web python manage.py load_csv
```

Заполнить через админку базу данных тегами(обязательны для создания рецепта)

Собрать статику:

```docker
sudo docker-compose exec web python manage.py collectstatic --no-input
```

## Проект создан

[Katrin Sakharova](https://github.com/KatrinDevelopment/)

Мы знаем, что разработка программного обеспечения может быть довольно сложной
задачей, поэтому мы здесь, чтобы помочь! Если вы столкнулись с проблемами,
которые не удается решить самостоятельно, не беспокойтесь - наша команда готова
прийти на помощь. Кроме того, если вы знаете, как исправить ошибку в нашем
коде, мы всегда рады новым контрибьюторам и открыты для вашей помощи.
Вместе мы можем создать лучший продукт для всех!
