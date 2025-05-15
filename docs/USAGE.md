# Usage Guide

This guide explains how to set up, authenticate, generate Manim scripts, execute them, and retrieve outputs using Omega Server.

---

## 1. Setup

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

---

## 2. Authentication

- **Register**: `POST /api/auth/register/` with `{ "email": ..., "password": ... }`
- **Login**: `POST /api/auth/login/` with `{ "email": ..., "password": ... }`
- **Verify Email**: `POST /api/auth/verify-email/` with `{ "token": ... }`
- **Get Profile**: `GET /api/auth/profile/` with `Authorization: Bearer <token>`

---

## 3. Generating a Manim Script

- **Endpoint**: `POST /api/agents/scripts/generate/`
- **Body Example**:
  ```json
  {
    "prompt": "Animate a rotating square",
    "provider": "gemini",
    "auto_execute": true
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "script_id": "...",
    "output_path": "videos/...",
    "output_url": "http://.../media/videos/..."
  }
  ```

---

## 4. Executing a Script

- **Endpoint**: `POST /api/agents/scripts/{id}/execute/`
- **Response**:
  ```json
  {
    "success": true,
    "output_path": "videos/...",
    "execution_id": "..."
  }
  ```

---

## 5. Retrieving Media

- **Endpoint**: `GET /media/<path>`
- **Example**: `GET /media/videos/abc123/720p30/Scene1.mp4`
- Returns the video or image file for download or streaming.

---

## 6. Managing Providers and Containers

- **List Providers**: `GET /api/agents/providers/`
- **List Containers**: `GET /api/agents/containers/`
- **Start Container**: `POST /api/agents/containers/{id}/start/`
- **Check Status**: `POST /api/agents/containers/{id}/check_status/`

---

## 7. Error Handling

- All endpoints return JSON with `error` or `message` fields on failure.
- Check HTTP status codes for success or failure.

---

For more details, see the API and architecture docs. 