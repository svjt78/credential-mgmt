# Credential Management Service

A robust, scalable authentication and user management microservice built with FastAPI and PostgreSQL. This service provides secure user authentication, JWT token management, password handling, and OAuth integration for modern web applications. Designed as a standalone service that can be integrated with any frontend application.

## Features

- **Secure Authentication**: JWT-based authentication with configurable expiration
- **User Management**: Complete user lifecycle management with registration, verification, and profile updates
- **Password Security**: BCrypt hashing with secure password reset functionality
- **Email Verification**: Token-based email verification system with configurable TTL
- **OAuth Integration**: Extensible OAuth framework supporting Google, Facebook, and other providers
- **Service-to-Service Communication**: Internal API tokens for microservice authentication
- **Database Management**: SQLAlchemy ORM with PostgreSQL for reliable data persistence
- **Docker Ready**: Containerized deployment with Docker Compose
- **CORS Support**: Configurable cross-origin resource sharing for frontend integration
- **RESTful API**: Clean, documented API endpoints following REST principles

## Architecture

The Credential Service follows a microservice architecture pattern:

```
Frontend Application → Credential Service API → PostgreSQL Database
                    ↗ OAuth Providers (Google, Facebook, etc.)
```

### Technology Stack

- **Framework**: FastAPI with Pydantic data validation
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT tokens with PassLib BCrypt hashing
- **Server**: Uvicorn ASGI server
- **Containerization**: Docker with Docker Compose
- **Data Validation**: Pydantic schemas with email validation
- **Password Security**: BCrypt with configurable rounds

## Installation

### Prerequisites

- Python 3.8+
- Docker and Docker Compose
- PostgreSQL (if running without Docker)
- SMTP server for email verification (optional)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd credential_service
   ```

2. **Environment Setup**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start with Docker**
   ```bash
   docker-compose up -d
   ```

   The API will be available at `http://localhost:8001`

### Manual Setup

1. **Create virtual environment**
   ```bash
   python -m venv sec_venv
   source sec_venv/bin/activate  # On Windows: sec_venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup database**
   ```bash
   # Ensure PostgreSQL is running
   # Database tables will be created automatically on first run
   ```

4. **Start development server**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8001 --reload
   ```

## Configuration

### Required Environment Variables

```bash
# Database Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=credentialdb
DATABASE_URL=postgresql://postgres:password@localhost:5432/credentialdb

# JWT Configuration
SECRET_KEY=your_super_secret_jwt_key_here
ALGORITHM=HS256
JWT_SECRET=your_super_secret_jwt_key_here

# Email Verification
EMAIL_VERIFICATION_TTL_HOURS=24
FRONTEND_BASE_URL=http://localhost:3000

# Service-to-Service Authentication
INTERNAL_SERVICE_TOKEN=your_internal_service_token

# OAuth Configuration (Optional)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
FACEBOOK_CLIENT_ID=your_facebook_client_id
FACEBOOK_CLIENT_SECRET=your_facebook_client_secret
```

### Security Recommendations

- **JWT Secret**: Use a cryptographically secure random key (minimum 256 bits)
- **Database Password**: Use a strong, unique password for production
- **Internal Token**: Generate a unique token for service-to-service communication
- **Environment Isolation**: Never commit secrets to version control

## API Endpoints

### Authentication Endpoints

#### User Registration
```http
POST /auth/signup
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "john_doe",
  "password": "securePassword123"
}
```

**Response:**
```json
{
  "id": 1,
  "user_id": "uuid-string",
  "email": "user@example.com",
  "username": "john_doe",
  "is_active": true,
  "is_verified": false,
  "verificationToken": "verification-token-uuid"
}
```

#### User Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response:**
```json
{
  "access_token": "jwt-token-string",
  "token_type": "bearer",
  "user_id": "uuid-string",
  "email": "user@example.com",
  "username": "john_doe",
  "is_active": true,
  "is_verified": true
}
```

#### Email Verification
```http
POST /auth/verify-email
Content-Type: application/json

{
  "token": "verification-token-uuid"
}
```

#### Password Reset Request
```http
POST /auth/reset-password-request
Content-Type: application/json

{
  "email": "user@example.com"
}
```

#### Password Reset Confirmation
```http
POST /auth/reset-password-confirm
Content-Type: application/json

{
  "token": "reset-token-uuid",
  "new_password": "newSecurePassword123"
}
```

#### Change Password
```http
POST /auth/change-password
Authorization: Bearer <jwt-token>
Content-Type: application/json

{
  "old_password": "currentPassword",
  "new_password": "newSecurePassword123"
}
```

### OAuth Endpoints

#### OAuth Login
```http
GET /oauth/{provider}
```
Supported providers: `google`, `facebook`

#### OAuth Callback
```http
GET /oauth/{provider}/callback?code=authorization_code
```

### Utility Endpoints

#### Health Check
```http
GET /
```

**Response:**
```json
{
  "message": "Welcome to the Credential Management Service"
}
```

## Database Schema

### User Model

```python
class User(Base):
    __tablename__ = "users"
    
    id: int                              # Primary key
    user_id: str                         # Unique UUID identifier
    email: str                           # Unique email address
    username: str                        # Display name
    hashed_password: str                 # BCrypt hashed password
    is_active: bool                      # Account status
    is_verified: bool                    # Email verification status
    created_at: datetime                 # Account creation timestamp
    updated_at: datetime                 # Last update timestamp
    email_verification_token: str        # Email verification token
    password_reset_token: str            # Password reset token
    token_expiration: datetime           # Token expiration time
```

### Key Features

- **Unique Constraints**: Email addresses are enforced unique
- **Password Security**: BCrypt hashing with configurable rounds
- **Token Management**: Separate tokens for email verification and password reset
- **Audit Trail**: Creation and update timestamps for all records
- **Flexible Authentication**: Support for both password and OAuth-based authentication

## Development

### Project Structure

```
credential_service/
├── main.py                 # FastAPI application entry point
├── auth.py                 # Authentication utilities and JWT handling
├── database.py             # Database connection and session management
├── models.py               # SQLAlchemy database models
├── schemas.py              # Pydantic request/response schemas
├── routes/                 # API route handlers
│   ├── auth.py            # Authentication endpoints
│   └── oauth.py           # OAuth integration endpoints
├── requirements.txt        # Python dependencies
├── Dockerfile             # Container configuration
├── docker-compose.yml     # Multi-container setup
└── entrypoint.sh          # Container startup script
```

### Key Components

- **FastAPI Application**: High-performance async web framework
- **SQLAlchemy Models**: Type-safe database models with relationships
- **Pydantic Schemas**: Request/response validation and serialization
- **JWT Authentication**: Stateless token-based authentication
- **Password Hashing**: Secure BCrypt implementation
- **Database Sessions**: Connection pooling and transaction management

### Development Scripts

```bash
# Start development server with auto-reload
uvicorn main:app --host 0.0.0.0 --port 8001 --reload

# Run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f api

# Access database
docker-compose exec db psql -U postgres -d credentialdb

# Stop services
docker-compose down
```

## Testing

### Manual Testing

The service includes comprehensive API endpoints that can be tested using tools like curl, Postman, or HTTPie:

```bash
# Test user registration
curl -X POST "http://localhost:8001/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"testuser","password":"testpass123"}'

# Test user login
curl -X POST "http://localhost:8001/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'

# Test protected endpoint
curl -X POST "http://localhost:8001/auth/change-password" \
  -H "Authorization: Bearer <jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{"old_password":"testpass123","new_password":"newpass123"}'
```

### Integration Testing

The service is designed to integrate seamlessly with frontend applications:

1. **User Registration Flow**: Frontend calls signup endpoint, receives verification token
2. **Email Verification**: Frontend handles email verification link with token
3. **Authentication**: Frontend stores JWT token for subsequent API calls
4. **Token Refresh**: Implement token refresh logic for long-lived sessions

## Deployment

### Production Build

```bash
# Build production image
docker build -f Dockerfile -t credential-service:latest .

# Run production container
docker run -p 8001:8001 --env-file .env.prod credential-service:latest
```

### Docker Compose Production

```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d

# With environment file
docker-compose --env-file .env.prod up -d
```

### Environment-Specific Configuration

```bash
# Development
uvicorn main:app --host 0.0.0.0 --port 8001 --reload

# Production
uvicorn main:app --host 0.0.0.0 --port 8001 --workers 4

# With Gunicorn (production)
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001
```

## Security

### Authentication Security

- **JWT Tokens**: Short-lived access tokens with configurable expiration
- **Password Hashing**: BCrypt with adaptive rounds for future-proofing
- **Token Validation**: Comprehensive JWT signature and expiration validation
- **CORS Configuration**: Configurable origins for cross-domain requests

### Best Practices

- **Environment Variables**: All secrets stored in environment variables
- **Password Policies**: Configurable password strength requirements
- **Rate Limiting**: Implement rate limiting for authentication endpoints (recommended)
- **HTTPS Only**: Always use HTTPS in production environments
- **Database Security**: Use connection pooling and prepared statements

## Future Development

The Credential Management Service is continuously evolving with several exciting features planned:

### Enhanced Security Features
- **Multi-Factor Authentication (MFA)**: SMS, TOTP, and hardware key support
- **OAuth 2.0 PKCE**: Enhanced security for public clients
- **JWT Refresh Tokens**: Long-lived refresh tokens with rotation
- **Session Management**: Advanced session handling with device tracking

### Integration & Analytics
- **Google Analytics Integration**: User authentication flow analytics
- **Audit Logging**: Comprehensive authentication and authorization logs
- **Metrics & Monitoring**: Prometheus metrics and health checks
- **API Rate Limiting**: Redis-based rate limiting with configurable rules

### Advanced Features
- **Social Login Expansion**: GitHub, LinkedIn, Microsoft, Apple OAuth
- **Custom OAuth Providers**: Support for enterprise identity providers
- **SAML Integration**: Enterprise single sign-on support
- **Passwordless Authentication**: Magic link and WebAuthn support

### Enterprise Features
- **Multi-Tenant Support**: Organization-based user management
- **Advanced User Roles**: Hierarchical role-based access control
- **API Key Management**: Service-to-service authentication tokens
- **Compliance Features**: GDPR, CCPA data handling and user privacy controls

### Developer Experience
- **OpenAPI Documentation**: Interactive API documentation with Swagger UI
- **SDK Generation**: Client libraries for popular programming languages
- **Webhook Support**: Real-time event notifications for user actions
- **GraphQL API**: Alternative query interface for complex data requirements

## Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 Python style guidelines
- Add type hints for all function parameters and return values
- Include docstrings for all public functions and classes
- Write tests for new features
- Update API documentation as needed

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions:

- **Issues**: GitHub Issues for bug reports and feature requests
- **Discussions**: GitHub Discussions for community support
- **Email**: Contact the development team at suvodutta.isme@gmail.com

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/) and [SQLAlchemy](https://sqlalchemy.org/)
- Database powered by [PostgreSQL](https://postgresql.org/)
- Authentication security by [PassLib](https://passlib.readthedocs.io/) and [PyJWT](https://pyjwt.readthedocs.io/)
- Data validation by [Pydantic](https://pydantic-docs.helpmanual.io/)
- Containerization with [Docker](https://docker.com/)

---

**Credential Management Service** - Secure, scalable authentication for modern applications.
