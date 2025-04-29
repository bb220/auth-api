<p align="center">
  <img src="assets/launcher-center-logo.png" alt="Launcher User Service Logo" width="180" />
</p>

# Launcher User Service

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.12%2B-blue?style=for-the-badge&logo=python)
![SendGrid](https://img.shields.io/badge/SendGrid-00b2ff?style=for-the-badge&logo=sendgrid)
![Deployed on Railway](https://img.shields.io/badge/Railway-App-6c4cff?style=for-the-badge&logo=railway)
![License: MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

A lean, secure, and easily extendable user service for technical founders who want to move fast and build products — exposing a simple, powerful API.

Built with FastAPI and SQLAlchemy, this service provides essential user management functionality out of the box and is ready to deploy. Designed for rapid development and easy extension, it helps technical founders go from idea to launch with minimal backend overhead.

Lean enough for your MVP. Strong enough to scale with you.

## Key Features

- 🔐 Secure user registration, login, and token-based authentication
- 📨 Built-in email verification and password reset flows
- ⚡ Asynchronous background tasks for fast user experiences
- 🛡️ JWT security and protected route examples
- 📊 Event tracking for analytics and user behavior insights
- 🛠️ Easily extendable with additional services (OAuth, profile management, roles)

---

## Technologies Used

- **FastAPI** — lightning-fast Python web framework
- **SQLAlchemy** — ORM for database interactions
- **SQLite** — Local development database
- **PostgreSQL** — Production database
- **SendGrid** — Email platform
- **Railway** — Deployment platform

---

## Local Setup and Installation

### 1. Clone the repository

```bash
git clone https://github.com/bb220/auth-api.git
cd auth-api
```

### 2. Set up a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements-dev.txt
```

### 4. Set environment variables (create a .env file):

```env
# Secret Key for JWT signing
SECRET_KEY=your_super_secret_key_here

# Access Token Expiry Time (minutes)
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Refresh Token Expiry Time (minutes)
REFRESH_TOKEN_EXPIRE_MINUTES=10080  # 7 days

# Database URL (SQLite local example)
DATABASE_URL=sqlite:///./auth_api.db

# SendGrid API Key for sending emails
SENDGRID_API_KEY=your_sendgrid_api_key_here

# Verified sender email (must match your SendGrid authenticated domain)
FROM_EMAIL_ADDRESS=your_verified_sender@example.com
```

✅ In deployed environments, all env variables are managed securely with Railway.

### 5. Run the app:

```bash
uvicorn app.main:app --reload
```

- API documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- OpenAPI schema: [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json)

---

## 🚀 Deploy with [Railway](https://railway.app/)
Launch hosted environments in minutes through Railway's console.

1. Create a project with the GitHub integration.
2. Set the app's `Custom Start Command`
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```
3. Create a Postgres DB
4. Set the app's environment variables

---

## 📬 Enable Email Features

1. Create a SendGrid account (free tier works)
2. Verify your sender email address or domain
3. Create an API Key and include in your environment variables

---

## 📦 Endpoints Overview

### User Authentication

| Method | Route | Purpose |
|:---|:---|:---|
| POST | `/register` | Register a new user |
| GET | `/verify-email` | Verify email using a token |
| POST | `/login` | Login and get access + refresh tokens |
| POST | `/refresh` | Refresh access token |
| POST | `/resend-verification-email` | Request resend of verification email |
| GET | `/protected` | Example secured endpoint |

### Password Management

| Method | Endpoint | Description |
|:---|:---|:---|
| `POST` | `/request-password-reset` | Request password reset email |
| `POST` | `/reset-password` | Reset password using token from email |

---

## 📈 Event Tracking

This API includes built-in **event tracking** for critical user actions.  
Events are recorded into the `events` database table for monitoring, reporting, and analysis.

### Tracked Events

| Event Name | Trigger |
|:-----------|:--------|
| `user_registered` | After successful user registration |
| `user_login_success` | After successful user login |
| `user_login_failure` | After failed user login attempt |
| `password_reset_requested` | When a password reset is requested |
| `password_reset_completed` | After a successful password reset |
| `email_verified` | After user successfully verifies their email |
| `protected_route_accessed` | When an authenticated user accesses a protected route |

### Adding New Events
When adding new routes or features, developers should:
- Identify key success and/or failure points.
- Use the record_event utility to capture meaningful events.
- Include useful metadata where relevant.

## Security Highlights

- Passwords securely hashed
- Access and Refresh tokens expire upon password changes
- CORS only allows trusted frontend origins
- Cooldown/rate limit to protect sensitive email actions

---

## ✨ Future Improvements

- OAuth integrations
---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Author

Built by [bb220](https://github.com/bb220)
Open to feedback and collaboration!
