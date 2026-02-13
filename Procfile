release: python manage.py migrate --noinput
web: gunicorn yourtubeflix.wsgi --log-file - --workers ${WEB_CONCURRENCY:-2}
