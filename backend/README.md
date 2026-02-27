# Breakthrough Publishers Backend API

FastAPI-based REST API backend for the Breakthrough Publishers Journal Management System.

## Features

- **Modern REST API** with FastAPI and Uvicorn
- **JWT Authentication** with access and refresh tokens
- **Password Hashing** using bcrypt for security
- **MySQL Database** integration with SQLAlchemy ORM
- **Pydantic Validation** for request/response schemas
- **CORS Support** for frontend integration
- **API Documentation** with Swagger UI and ReDoc
- **Security Middleware** with rate limiting foundations

## Tech Stack

- **Framework**: FastAPI 0.104+
- **Server**: Uvicorn
- **Database**: MySQL with SQLAlchemy ORM
- **Authentication**: JWT with python-jose
- **Password Hashing**: bcrypt via passlib
- **Validation**: Pydantic v2

## Project Structure

```
backend/
├── app/
│   ├── core/              # Authentication and security
│   │   ├── auth.py        # JWT and password utilities
│   │   └── security.py    # Dependency injection
│   ├── db/                # Database configuration
│   │   ├── database.py    # SQLAlchemy setup
│   │   └── models.py      # ORM models
│   ├── schemas/           # Pydantic models
│   │   └── user.py        # User request/response schemas
│   ├── api/               # API endpoints
│   │   └── v1/            # API version 1
│   │       └── auth.py    # Authentication endpoints
│   ├── utils/             # Utilities
│   │   └── exceptions.py  # Custom exceptions
│   ├── config.py          # Application settings
│   └── main.py            # FastAPI app factory
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
└── .gitignore            # Git ignore rules
```

## Setup Instructions

### 1. Prerequisites

- Python 3.8+
- MySQL Server running
- pip package manager

### 2. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your database credentials
# DB_HOST=localhost
# DB_PORT=3306
# DB_USER=root
# DB_PASSWORD=your_password
# DB_NAME=aacsjour_aacs
# JWT_SECRET_KEY=your-secret-key-min-32-chars
```

### 5. Run the Application

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Authentication Endpoints

#### 1. Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

#### 2. Refresh Token
```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

#### 3. Get Current User
```http
GET /api/v1/auth/me
Authorization: Bearer {access_token}

Response:
{
  "id": 1,
  "email": "user@example.com",
  "role": "author",
  "fname": "John",
  "lname": "Doe",
  "affiliation": "University",
  "specialization": "Computer Science"
}
```

#### 4. Change Password
```http
POST /api/v1/auth/change-password
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "current_password": "oldpassword123",
  "new_password": "newpassword123",
  "confirm_password": "newpassword123"
}

Response:
{
  "message": "Password changed successfully",
  "status": "success"
}
```

## Authentication

The API uses JWT (JSON Web Token) for authentication:

1. **Access Token**: Short-lived token (24 hours) for API requests
2. **Refresh Token**: Long-lived token (7 days) to obtain new access tokens
3. **Bearer Token**: Include access token in Authorization header: `Authorization: Bearer {token}`

### Example Protected Request
```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## Password Security

- Passwords are hashed using **bcrypt** (salted and iterative)
- Never store plain-text passwords
- Use `hash_password()` when creating users
- Use `verify_password()` for authentication
- Passwords are automatically hashed on change

## Database Integration

### Connection Details

The backend connects to the MySQL database:
- **Database**: aacsjour_aacs (legacy name)
- **Tables**: User, Journal, Paper, Author, Editor, etc.
- **ORM**: SQLAlchemy with connection pooling
- **Health Check**: Pre-ping enabled for stale connection handling

### Adding New Models

1. Create model in `app/db/models.py`:
```python
class Journal(Base):
    __tablename__ = "journal"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
```

2. Create schema in `app/schemas/journal.py`:
```python
class JournalResponse(BaseModel):
    id: int
    name: str
```

3. Create endpoints in `app/api/v1/journal.py`

## Error Handling

The API returns standard HTTP status codes:

- `200 OK`: Successful request
- `400 Bad Request`: Invalid input
- `401 Unauthorized`: Authentication failed
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

### Error Response Format
```json
{
  "detail": "Invalid email or password",
  "status_code": 401
}
```

## CORS Configuration

The API allows requests from:
- `http://localhost:3000` (React dev server)
- `http://localhost:5173` (Vite dev server)

Update `CORS_ORIGINS` in `.env` for production domains.

## Environment Variables

```
# Database
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=aacsjour_aacs

# JWT
JWT_SECRET_KEY=your-secret-key-min-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
REFRESH_TOKEN_EXPIRATION_DAYS=7

# API
API_TITLE=Breakthrough Publishers API
API_VERSION=1.0.0
ENVIRONMENT=development
DEBUG=False

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]
```

## Deployment

### Production Checklist

- [ ] Set `DEBUG=False` in `.env`
- [ ] Generate strong `JWT_SECRET_KEY` (min 32 chars)
- [ ] Configure database credentials securely
- [ ] Update `CORS_ORIGINS` for production domains
- [ ] Update `ALLOWED_HOSTS` in TrustedHostMiddleware
- [ ] Use HTTPS in production
- [ ] Set up rate limiting
- [ ] Configure logging
- [ ] Use production WSGI server (Gunicorn)

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Run with Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app.main:app
```

## Testing

### Manual Testing with cURL

```bash
# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'

# Get current user
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer {access_token}"
```

### Using Swagger UI

Visit http://localhost:8000/docs and use the interactive Swagger interface to test all endpoints.

## Future Endpoints

Planned endpoints for future development:

### Journals API
- `GET /api/v1/journals/` - List all journals
- `GET /api/v1/journals/{id}` - Get journal details
- `POST /api/v1/journals/` - Create journal (admin only)

### Papers API
- `GET /api/v1/papers/` - List papers
- `POST /api/v1/papers/` - Submit new paper
- `GET /api/v1/papers/{id}` - Get paper details

### Articles/News API
- `GET /api/v1/articles/latest/` - Get latest articles
- `GET /api/v1/news/latest/` - Get latest news
- `GET /api/v1/news/` - Get all news

## Troubleshooting

### MySQL Connection Error

```
Error: Can't connect to MySQL server
```

**Solution**: 
- Check MySQL is running
- Verify credentials in `.env`
- Check DB_HOST and DB_PORT are correct

### Invalid Token Error

```
Error: Invalid or expired token
```

**Solution**:
- Token may have expired (24 hours for access token)
- Use refresh token to get new access token
- Check Authorization header format: `Bearer {token}`

### CORS Error

```
Error: Access to XMLHttpRequest blocked by CORS policy
```

**Solution**:
- Add frontend URL to `CORS_ORIGINS` in `.env`
- Check CORS middleware is configured correctly
- Include credentials in frontend axios config

## Contributing

Follow these guidelines:
1. Create feature branch: `git checkout -b feature/name`
2. Write tests for new endpoints
3. Follow PEP 8 style guide
4. Add docstrings to all functions
5. Update README for new features
6. Submit pull request

## License

Copyright © 2026 Breakthrough Publishers. All rights reserved.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review API documentation at `/docs`
3. Check existing GitHub issues
4. Submit new issue with details
