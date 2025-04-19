# Auth API

![License](https://img.shields.io/badge/license-MIT-green)
![Framework](https://img.shields.io/badge/framework-FastAPI-0ba360)
![Deployment](https://img.shields.io/badge/deployment-Railway-6c4cff)
![Python](https://img.shields.io/badge/python-3.12%2B-blue)

A lightweight, secure **Authentication API** built with **FastAPI** and **Python**, supporting:
- **User registration**
- **Login with JWT Authentication**
- **Access and Refresh Tokens**
- **Protected routes**
- **Password reset (in progress)**
- **Secure API key verification**

---

## Features

- 🛡 **User Registration** with secure password hashing (bcrypt)
- 🔐 **Login** with JWT Access Tokens (30 min) + Refresh Tokens (7 days)
- 🔒 **Protected Routes** using Bearer Token authentication
- 🚀 **Refresh Tokens** endpoint to renew access tokens
- 🔑 **API Key Middleware** to secure all requests
- ⚡ **SQLite for local development** and **Postgres (Railway) in production**
- 🌐 **CORS configured** for frontend integrations

---

## Technologies Used

- **FastAPI** — lightning-fast Python web framework
- **SQLAlchemy** — ORM for database interactions
- **PostgreSQL** — Production database via Railway
- **SQLite** — Local development database
- **Passlib** — Password hashing using bcrypt
- **Python-Jose** — JWT token creation and validation
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
```

✅ In production, `DATABASE_URL` and other env vars are managed by Railway.

---

## Running Locally

```bash
uvicorn app.main:app --reload
```

- API documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- OpenAPI schema: [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json)

---

## API Endpoints

| Method | Endpoint | Purpose |
|:---|:---|:---|
| `POST` | `/register` | Register a new user |
| `POST` | `/login` | Log in and receive access + refresh tokens |
| `POST` | `/refresh` | Refresh access token using refresh token |
| `GET` | `/protected` | Access protected route (requires Bearer token) |
| `POST` | `/reset-password` | (Planned) Reset password functionality |
| `POST` | `/request-password-reset` | (Planned) Send password reset email |

---

## Security Highlights

- Passwords are **hashed** before storage (bcrypt)
- Tokens are **short-lived** and **signed** (JWT)
- Refresh tokens enable **longer sessions** without compromising security
- API access requires a **valid API key header**
- Environment variables securely managed using `.env` (local) or Railway (production)

---

## Deployment

This project is deployed on [Railway](https://railway.app/).

---

## Future Improvements

- 📬 Password reset email functionality (coming next)
- 🖥️ Frontend integration (React/Next.js)
- 🧪 Unit and integration tests
- 🛡 Role-based access control (RBAC)
- ⚙️ Alembic migrations for database versioning


---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Author

Built by [Brandon Bellero](https://github.com/bb220)  
Open to feedback and collaboration!
