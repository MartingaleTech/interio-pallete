# Interio Palette Backend

A modular, scalable backend for the Interio Palette platform built with FastAPI and SQLAlchemy.

## Architecture

The backend follows clean architecture principles with clear separation of concerns:

```
backend/
├── app/
│   └── main.py                    # FastAPI application entry point
├── src/
│   ├── models/                    # Pydantic models for API validation
│   ├── database/
│   │   ├── models.py              # SQLAlchemy ORM models
│   │   └── in_memory.py           # Legacy in-memory database (deprecated)
│   ├── repositories/              # Data access layer
│   │   ├── user_repository.py
│   │   ├── organization_repository.py
│   │   ├── project_repository.py
│   │   ├── team_repository.py
│   │   └── invoice_repository.py
│   ├── services/                  # Business logic layer
│   │   ├── auth_service_new.py
│   │   ├── organization_service_new.py
│   │   ├── project_service_new.py
│   │   ├── client_service_new.py
│   │   └── invoice_service_new.py
│   ├── routes/                    # API route handlers
│   │   ├── auth.py
│   │   ├── admin.py
│   │   ├── organizations.py
│   │   ├── projects.py
│   │   └── clients.py
│   ├── dependencies/              # Dependency injection
│   │   └── auth_new.py            # Authentication dependencies
│   ├── config/                    # Configuration
│   │   ├── settings.py
│   │   └── database.py            # Database connection setup
│   ├── utils/                     # Utility functions
│   │   ├── security.py            # Password hashing, token generation
│   │   ├── notifications.py       # OTP and notifications
│   │   └── mappers.py             # DB model to Pydantic converters
│   └── core/
│       ├── init_data.py           # Legacy initialization
│       └── init_db.py             # Database initialization script
├── alembic/                       # Database migrations
│   └── versions/
├── tests/                         # Unit tests
│   └── unit/
├── alembic.ini                    # Alembic configuration
└── pyproject.toml                 # Poetry dependencies

```

## Key Features

- **Clean Architecture**: Repository pattern, service layer, dependency injection
- **Database**: SQLAlchemy ORM with SQLite (easily switchable to PostgreSQL)
- **Migrations**: Alembic for database schema management
- **Type Safety**: Pydantic models for request/response validation
- **Authentication**: JWT-like token-based auth with phone OTP support
- **Role-Based Access**: Admin, Organization Owner/Member, Client roles
- **Modular Design**: Feature-based organization for scalability

## Setup

### Prerequisites

- Python 3.8+
- Poetry (Python package manager)

### Installation

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
poetry install
```

3. Initialize the database:
```bash
poetry run python -m src.core.init_db
```

This creates the database tables and a default admin user:
- **Email**: admin@interiopalette.com
- **Password**: admin123
- **Phone**: 9999999999

4. Start the development server:
```bash
poetry run fastapi dev app/main.py
```

The backend will be available at `http://localhost:8000`

API documentation is available at `http://localhost:8000/docs`

## Database Management

### Migrations

The project uses Alembic for database migrations.

**Create a new migration**:
```bash
poetry run alembic revision --autogenerate -m "Description of changes"
```

**Apply migrations**:
```bash
poetry run alembic upgrade head
```

**Rollback migration**:
```bash
poetry run alembic downgrade -1
```

### Database Configuration

The database URL can be configured via environment variable:
```bash
export DATABASE_URL="sqlite:///./interio_palette.db"
```

For PostgreSQL:
```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/interio_palette"
```

## Architecture Patterns

### Repository Pattern

Repositories handle all database operations, providing a clean abstraction over SQLAlchemy:

```python
from src.repositories import UserRepository

user_repo = UserRepository(db)
user = user_repo.get_by_email("user@example.com")
```

### Service Layer

Services contain business logic and use repositories for data access:

```python
from src.services import auth_service_new

def login(db: Session, credentials: UserLogin):
    return auth_service_new.login_user(db, credentials)
```

### Dependency Injection

FastAPI dependencies provide database sessions and authentication:

```python
from fastapi import Depends
from sqlalchemy.orm import Session
from src.config.database import get_db
from src.dependencies.auth_new import get_current_user

@router.get("/protected")
async def protected_route(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    # Your logic here
    pass
```

## API Structure

### Authentication
- `POST /api/auth/login` - Email/password login
- `POST /api/auth/phone/request-otp` - Request OTP
- `POST /api/auth/phone/verify-otp` - Verify OTP and login
- `GET /api/auth/me` - Get current user
- `POST /api/auth/logout` - Logout

### Admin (Super Admin only)
- `POST /api/admin/organizations` - Create organization
- `GET /api/admin/organizations` - List all organizations
- `GET /api/admin/organizations/{org_id}` - Get organization
- `PATCH /api/admin/organizations/{org_id}` - Update organization
- `DELETE /api/admin/organizations/{org_id}` - Delete organization

### Organizations
- `GET /api/organizations/members` - List organization members
- `POST /api/organizations/members` - Add member
- `PUT /api/organizations/members/{member_id}` - Update member
- `DELETE /api/organizations/members/{member_id}` - Remove member

### Projects
- `POST /api/organizations/projects` - Create project
- `GET /api/organizations/projects` - List projects
- `GET /api/organizations/projects/{project_id}` - Get project
- `POST /api/projects/{project_id}/team` - Add team member
- `GET /api/projects/{project_id}/team` - List team members
- `POST /api/projects/{project_id}/calendar` - Create event
- `GET /api/projects/{project_id}/calendar` - List events
- `POST /api/projects/{project_id}/designs` - Upload design
- `GET /api/projects/{project_id}/designs` - List designs
- `POST /api/projects/{project_id}/invoices` - Create invoice
- `GET /api/projects/{project_id}/invoices` - List invoices

### Clients
- `POST /api/organizations/clients` - Add client
- `GET /api/organizations/clients` - List clients
- `GET /api/clients/projects` - Get client's projects

## Testing

Run tests with:
```bash
poetry run pytest
```

Run tests with coverage:
```bash
poetry run pytest --cov=src
```

## Development

### Adding a New Feature

1. **Create database models** in `src/database/models.py`
2. **Create repository** in `src/repositories/`
3. **Create service** in `src/services/`
4. **Create routes** in `src/routes/`
5. **Create migration**: `poetry run alembic revision --autogenerate -m "Add feature"`
6. **Apply migration**: `poetry run alembic upgrade head`

### Code Organization Principles

- **Models**: Pydantic models for API requests/responses
- **Database Models**: SQLAlchemy ORM models for database tables
- **Repositories**: Single responsibility - database operations only
- **Services**: Business logic - no direct database access
- **Routes**: HTTP handling - delegate to services
- **Dependencies**: Reusable injection patterns

## Environment Variables

- `DATABASE_URL`: Database connection string (default: SQLite)
- Add other environment variables in `.env` file

## Production Deployment

For production:

1. **Switch to PostgreSQL**:
```bash
export DATABASE_URL="postgresql://user:pass@host:5432/dbname"
```

2. **Run migrations**:
```bash
poetry run alembic upgrade head
```

3. **Use production server**:
```bash
poetry run fastapi run app/main.py
```

4. **Enable HTTPS** and configure CORS appropriately in `app/main.py`

## Contributing

When adding new code:
- Follow existing architectural patterns
- Add type hints
- Write unit tests
- Create migrations for schema changes
- Update this README if adding new features

## License

Proprietary - All rights reserved
