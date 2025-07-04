
```markdown
# Credential Management Service for Storyapp

This project is a standalone **FastAPI-based microservice** that manages user credentials.
It supports **email/password-based login**, **OAuth login (Google, Facebook)**, and **JWT token-based authentication**,
and is designed to integrate cleanly with a React or Next.js frontend running on `localhost:3000`.

---

## 🔧 Tech Stack

- **Backend Framework:** FastAPI
- **Database:** PostgreSQL (via SQLAlchemy ORM)
- **Authentication:**
  - JWT (for sessionless API access)
  - OAuth 2.0 (Google, Facebook — using `Authlib`)
- **Password Hashing:** Passlib with bcrypt
- **Email Integration:** SMTP (with SendGrid or others)
- **CORS:** Configured for local development with frontend at `http://localhost:3000`

---

## 📁 Project Structure

```

credential\_service/
├── main.py                  # App entry point
├── database.py              # DB connection and session config
├── models.py                # SQLAlchemy ORM models
├── schemas.py               # Pydantic models for requests/responses
├── auth.py                  # Auth utilities (JWT, hashing)
├── routes/
│   ├── auth.py              # Sign up, login, password reset, etc.
│   └── oauth.py             # OAuth login flow stubs (Google, Facebook)
├── email\_utils.py           # SMTP integration (optional module)
├── .env                     # Secrets & environment variables
└── .gitignore               # Standard Python and secret ignores

````

---

## ✅ Features

### 🔐 Authentication
- Sign up with **email, username, and password**
- Login with **email + password**, returns **JWT token**
- Secure password hashing using `bcrypt`
- Support for **password reset via email**

### 🌐 OAuth (Google, Facebook)
- Google and Facebook login using OAuth 2.0 via `Authlib`
- Stores OAuth users in a separate `oauth_users` table
- Automatically issues JWT tokens after successful OAuth login

### 📧 Email Integration
- SMTP-based email verification and password reset (uses `.env` config)
- Stubbed `send_email()` function with support for:
  - SendGrid
  - Mailgun
  - Amazon SES
  - Gmail SMTP (with App Passwords)

### 🛂 Super User Handling
- Preconfigured superuser:
  - `user_id = suvodutta`
  - `email = suvodutta.isme@gmail.com`

### ⚙️ Configurability
- `.env` controls:
  - DB connection (`DATABASE_URL`)
  - JWT secrets
  - SMTP settings

### 🛡️ CORS
- Enabled for local development:
  - Allows API calls from `http://localhost:3000`

---

## 🚀 Quick Start

### 1. Clone and Install

```bash
git clone https://github.com/your-org/credentials.git
cd credential_service
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
pip install -r requirements.txt
````

### 2. Configure Environment

Create a `.env` file in the root:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/credential_db
JWT_SECRET=your_random_secret_key
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your_sendgrid_api_key
MAIL_FROM=noreply@yourdomain.com

GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
FACEBOOK_CLIENT_ID=your_facebook_app_id
FACEBOOK_CLIENT_SECRET=your_facebook_app_secret
```

Generate a secure JWT secret:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

### 3. Run the App

```bash
uvicorn main:app --reload
```

The API will be available at:
`http://localhost:8000`

---

## 🔑 API Endpoints

### Auth

| Method | Endpoint                       | Description              |
| ------ | ------------------------------ | ------------------------ |
| POST   | `/auth/signup`                 | Register a new user      |
| POST   | `/auth/login`                  | Login and get JWT token  |
| POST   | `/auth/change-password`        | Change password (JWT)    |
| POST   | `/auth/reset-password/request` | Send reset link to email |
| POST   | `/auth/reset-password/confirm` | Confirm reset and update |

### OAuth

| Method | Endpoint                   | Description                    |
| ------ | -------------------------- | ------------------------------ |
| GET    | `/oauth/google`            | Start Google OAuth login       |
| GET    | `/oauth/google/callback`   | Handle Google OAuth callback   |
| GET    | `/oauth/facebook`          | Start Facebook OAuth login     |
| GET    | `/oauth/facebook/callback` | Handle Facebook OAuth callback |

---

## ⚠️ Notes

* **Email Verification Suppressed:**
  In this version, email verification is **disabled** for faster login after signup. Users are marked `is_verified=True` at signup time.

* **Frontend Integration:**
  You can connect this to a Next.js or React frontend on `http://localhost:3000`. JWT tokens should be stored securely (e.g., in memory or secure HTTP-only cookies).

---

## 🔐 Security Checklist

* [x] Secure password hashing
* [x] JWT token signing (with env-based secret)
* [x] Optional email verification
* [x] OAuth flow isolation
* [ ] Rate limiting (optional)
* [ ] CSRF protection (if cookies used)

---

## 🧪 Testing Tips

Use [Postman](https://www.postman.com/) or [Insomnia](https://insomnia.rest/) to test:

1. **POST** `/auth/signup`
2. **POST** `/auth/login` → Receive `access_token`
3. Use token in `Authorization: Bearer <token>` for protected routes

---

## 📌 TODO (Future Enhancements)

* Implement OAuth callback flow (Google/Facebook)
* Add multi-factor authentication (MFA)
* Add admin dashboard for managing users
* Support account linking (OAuth + email/pass)
* Add refresh tokens and logout

---

## 👤 Author

**Suvojit Dutta**
→ [LinkedIn](https://linkedin.com/in/suvojit-dutta)
→ `suvodutta.isme@gmail.com`

---

## 📜 License

MIT — feel free to use and adapt with attribution.

