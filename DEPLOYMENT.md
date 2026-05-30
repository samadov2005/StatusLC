# StatusLC Deployment Guide

Complete instructions for deploying StatusLC to production.

## Table of Contents
1. [Pre-deployment Checklist](#pre-deployment-checklist)
2. [Environment Setup](#environment-setup)
3. [Database Setup](#database-setup)
4. [Web Server Configuration](#web-server-configuration)
5. [Security Hardening](#security-hardening)
6. [Monitoring & Maintenance](#monitoring--maintenance)

## Pre-deployment Checklist

### Security
- [ ] Generate a secure `DJANGO_SECRET_KEY`
- [ ] Set `DEBUG=False` in production
- [ ] Configure `ALLOWED_HOSTS` with your domain
- [ ] Set up HTTPS/SSL certificates
- [ ] Configure secure database credentials (not in code)
- [ ] Enable all security middleware

### Database
- [ ] Use PostgreSQL (or MySQL) instead of SQLite
- [ ] Create database backups
- [ ] Run migrations
- [ ] Create superuser account
- [ ] Test database connectivity

### Static Files
- [ ] Configure static file serving
- [ ] Collect static files
- [ ] Set up CDN if needed

### Monitoring
- [ ] Set up error tracking (Sentry)
- [ ] Configure logging
- [ ] Set up uptime monitoring
- [ ] Configure email alerts

## Environment Setup

### 1. Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.9 python3.9-venv python3-pip nginx
sudo apt install -y postgresql postgresql-contrib
```

### 2. Create Application User

```bash
# Create dedicated user for app
sudo useradd -m -s /bin/bash statuslc
sudo su - statuslc

# Create project directory
mkdir -p ~/statuslc
cd ~/statuslc

# Clone repository (or upload code)
git clone <your-repo> .
```

### 3. Python Environment

```bash
# Create virtual environment
python3.9 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

### 4. Environment Configuration

```bash
# Create .env file
nano .env
```

Production `.env` example:
```
DEBUG=False
DJANGO_SECRET_KEY=your-generated-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database (PostgreSQL)
DATABASE_URL=postgresql://statuslc:password123@localhost:5432/statuslc

# Email configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Telegram
TELEGRAM_BOT_TOKEN=your-bot-token-here

# CORS
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Security
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
```

## Database Setup

### PostgreSQL Configuration

```bash
# Connect as postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE statuslc;
CREATE USER statuslc WITH PASSWORD 'your-secure-password';
ALTER ROLE statuslc SET client_encoding TO 'utf8';
ALTER ROLE statuslc SET default_transaction_isolation TO 'read committed';
ALTER ROLE statuslc SET default_transaction_deferrable TO on;
ALTER ROLE statuslc SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE statuslc TO statuslc;
\q
```

### Run Django Migrations

```bash
source venv/bin/activate
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

## Web Server Configuration

### Gunicorn Service

Create `/etc/systemd/system/statuslc.service`:

```ini
[Unit]
Description=StatusLC gunicorn service
After=network.target

[Service]
User=statuslc
Group=www-data
WorkingDirectory=/home/statuslc/statuslc
ExecStart=/home/statuslc/statuslc/venv/bin/gunicorn \
    --workers 4 \
    --worker-class sync \
    --bind unix:/run/statuslc.sock \
    --timeout 60 \
    statuslc.wsgi:application

[Install]
WantedBy=multi-user.target
```

Enable and start service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable statuslc
sudo systemctl start statuslc
sudo systemctl status statuslc
```

### Nginx Configuration

Create `/etc/nginx/sites-available/statuslc`:

```nginx
upstream statuslc_app {
    server unix:/run/statuslc.sock fail_timeout=0;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    client_max_body_size 20M;
    
    # Static files
    location /static/ {
        alias /home/statuslc/statuslc/staticfiles/;
        expires 30d;
    }
    
    # Media files
    location /media/ {
        alias /home/statuslc/statuslc/media/;
        expires 7d;
    }
    
    # Django application
    location / {
        proxy_pass http://statuslc_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/statuslc /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### SSL Certificate (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot certonly --nginx -d yourdomain.com -d www.yourdomain.com
```

## Security Hardening

### 1. Django Settings

Ensure these are set in production:
```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_SECURITY_POLICY = {
    "default-src": ("'self'",),
}
```

### 2. System Security

```bash
# Enable firewall
sudo ufw enable
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Fail2ban for brute force protection
sudo apt install fail2ban
sudo systemctl enable fail2ban
```

### 3. Database Backups

Create `/home/statuslc/backup.sh`:
```bash
#!/bin/bash
BACKUP_DIR="/backups/statuslc"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

mkdir -p $BACKUP_DIR
pg_dump -U statuslc statuslc | gzip > $BACKUP_DIR/statuslc_$TIMESTAMP.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -mtime +30 -delete
```

Schedule with cron:
```bash
crontab -e
# Add: 0 2 * * * /home/statuslc/backup.sh
```

## Monitoring & Maintenance

### 1. Error Tracking with Sentry

```bash
pip install sentry-sdk
```

Add to settings.py:
```python
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="https://your-sentry-dsn@sentry.io/project-id",
    integrations=[DjangoIntegration()],
    traces_sample_rate=0.1,
    environment="production"
)
```

### 2. Logging

Logs are written to console (captured by systemd). View with:
```bash
sudo journalctl -u statuslc -f
```

### 3. Regular Maintenance

```bash
# Check for security updates
sudo apt list --upgradable

# Django security check
python manage.py check --deploy

# Database maintenance
python manage.py dbshell
VACUUM ANALYZE;

# Clear old sessions
python manage.py clearsessions
```

### 4. Monitoring Dashboard

Use tools like:
- **Prometheus + Grafana** for metrics
- **ELK Stack** for logging
- **Uptime Kuma** for uptime monitoring

## Troubleshooting

### Service Won't Start
```bash
sudo systemctl status statuslc
sudo journalctl -u statuslc -n 50
```

### Static Files Not Loading
```bash
python manage.py collectstatic --clear --noinput
```

### Database Connection Issues
```bash
# Test database
python manage.py dbshell

# Check migrations
python manage.py showmigrations
```

### High Memory Usage
```bash
# Limit Gunicorn workers
# Edit /etc/systemd/system/statuslc.service
# Adjust --workers parameter (recommended: 2-4 per CPU core)
```

## Performance Optimization

1. **Database Indexing**: Already configured in models
2. **Query Optimization**: Use select_related() and prefetch_related()
3. **Caching**: Add Redis for caching
4. **CDN**: Serve static files through CloudFlare or similar
5. **Compression**: Gzip is enabled in Nginx

## Support

For issues or questions:
1. Check logs: `sudo journalctl -u statuslc -n 100`
2. Test with `python manage.py check --deploy`
3. Review this guide's troubleshooting section
