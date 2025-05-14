# Authentication System

The Codercops Omega application uses a custom authentication system built with Django's authentication framework and Django REST Framework. This document describes the authentication system in detail.

## Overview

The authentication system (`auth`) provides the following features:

- Email-based authentication (no username)
- Email verification
- Admin approval for new users
- Waiting list management
- JWT-based token authentication
- Custom permissions

## Models

### CustomUser

The `CustomUser` model extends Django's `AbstractUser` model with the following key fields:

- `email`: Primary identifier for authentication (replaces username)
- `email_verified`: Boolean flag indicating if the user's email has been verified
- `is_approved`: Boolean flag indicating if the user has been approved by an admin
- `verification_token`: UUID used for email verification

### WaitingList

The `WaitingList` model manages the waiting list for users who want to join the platform:

- `email`: Email address of the person on the waiting list
- `name`: Full name
- `reason`: Reason for wanting to join
- `is_invited`: Boolean flag indicating if the person has been invited
- `invitation_sent_at`: Timestamp of when the invitation was sent

## Authentication Flow

1. A user joins the waiting list
2. Admin sends an invitation to selected users from the waiting list
3. User receives an email with a registration link
4. User registers with the invitation token
5. User receives an email verification link
6. User verifies their email address
7. Admin approves the user account
8. User can now log in and access platform features

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/waiting-list/` | POST | Join the waiting list |
| `/api/auth/register/` | POST | Register a new user with invitation |
| `/api/auth/login/` | POST | Log in and get JWT tokens |
| `/api/auth/verify-email/` | POST | Verify email address |
| `/api/auth/profile/` | GET, PUT, PATCH | View or update user profile |
| `/api/auth/token/refresh/` | POST | Refresh JWT access token |

## Custom Permissions

The authentication system provides the following custom permissions:

### IsApprovedUser

Allows access only to users whose accounts have been approved by an admin.

### IsVerifiedUser

Allows access only to users who have verified their email addresses.

### IsApprovedAndVerifiedUser

Combines the above permissions, requiring both verification and approval.

## Admin Interface

The admin interface provides the following features:

- Manage user accounts
- Approve users
- Send invitations to people on the waiting list
- View waiting list entries

## JWT Authentication

The application uses JWT (JSON Web Tokens) for authentication:

- Access tokens have a short lifespan (typically 5-15 minutes)
- Refresh tokens have a longer lifespan (typically 24 hours)
- Token refresh allows obtaining a new access token without re-authentication

## How to Use the Authentication System

### Joining the Waiting List

```json
POST /api/auth/waiting-list/
{
  "email": "user@example.com",
  "name": "John Doe",
  "reason": "I want to create mathematical animations"
}
```

### Registering a New User

```json
POST /api/auth/register/
{
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "password": "securepassword",
  "password2": "securepassword",
  "invitation_token": "INVITATION_1621478367.123456"
}
```

### Logging In

```json
POST /api/auth/login/
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

Response:
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

### Verifying Email

```json
POST /api/auth/verify-email/
{
  "token": "123e4567-e89b-12d3-a456-426614174000"
}
```

### Refreshing Access Token

```json
POST /api/auth/token/refresh/
{
  "refresh": "eyJ0eXAiO..."
}
```

Response:
```json
{
  "access": "eyJ0eXAiO..."
}
``` 