# Auth API

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.12%2B-blue?style=for-the-badge&logo=python)
![SendGrid](https://img.shields.io/badge/SendGrid-00b2ff?style=for-the-badge&logo=sendgrid)
![Deployed on Railway](https://img.shields.io/badge/Railway-App-6c4cff?style=for-the-badge&logo=railway)
![License: MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

A secure authentication API providing:
- User Registration with Email Verification
- Login with JWT Access and Refresh Tokens
- Password Reset Flow via Email
- Token Invalidation on Password Reset
- Rate Limiting on Sensitive Email Actions
- CORS Middleware and API Key Protection
- Production-grade Scalability

---

## Technologies Used

- **FastAPI** — lightning-fast Python web framework
- **SQLAlchemy** — ORM for database interactions
- **PostgreSQL** — Production database via Railway
- **SQLite** — Local development database
- **Passlib** — Password hashing using bcrypt
- **Python-Jose** — JWT token creation and validation
- **SendGrid** — Real email sending service
- **python-dotenv** — Environment variable management
- **Uvicorn** — ASGI server for running FastAPI apps

---

## Setup and Installation

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
pip install -r requirements.txt
```

### 4. Create a `.env` file

Example `.env`:

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

# API Key for protecting backend endpoints (x-api-key header)
API_KEY=your_custom_api_key_here
```

✅ In production, `DATABASE_URL` and all env variables are managed securely with Railway.

---

## Running Locally

```bash
uvicorn app.main:app --reload
```

- API documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- OpenAPI schema: [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json)

---

## 🚀 Deployment

- App and database deployed on [Railway](https://railway.app/).
- Environment variables configured securely through Railway console.

---

## 📬 Email Requirements

- SendGrid account (free tier works)
- Verified sender email address or domain
- Frontend application (optional) to catch email verification redirects

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

## Security Highlights

- Passwords securely hashed
- Access and Refresh tokens expire upon password changes
- CORS only allows trusted frontend origins
- API Key required for all non-doc routes
- Cooldown/rate limit to protect sensitive email actions

---

## ✨ Future Improvements

- Session Logging
- Role-based access control (RBAC)
- Unit and integration test coverage
  
---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Author

Built by [bb220](https://github.com/bb220)
Open to feedback and collaboration!
