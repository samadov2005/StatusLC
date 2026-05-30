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

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn..."
exec gunicorn statuslc.wsgi:application --bind 0.0.0.0:8000
