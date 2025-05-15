# Architecture Overview

Omega Server is designed as a modular, secure, and extensible backend for AI-powered Manim script generation and execution. Below is an overview of its architecture and main components.

---

## 1. High-Level Diagram

```
[User / Frontend]
      |
      v
[REST API (Django/DRF)]
      |
      v
[Agents Layer]
  |    |    |
  v    v    v
[AI] [Execution] [Docker]
      |
      v
[Media Storage (videos, images, scripts)]
```

---

## 2. Main Components

### a. Django Apps
- **core/**: Project settings, URLs, and configuration.
- **omega/**: Manim script management, API endpoints, and media serving.
- **omega_auth/**: Custom user model, registration, JWT authentication, email verification.
- **agents/**: Modular agents for AI, script execution, Docker, and dependency management.

### b. Agents System
- **AIScriptGenerationAgent**: Handles prompt-to-Manim-script using Gemini or Azure OpenAI.
- **ManimExecutionAgent**: Runs scripts in Docker, manages retries, error handling, and AI-based debugging.
- **DockerAgent**: Manages Docker containers for safe, isolated execution.
- **DependencyAgent**: Installs missing Python dependencies as needed.
- **AIScriptDebuggingAgent**: Uses AI to fix scripts that fail to execute.

### c. Models
- **ManimScript**: Tracks prompt, script, provider, output, status, errors, and user.
- **Execution**: Tracks each script execution attempt, status, and output.
- **AIProvider**: Stores configuration for AI providers (Gemini, Azure OpenAI, etc.).
- **Container**: Tracks Docker containers used for execution.
- **CustomUser**: Extends Django's user model for authentication and profile management.

### d. Media & Static
- **media/**: Stores all generated videos, images, and scripts.
- **static/**: Static files served via WhiteNoise.

---

## 3. Workflow

1. **User submits a prompt** via API.
2. **AIScriptGenerationAgent** generates a Manim script using the selected AI provider.
3. **Script is saved** to the database.
4. **If execution is requested**:
   - **ManimExecutionAgent** runs the script in Docker.
   - Handles errors, retries, and can use AI to auto-debug/fix scripts.
   - Output video is saved and linked to the script.
5. **API returns** script and (if executed) output video URL.

---

## 4. Security
- **JWT Authentication** for all API endpoints.
- **CORS**: Open in dev, configurable for production.
- **Docker Isolation**: All script execution is sandboxed.
- **Environment Variables**: All secrets and API keys are loaded from environment.

---

## 5. Extensibility
- Add new AI providers by extending the agent system.
- Add new endpoints or business logic via DRF viewsets and serializers.
- Modular agent design allows for easy addition of new execution or debugging strategies.

---

## 6. Deployment
- **Docker**: Used for both the backend and Manim execution containers.
- **Gunicorn**: For production WSGI serving.
- **WhiteNoise**: For static file serving.

---

For more details, see the source code and other docs in this directory. 