# Auth API

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.12%2B-blue?style=for-the-badge&logo=python)
![SendGrid](https://img.shields.io/badge/SendGrid-00b2ff?style=for-the-badge&logo=sendgrid)
![Deployed on Railway](https://img.shields.io/badge/Railway-App-6c4cff?style=for-the-badge&logo=railway)
![License: MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

A lightweight, secure **Authentication API** built with **FastAPI** and **Python**, supporting:
- **User registration**
- **Login with JWT Authentication**
- **Access and Refresh Tokens**
- **Protected routes**
- **Password reset with real email sending via SendGrid**
- **Secure API key verification**

---

## Features

- 🛡 **User Registration** with secure password hashing (bcrypt)
- Email Verification via Secure Token (required before login)
- 🔐 **Login** with JWT Access Tokens (30 min) + Refresh Tokens (7 days)
- 🔒 **Protected Routes** using Bearer Token authentication
- 📬 **Password Reset Email Flow** (Real email delivery via SendGrid)
- 🚀 **Refresh Tokens** endpoint to renew access tokens
- 🔑 **API Key Middleware** to secure all API requests
- ⚡ **SQLite for local development** and **Postgres (Railway) in production**
- 🌐 **CORS configuration** for frontend integrations
- 🧪 Clean local dev setup ready for production upgrades

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
DATABASE_URL=sqlite:///./test.db
SECRET_KEY=your-super-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_MINUTES=10080  # 7 days
API_KEY=your-api-key-here
SENDGRID_API_KEY=your-sendgrid-api-key
FROM_EMAIL=your-verified-sender@example.com
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

## 📦 Endpoints Overview

### User Authentication

| Method | Endpoint | Description |
|:---|:---|:---|
| `POST` | `/register` | Create new user (sends verification email) |
| `GET` | `/verify-email` | Verify email using token from email link |
| `POST` | `/login` | Login user (only verified users allowed) |
| `POST` | `/refresh` | Refresh access token with refresh token |
| `GET` | `/protected` | Access a protected route (requires JWT) |

### Password Management

| Method | Endpoint | Description |
|:---|:---|:---|
| `POST` | `/request-password-reset` | Request password reset email |
| `POST` | `/reset-password` | Reset password using token from email |

---


## Security Highlights

- Passwords are **hashed** before storage (bcrypt)
- Access Tokens and Refresh Tokens are **short-lived** and **signed** (JWT)
- Password Reset Tokens are **short-lived** and securely signed
- API requests secured with a **valid API key** middleware
- CORS configured to allow only trusted frontend domains
- Real **email password reset flow** using **SendGrid** with API keys

---

## 📬 Email Requirements

- SendGrid account (free tier works)
- Verified sender email address or domain
- Frontend application (optional) to catch email verification redirects

---

## 🚀 Deployment

- App and database deployed on [Railway](https://railway.app/).
- Environment variables configured securely through Railway console.

---

## ✨ Future Improvements

- 🛡 Role-based access control (RBAC)
- Resend Verification Email endpoint
- Session Logging (multi-device login)
- OAuth2 Social Login (Google, GitHub)
- 🧪 Unit and integration test coverage

---

## 🏆 Status

- ✅ Authentication, registration, email verification, and password reset are working and production-ready.
- ✅ Ready to plug into a real frontend application or extend further.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Author

Built by [Brandon Bellero](https://github.com/bb220)  
Open to feedback and collaboration!
