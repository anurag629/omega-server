# Environment Variables

Omega Server uses environment variables for configuration, secrets, and API keys. Below is a list of required and optional variables, their purpose, and example values.

---

## 1. Django & Database

| Variable           | Purpose                        | Example Value                |
|--------------------|--------------------------------|------------------------------|
| SECRET_KEY         | Django secret key              | super-secret-key             |
| DEBUG              | Debug mode (True/False)        | True                         |
| ALLOWED_HOSTS      | Allowed hosts (comma-separated)| localhost,127.0.0.1          |
| DB_NAME            | PostgreSQL database name       | omega_db                     |
| DB_USER            | PostgreSQL user                | omega_user                   |
| DB_PASSWORD        | PostgreSQL password            | password123                  |
| DB_HOST            | PostgreSQL host                | localhost                    |
| DB_PORT            | PostgreSQL port                | 5432                         |

---

## 2. Email

| Variable             | Purpose                        | Example Value                |
|----------------------|--------------------------------|------------------------------|
| EMAIL_BACKEND        | Django email backend           | django.core.mail.backends.smtp.EmailBackend |
| EMAIL_HOST           | SMTP server host               | smtp.gmail.com               |
| EMAIL_PORT           | SMTP server port               | 587                          |
| EMAIL_USE_TLS        | Use TLS for email              | True                         |
| EMAIL_HOST_USER      | SMTP username                  | user@example.com             |
| EMAIL_HOST_PASSWORD  | SMTP password                  | yourpassword                 |
| DEFAULT_FROM_EMAIL   | Default from address           | user@example.com             |

---

## 3. AI Providers

| Variable                | Purpose                        | Example Value                |
|-------------------------|--------------------------------|------------------------------|
| GEMINI_API_KEY          | Google Gemini API key          | ...                          |
| AZURE_OPENAI_API_KEY    | Azure OpenAI API key           | ...                          |
| AZURE_OPENAI_ENDPOINT   | Azure OpenAI endpoint URL      | https://...openai.azure.com/ |
| AZURE_OPENAI_DEPLOYMENT | Azure OpenAI deployment name   | gpt-4o                       |

---

## 4. Application URLs

| Variable         | Purpose                        | Example Value                |
|------------------|--------------------------------|------------------------------|
| BASE_URL         | Backend base URL               | http://localhost:8000        |
| FRONTEND_URL     | Frontend base URL              | http://localhost:3000        |

---

## 5. Manim Execution

| Variable         | Purpose                        | Example Value                |
|------------------|--------------------------------|------------------------------|
| MANIM_SERVICE    | Hostname for Manim container   | localhost or omega-manim     |

---

## 6. Example .env File

```
SECRET_KEY=super-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=omega_db
DB_USER=omega_user
DB_PASSWORD=password123
DB_HOST=localhost
DB_PORT=5432
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=user@example.com
EMAIL_HOST_PASSWORD=yourpassword
DEFAULT_FROM_EMAIL=user@example.com
GEMINI_API_KEY=your-gemini-key
AZURE_OPENAI_API_KEY=your-azure-key
AZURE_OPENAI_ENDPOINT=https://...openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o
BASE_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
MANIM_SERVICE=localhost
```

---

For more details, see `env.example` in the project root. 