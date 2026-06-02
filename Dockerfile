# Build frontend (Vite) in a separate stage
FROM node:22-alpine as frontend-build
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
# Build with base pointing to Django static path for the SPA assets
# Assets will be referenced as /static/student_dashboard/... and index served at /student/dashboard/
RUN npm run build -- --base /static/student_dashboard/

# Python runtime image
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy frontend build into Django static and templates so Django can serve it at /student/dashboard/
RUN mkdir -p /app/templates/student_dashboard
RUN mkdir -p /app/static/student_dashboard
COPY --from=frontend-build /frontend/dist/index.html /app/templates/student_dashboard/index.html
COPY --from=frontend-build /frontend/dist /app/static/student_dashboard/

# Copy entrypoint script and make executable
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]

