# API Documentation

## Authentication

### Register
- **POST** `/api/auth/register/`
- Request: `{ "email": "user@example.com", "password": "..." }`
- Response: `{ "message": "Registration successful. Please verify your email." }`

### Login
- **POST** `/api/auth/login/`
- Request: `{ "email": "user@example.com", "password": "..." }`
- Response: `{ "access": "...", "refresh": "..." }`

### Verify Email
- **POST** `/api/auth/verify-email/`
- Request: `{ "token": "..." }`
- Response: `{ "message": "Email verified." }`

### Profile
- **GET** `/api/auth/profile/`
- Headers: `Authorization: Bearer <token>`
- Response: `{ "id": ..., "email": ..., ... }`

---

## Manim Scripts

### List Scripts
- **GET** `/api/agents/scripts/`
- Headers: `Authorization: Bearer <token>`
- Response: `[ { "id": ..., "prompt": ..., "status": ... }, ... ]`

### Generate Script
- **POST** `/api/agents/scripts/generate/`
- Body: `{ "prompt": "Animate a circle", "provider": "gemini", "auto_execute": true }`
- Response: `{ "success": true, "script_id": "...", ... }`

### Execute Script
- **POST** `/api/agents/scripts/{id}/execute/`
- Response: `{ "success": true, "output_path": "videos/...", ... }`

---

## Executions

### List Executions
- **GET** `/api/agents/executions/`
- Response: `[ { "id": ..., "script": ..., "status": ... }, ... ]`

### Retry Execution
- **POST** `/api/agents/executions/{id}/retry/`
- Response: `{ "success": true, ... }`

---

## Providers

### List Providers
- **GET** `/api/agents/providers/`
- Response: `[ { "id": ..., "provider_type": ... }, ... ]`

---

## Containers

### List Containers
- **GET** `/api/agents/containers/`
- Response: `[ { "id": ..., "name": ..., "is_running": ... }, ... ]`

### Start Container
- **POST** `/api/agents/containers/{id}/start/`
- Response: `{ "success": true, "is_running": true }`

### Check Status
- **POST** `/api/agents/containers/{id}/check_status/`
- Response: `{ "success": true, "is_running": true }`

---

## Media

### Serve Media
- **GET** `/media/<path>`
- Returns the requested media file (video, image, etc.)

---

## Error Handling
- All endpoints return JSON with `error` or `message` fields on failure.
- HTTP status codes follow REST conventions.

---

For more details on request/response formats, see the source code or contact the maintainers. 