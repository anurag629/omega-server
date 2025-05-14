# Docker Setup

Codercops Omega uses Docker and Docker Compose to provide a consistent development and deployment environment. This document explains the Docker configuration and how to work with containerized services.

## Overview

The application is containerized using Docker and orchestrated using Docker Compose. The main services are:

- **web**: Django web application
- **db**: PostgreSQL database
- **manim**: Manim animation engine
- **nginx**: Web server for production deployment (optional)

## Docker Files

The project includes several Docker-related files:

- `Dockerfile`: Main Dockerfile for the Django application
- `Dockerfile.flask`: Dockerfile for the Flask server (used as an API proxy)
- `Dockerfile.manim`: Dockerfile for the Manim service
- `docker-compose.yml`: Docker Compose configuration
- `install_in_container.sh`: Helper script for container setup

## Docker Compose Configuration

The `docker-compose.yml` file defines the services, networks, and volumes for the application.

### Services

#### Web Service

```yaml
web:
  build:
    context: .
    dockerfile: Dockerfile
  ports:
    - "8000:8000"
  volumes:
    - .:/app
    - ./media:/app/media
  environment:
    - PYTHONUNBUFFERED=1
  env_file:
    - .env
  depends_on:
    - db
  command: python manage.py runserver 0.0.0.0:8000
```

The web service runs the Django application, which handles authentication, API requests, and serving web pages.

#### Database Service

```yaml
db:
  image: postgres:14
  volumes:
    - postgres_data:/var/lib/postgresql/data/
  environment:
    - POSTGRES_DB=${DB_NAME}
    - POSTGRES_USER=${DB_USER}
    - POSTGRES_PASSWORD=${DB_PASSWORD}
  ports:
    - "5432:5432"
```

The database service uses PostgreSQL to store application data.

#### Manim Service

```yaml
manim:
  build:
    context: .
    dockerfile: Dockerfile.manim
  volumes:
    - ./media:/app/media
  command: tail -f /dev/null
```

The Manim service is responsible for generating mathematical animations based on scripts.

## Dockerfiles

### Dockerfile (Django)

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

### Dockerfile.manim

```dockerfile
FROM manimcommunity/manim:stable

WORKDIR /app

# Install additional dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip \
    python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Set up media directories
RUN mkdir -p /app/media/videos /app/media/images /app/media/Tex

# Keep container running
CMD ["tail", "-f", "/dev/null"]
```

## Working with Docker

### Building Containers

```bash
docker-compose build
```

This command builds or rebuilds all services defined in the `docker-compose.yml` file.

### Starting Containers

```bash
docker-compose up -d
```

This command starts all services in detached mode (running in the background).

### Stopping Containers

```bash
docker-compose down
```

This command stops and removes all containers.

### Viewing Logs

```bash
docker-compose logs -f
```

This command shows logs from all services. Add a service name to see logs for a specific service:

```bash
docker-compose logs -f web
```

### Running Commands in Containers

```bash
docker-compose exec web python manage.py migrate
```

This runs the Django migrations in the web container.

```bash
docker-compose exec web python manage.py createsuperuser
```

This creates a superuser in the web container.

## Data Persistence

The Docker Compose configuration uses volumes to persist data:

- `postgres_data`: Stores PostgreSQL database files
- `./media:/app/media`: Maps the local media directory to the container

## Development Workflow with Docker

1. Make changes to the code
2. Docker will automatically reflect code changes in the Django development server
3. For changes to static files or templates, you may need to restart the server:
   ```bash
   docker-compose restart web
   ```
4. For changes to the database models, run migrations:
   ```bash
   docker-compose exec web python manage.py makemigrations
   docker-compose exec web python manage.py migrate
   ```

## Executing Manim Scripts

To execute Manim scripts through the Docker setup:

1. The Django application sends the script to the Manim service
2. The Manim service executes the script and saves the output to the shared media volume
3. The Django application can then serve the generated media files

## Production Deployment

For production deployment, you should make the following changes:

1. Use a production-ready web server like Nginx
2. Use Gunicorn or uWSGI as the application server
3. Set appropriate environment variables
4. Secure secrets and sensitive information
5. Set up SSL/TLS for HTTPS

A sample production `docker-compose.yml` might include:

```yaml
version: '3'

services:
  web:
    build: .
    command: gunicorn core.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - ./media:/app/media
    depends_on:
      - db
    env_file:
      - .env.prod
    restart: always

  db:
    image: postgres:14
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    env_file:
      - .env.prod
    restart: always

  nginx:
    image: nginx:latest
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d
      - ./media:/app/media
      - ./nginx/certbot/conf:/etc/letsencrypt
      - ./nginx/certbot/www:/var/www/certbot
    depends_on:
      - web
    restart: always

volumes:
  postgres_data:
``` 