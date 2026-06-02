#!/bin/sh
set -e

echo "Waiting for database..."
# simple wait loop until Postgres is reachable
tries=0
until python - <<PYTHON
import sys, os
import socket
host=os.environ.get('POSTGRES_HOST','db')
port=int(os.environ.get('POSTGRES_PORT','5432'))
try:
    s=socket.create_connection((host,port), timeout=1)
    s.close()
    sys.exit(0)
except Exception:
    sys.exit(1)
PYTHON
do
  tries=$((tries+1))
  if [ "$tries" -gt 30 ]; then
    echo "Database did not become available in time" >&2
    exit 1
  fi
  sleep 1
done

echo "Running migrations..."
python manage.py migrate --noinput

echo "Ensuring superuser (if env provided)..."
python - <<PYTHON
import os
from django.contrib.auth import get_user_model
User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
if username and email and password:
  try:
    user = User.objects.filter(username=username).first()
    if not user:
      User.objects.create_superuser(username=username, email=email, password=password)
      print('Created superuser', username)
    else:
      user.email = email
      user.set_password(password)
      user.is_staff = True
      user.is_superuser = True
      user.save()
      print('Updated superuser', username)
  except Exception as e:
    print('Failed to ensure superuser:', e)
PYTHON

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn..."
# Bind to the port provided by the environment (Render provides $PORT)
exec gunicorn statuslc.wsgi:application --bind 0.0.0.0:${PORT:-8000}
