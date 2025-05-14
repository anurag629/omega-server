# Project Overview

Codercops Omega is a web application built with Django that enables users to generate and execute Manim animations using AI. The platform leverages AI providers like Google Gemini and Azure OpenAI to generate mathematical animation scripts and render them using the Manim library.

## Core Features

- **AI-Powered Animation Generation**: Generate Manim animation scripts from natural language prompts
- **Multiple AI Providers**: Support for Google Gemini and Azure OpenAI
- **Animation Execution**: Execute generated scripts to create mathematical animations
- **User Authentication**: Complete authentication system with email verification
- **User Approval Workflow**: Admin approval for new users
- **Waiting List Management**: System to manage user invitations and waiting list

## Tech Stack

- **Backend**: Django (Python) with Django REST Framework
- **Authentication**: JWT (JSON Web Tokens) using Simple JWT
- **Database**: PostgreSQL
- **AI Integration**: Google Gemini and Azure OpenAI APIs
- **Containerization**: Docker and Docker Compose
- **Animation Engine**: Manim (Mathematical Animation Engine)

## System Architecture

The application consists of two main components:

1. **Authentication App (`auth`)**: Handles user registration, authentication, email verification, and admin approval
2. **Omega App (`omega`)**: Core application that handles the generation and execution of Manim scripts

Both components are containerized using Docker for easy deployment and development. 