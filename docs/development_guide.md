# Development Guide

This guide provides information for developers who want to contribute to or extend the Codercops Omega project.

## Development Environment Setup

### Prerequisites

- Python 3.10 or higher
- Docker and Docker Compose
- Git
- Code editor (VSCode recommended)
- Postgres (if not using Docker)

### Setting Up the Development Environment

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

Alternatively, use Docker Compose:
```bash
docker-compose up -d
```

## Project Structure

```
codercops-omega/
├── auth/                  # Authentication application
│   ├── admin.py               # Admin configurations
│   ├── apps.py                # App configuration
│   ├── models.py              # User models
│   ├── permissions.py         # Custom permissions
│   ├── serializers.py         # API serializers
│   ├── urls.py                # URL routing
│   └── views.py               # API views
├── core/                      # Project core
│   ├── settings.py            # Django settings
│   ├── urls.py                # Main URL routing
│   └── wsgi.py                # WSGI configuration
├── docs/                      # Documentation
├── media/                     # Media files (images, videos)
│   ├── images/                # Generated images
│   └── videos/                # Generated videos
├── omega/                     # Omega application
│   ├── models.py              # Manim script models
│   ├── scripts/               # Helper scripts
│   ├── serializers.py         # API serializers
│   ├── services.py            # Business logic
│   ├── templates/             # HTML templates
│   └── views.py               # API and web views
├── static/                    # Static files
├── .env                       # Environment variables
├── .gitignore                 # Git ignore file
├── docker-compose.yml         # Docker Compose configuration
├── Dockerfile                 # Django Dockerfile
├── Dockerfile.flask           # Flask API Dockerfile
├── Dockerfile.manim           # Manim Dockerfile
├── docker-compose.manim.yml   # Manim service Docker Compose
├── executor.py                # Manim execution service
├── restart_manim_container.sh # Shell script to restart Manim service
├── restart_manim_container.bat # Windows batch file to restart Manim service
└── requirements.txt           # Python dependencies
```

## Core Concepts

### Authentication Flow

1. User joins waiting list
2. Admin sends invitation
3. User registers with invitation token
4. User verifies email
5. Admin approves user
6. User can log in and use the platform

### Manim Script Generation and Execution

1. User submits a prompt and selects AI provider
2. Backend sends prompt to selected AI provider
3. AI generates a Manim script
4. If execution is requested, the script is sent to the Manim service
5. Manim executes the script and generates animation
6. If errors occur during execution, the system will automatically:
   a. Analyze the error using AI
   b. Generate a fixed version of the script
   c. Retry execution
   d. Install any missing dependencies if needed
7. Output files are saved to the media directory
8. User can view and download the generated animation

## Adding New Features

### Adding a New API Endpoint

1. Define a new serializer in the appropriate serializers.py file
2. Create a new view in the views.py file
3. Add the URL route in the urls.py file
4. Test the new endpoint

Example:
```python
# serializers.py
class NewFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = YourModel
        fields = ['field1', 'field2']

# views.py
class NewFeatureViewSet(viewsets.ModelViewSet):
    queryset = YourModel.objects.all()
    serializer_class = NewFeatureSerializer
    permission_classes = [IsAuthenticated]

# urls.py
router.register(r'new-feature', views.NewFeatureViewSet)
```

### Adding a New AI Provider

1. Update the ManimScript model to include the new provider
2. Implement the provider integration in the services.py file
3. Update the serializer to validate the new provider
4. Test the integration

Example:
```python
# models.py
provider = models.CharField(
    max_length=20, 
    choices=[
        ('gemini', 'Google Gemini'), 
        ('azure_openai', 'Azure OpenAI'),
        ('new_provider', 'New Provider')
    ],
    help_text="AI provider used for generation"
)

# services.py
def generate_manim_script(prompt, provider):
    if provider == 'gemini':
        # Existing code for Gemini
    elif provider == 'azure_openai':
        # Existing code for Azure OpenAI
    elif provider == 'new_provider':
        # New provider implementation
        return generate_with_new_provider(prompt)
    else:
        raise ValueError(f"Unsupported provider: {provider}")
```

### Manim Script Debugging System

The system includes an automatic error handling and debugging mechanism for Manim scripts:

1. **AI-based Script Fixing**:
   The `debug_manim_script` function in `services.py` uses AI to automatically fix errors in scripts:

   ```python
   fixed_script = debug_manim_script(script, error_message)
   ```

2. **Automatic Dependency Installation**:
   The `install_missing_dependencies` function detects missing packages from error messages and installs them:

   ```python
   # Example usage in execute_manim_script
   if install_missing_dependencies(error_msg):
       logger.info("Installed missing dependencies, retrying execution")
       continue
   ```

3. **Multiple Execution Attempts**:
   The system will automatically retry script execution after fixing errors, up to a configurable limit:

   ```python
   # Example configuration in execute_manim_script
   max_debug_attempts = 3
   ```

4. **Improved Error Reporting**:
   Enhanced error capture and formatting from the Manim container for better debugging:

   ```python
   # Extract detailed error information in the Flask app
   if "TypeError: " in complete_output:
       # Extract TypeError and related lines
       error_lines = []
       for line in complete_output.split("\n"):
           if "TypeError: " in line or "❱" in line:
               error_lines.append(line)
   ```

## Testing

### Running Tests

```bash
python manage.py test
```

Or with Docker:
```bash
docker-compose exec web python manage.py test
```

### Writing Tests

#### Testing API Endpoints

```python
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import YourModel

class YourAPITestCase(APITestCase):
    def setUp(self):
        # Setup code
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpassword',
            is_approved=True,
            email_verified=True
        )
        self.client.force_authenticate(user=self.user)
        
    def test_your_api_endpoint(self):
        url = reverse('your-api-endpoint')
        data = {'field1': 'value1', 'field2': 'value2'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(YourModel.objects.count(), 1)
        self.assertEqual(YourModel.objects.get().field1, 'value1')
```

#### Testing Models

```python
from django.test import TestCase
from .models import YourModel

class YourModelTestCase(TestCase):
    def setUp(self):
        # Setup code
        YourModel.objects.create(field1='value1', field2='value2')
        
    def test_your_model_method(self):
        model = YourModel.objects.get(field1='value1')
        self.assertEqual(model.your_method(), expected_result)
```

## Code Style and Guidelines

- Follow PEP 8 for Python code style
- Use Django's coding style for Django-specific code
- Write meaningful docstrings
- Keep functions small and focused
- Use type hints where appropriate
- Write tests for new features
- Follow REST API best practices

## Common Development Tasks

### Creating Migrations

```bash
python manage.py makemigrations
```

### Applying Migrations

```bash
python manage.py migrate
```

### Creating a Superuser

```bash
python manage.py createsuperuser
```

### Collecting Static Files

```bash
python manage.py collectstatic
```

### Opening a Django Shell

```bash
python manage.py shell
```

### Running a Specific Test

```bash
python manage.py test app_name.tests.test_module.TestClass.test_method
```

### Managing the Manim Container

#### Starting or Restarting the Manim Container

On Linux/Mac:
```bash
./restart_manim_container.sh
```

On Windows:
```cmd
restart_manim_container.bat
```

#### Checking Manim Container Logs

```bash
docker logs omega-manim
```

#### Installing Additional Dependencies in the Manim Container

```bash
docker exec omega-manim pip install <package-name>
```

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
   - Check your database configuration in .env
   - Ensure PostgreSQL service is running

2. **Docker-related Issues**
   - Check Docker logs: `docker-compose logs <service_name>`
   - Rebuild containers: `docker-compose build`
   - Reset containers: `docker-compose down && docker-compose up -d`

3. **Media File Issues**
   - Check file permissions in the media directory
   - Ensure media paths are correctly configured in settings.py

4. **API Authentication Issues**
   - Check token expiration
   - Verify that the user is approved and email verified

5. **Manim Script Execution Issues**
   - Check `MANIM_SERVICE` and `MANIM_SERVICE_PORT` in settings.py (should point to the container name 'omega-manim')
   - Ensure the Manim container is running: `docker ps | grep omega-manim`
   - Check Manim service logs: `docker logs omega-manim`
   - Restart the Manim container using restart_manim_container script
   - If scripts consistently fail, check the error patterns and update debug_manim_script to handle them

## Contributing

1. Create a new branch for your feature or bugfix
2. Make changes and write tests
3. Ensure all tests pass
4. Create a pull request with a detailed description
5. Code review and merge 