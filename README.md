# Omega Server

Omega Server is a Django-based backend for AI-powered Manim script generation and execution. It provides a secure, extensible API for generating, executing, and managing Manim animation scripts using advanced AI models (Google Gemini, Azure OpenAI) and Dockerized execution environments.

# Frontend is at: https://github.com/anurag629/omega-client

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

## Visualizations

The project includes various mathematical and educational animations generated using Manim. These visualizations are stored in `docs/media/videos/` and include:

### Linear Regression Demonstration  
[![Circle Area Diameter Relation](http://img.youtube.com/vi/92PgdUDL7Lw/0.jpg)](https://youtu.be/92PgdUDL7Lw)  
*A visual explanation of linear regression concepts*  
- Shows data points, best fit line, and error calculations  
- Demonstrates gradient descent optimization  

### Mathematical Concepts  
[![Circle Area Diameter](http://img.youtube.com/vi/2rw7FwE-ppE/0.jpg)](https://youtu.be/2rw7FwE-ppE)  
*Visualization of complex mathematical operations*  
- Step-by-step animation of problem-solving techniques  
- Interactive mathematical proofs  

### Educational Sequences  
[![Circle To Point](http://img.youtube.com/vi/Z_uXTv-gRTM/0.jpg)](https://youtu.be/Z_uXTv-gRTM)  
*Clear, step-by-step explanations of concepts*  
- Visual aids for better understanding  
- Interactive learning elements  


Each visualization is generated through our AI-powered script generation system and executed in a secure Docker environment. The outputs are high-quality MP4 files at 720p resolution.

## License
MIT

---

For more details, see the `docs/` directory. 
