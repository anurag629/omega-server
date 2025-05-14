# Getting Started

This guide will help you set up the Codercops Omega project on your local machine for development and testing purposes.

## Prerequisites

- Docker and Docker Compose (latest version recommended)
- Python 3.10 or higher (if running outside Docker)
- Git
- API keys for:
  - Google Gemini API
  - Azure OpenAI API

## Installation

### Using Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd codercops-omega
   ```

2. Create environment file:
   ```bash
   cp env.example .env
   ```

3. Edit the `.env` file with your configuration (see [Configuration](#configuration) section)

4. Build and start the Docker containers:
   ```bash
   docker-compose up -d --build
   ```

5. Create a superuser:
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

6. Access the application:
   - Web app: http://localhost:8000
   - Admin panel: http://localhost:8000/admin

### Manual Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd codercops-omega
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create environment file:
   ```bash
   cp env.example .env
   ```

5. Edit the `.env` file with your configuration

6. Apply migrations:
   ```bash
   python manage.py migrate
   ```

7. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

8. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Configuration

The `.env` file contains all the necessary configuration options. Here's what you need to configure:

### Django Settings
```
SECRET_KEY=your_django_secret_key_here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Database Configuration
```
DB_NAME=omega_db
DB_USER=omega_user
DB_PASSWORD=omega_password
DB_HOST=db
DB_PORT=5432
```

### API Keys
```
GEMINI_API_KEY=your_gemini_api_key_here
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=deployment_name_here
```

### Application Settings
```
BASE_URL=http://localhost:8000
```

### Email Configuration
```
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=codercops@codercops.com
EMAIL_HOST_PASSWORD=email_password
DEFAULT_FROM_EMAIL=codercops@codercops.com
```

For production, set `DEBUG=False` and update `ALLOWED_HOSTS` and email configuration accordingly. 