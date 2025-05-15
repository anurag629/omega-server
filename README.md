# Omega Server

Omega Server is a Django-based backend for AI-powered Manim script generation and execution. It provides a secure, extensible API for generating, executing, and managing Manim animation scripts using advanced AI models (Google Gemini, Azure OpenAI) and Dockerized execution environments.

## Features

- **AI-Powered Script Generation**: Generate Manim scripts from natural language prompts using Gemini or Azure OpenAI.
- **Secure Script Execution**: Run scripts in isolated Docker containers, with automatic dependency management and AI-based debugging.
- **User Authentication**: JWT-based authentication, email verification, and custom user management.
- **RESTful API**: Endpoints for scripts, executions, providers, containers, and user management.
- **Media Management**: Stores and serves generated videos, images, and scripts.
- **Extensible Agent System**: Modular agents for AI, execution, Docker, and dependency management.

## Project Structure

- `core/` - Django project settings and root URLs
- `omega/` - Main app for Manim script management
- `omega_auth/` - Custom authentication and user management
- `agents/` - AI, execution, Docker, and dependency agents
- `media/` - Stores generated videos, images, and scripts
- `requirements.txt` - Python dependencies
- `Dockerfile`, `docker-compose.yml` - Containerization support

## Quick Start

### Prerequisites
- Python 3.10+
- Docker (for script execution)
- PostgreSQL database

### Setup
1. **Clone the repository**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure environment variables**:
   - Copy `env.example` to `.env` and fill in required values (DB, AI keys, etc.)
4. **Apply migrations**:
   ```bash
   python manage.py migrate
   ```
5. **Create a superuser**:
   ```bash
   python manage.py createsuperuser
   ```
6. **Run the server**:
   ```bash
   python manage.py runserver
   ```
7. **(Optional) Start Docker Manim container**:
   ```bash
   docker-compose up -d
   ```

## API Overview

- **Authentication**: `/api/auth/`
- **Manim Scripts**: `/api/agents/scripts/` and `/api/generate-manim/`
- **Executions**: `/api/agents/executions/`
- **Providers**: `/api/agents/providers/`
- **Containers**: `/api/agents/containers/`

See [docs/API.md](docs/API.md) for detailed endpoint documentation.

## Architecture

- **Agents**: Modular classes for AI, execution, Docker, and dependency management.
- **Models**: Track scripts, executions, providers, containers, and users.
- **Security**: JWT authentication, CORS, Docker isolation, and environment-based secrets.
- **Media**: All outputs are stored in `/media` and served via API.

## Extending
- Add new AI providers by extending `AIScriptGenerationAgent`.
- Add new endpoints or business logic via DRF viewsets and serializers.

## License
MIT

---

For more details, see the `docs/` directory. 