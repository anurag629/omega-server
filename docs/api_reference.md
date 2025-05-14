# API Reference

This document provides a comprehensive reference for all API endpoints in the Codercops Omega application.

## Authentication

All authenticated endpoints require a valid JWT token in the Authorization header:

```
Authorization: Bearer <access_token>
```

## Authentication API

### Join Waiting List

```
POST /api/auth/waiting-list/
```

Allows a user to join the waiting list for the application.

**Request Body:**
```json
{
  "email": "user@example.com",
  "name": "John Doe",
  "reason": "I want to create mathematical animations"
}
```

**Response:**
```json
{
  "email": "user@example.com",
  "name": "John Doe",
  "reason": "I want to create mathematical animations"
}
```

**Status Codes:**
- `201 Created`: Successfully joined the waiting list
- `400 Bad Request`: Invalid request data

### Register User

```
POST /api/auth/register/
```

Registers a new user with an invitation token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "password": "securepassword",
  "password2": "securepassword",
  "invitation_token": "INVITATION_1621478367.123456"
}
```

**Response:**
```json
{
  "message": "User registered successfully. Please check your email to verify your account."
}
```

**Status Codes:**
- `201 Created`: Successfully registered
- `400 Bad Request`: Invalid request data or invitation token

### Login

```
POST /api/auth/login/
```

Authenticates a user and returns JWT tokens.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "refresh": "eyJ0eXAiO...",
  "access": "eyJ0eXAiO...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "email_verified": true,
    "is_approved": true,
    "date_joined": "2023-06-01T12:00:00Z"
  }
}
```

**Status Codes:**
- `200 OK`: Successfully authenticated
- `401 Unauthorized`: Invalid credentials
- `403 Forbidden`: Email not verified or user not approved

### Verify Email

```
POST /api/auth/verify-email/
```

Verifies a user's email address using the verification token.

**Request Body:**
```json
{
  "token": "123e4567-e89b-12d3-a456-426614174000"
}
```

**Response:**
```json
{
  "message": "Email verified successfully"
}
```

**Status Codes:**
- `200 OK`: Email verified successfully
- `400 Bad Request`: Invalid verification token

### Get/Update User Profile

```
GET /api/auth/profile/
```

Retrieves the authenticated user's profile.

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "email_verified": true,
  "is_approved": true,
  "date_joined": "2023-06-01T12:00:00Z"
}
```

```
PUT/PATCH /api/auth/profile/
```

Updates the authenticated user's profile.

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Smith"
}
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Smith",
  "email_verified": true,
  "is_approved": true,
  "date_joined": "2023-06-01T12:00:00Z"
}
```

**Status Codes:**
- `200 OK`: Successfully retrieved or updated
- `401 Unauthorized`: Not authenticated

### Refresh Token

```
POST /api/auth/token/refresh/
```

Obtains a new access token using a refresh token.

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiO..."
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiO..."
}
```

**Status Codes:**
- `200 OK`: Successfully refreshed
- `401 Unauthorized`: Invalid refresh token

## Omega API

### List Manim Scripts

```
GET /api/scripts/
```

Lists all Manim scripts created by the authenticated user.

**Response:**
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "prompt": "Create an animation showing the Pythagorean theorem",
    "script": "from manim import *\n...",
    "provider": "gemini",
    "status": "completed",
    "output_url": "http://localhost:8000/media/videos/manim_script_123e4567/720p30/PythagoreanTheorem.mp4",
    "created_at": "2023-06-01T12:00:00Z",
    "updated_at": "2023-06-01T12:05:00Z"
  },
  {
    "id": "223e4567-e89b-12d3-a456-426614174001",
    "prompt": "Create an animation showing a sine wave",
    "script": "from manim import *\n...",
    "provider": "azure_openai",
    "status": "completed",
    "output_url": "http://localhost:8000/media/videos/manim_script_223e4567/720p30/SineWave.mp4",
    "created_at": "2023-06-02T12:00:00Z",
    "updated_at": "2023-06-02T12:05:00Z"
  }
]
```

**Status Codes:**
- `200 OK`: Successfully retrieved
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: Not authorized

### Get Manim Script Details

```
GET /api/scripts/{id}/
```

Retrieves details of a specific Manim script.

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "prompt": "Create an animation showing the Pythagorean theorem",
  "script": "from manim import *\n...",
  "provider": "gemini",
  "script_path": "path/to/script.py",
  "output_path": "videos/manim_script_123e4567/720p30/PythagoreanTheorem.mp4",
  "output_url": "http://localhost:8000/media/videos/manim_script_123e4567/720p30/PythagoreanTheorem.mp4",
  "status": "completed",
  "error_message": null,
  "created_at": "2023-06-01T12:00:00Z",
  "updated_at": "2023-06-01T12:05:00Z"
}
```

**Status Codes:**
- `200 OK`: Successfully retrieved
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: Not authorized
- `404 Not Found`: Script not found

### Generate Manim Script

```
POST /api/generate/
```

Generates a new Manim script from a prompt.

**Request Body:**
```json
{
  "prompt": "Create an animation showing the Pythagorean theorem",
  "provider": "gemini",
  "execute": true
}
```

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "script": "from manim import *\n\nclass PythagoreanTheorem(Scene):\n    def construct(self):\n        # Create a right triangle\n        triangle = Polygon(\n            ORIGIN, 3*RIGHT, 3*RIGHT+4*UP,\n            color=WHITE\n        )\n        ...",
  "script_path": "path/to/script.py",
  "output_path": "videos/manim_script_123e4567/720p30/PythagoreanTheorem.mp4",
  "output_url": "http://localhost:8000/media/videos/manim_script_123e4567/720p30/PythagoreanTheorem.mp4"
}
```

**Status Codes:**
- `200 OK`: Successfully generated
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: Not authorized
- `500 Internal Server Error`: Error during generation or execution

## Media Access

### Serve Media File

```
GET /media/{path}
```

Serves a media file (image or video).

**Status Codes:**
- `200 OK`: Successfully served
- `404 Not Found`: File not found 