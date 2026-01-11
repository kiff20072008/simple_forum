#!/bin/sh

if [ "$SQL_DATABASE" = "forum_db" ]
then
    echo "Waiting for postgres..."
    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done
    echo "PostgreSQL started"
fi

echo "Making migrations..."
python manage.py makemigrations users
python manage.py makemigrations forum
python manage.py makemigrations

echo "Migrating..."
python manage.py migrate
python manage.py shell -c "from django.contrib.auth.models import Group; Group.objects.get_or_create(name='Moderators')"
python manage.py collectstatic --no-input --clear

exec gunicorn project.wsgi:application --bind 0.0.0.0:8000 --workers 10 --timeout 120