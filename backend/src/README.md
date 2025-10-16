# Backend Architecture

**Last Updated:** October 16, 2025

This document describes the restructured backend architecture for the Interio Palette application, including completed work, current priorities, and roadmap.

---

## 📊 Project Status

### ✅ Completed (Phase 0 - Foundation)

**Backend Restructuring** (Completed: Oct 16, 2025)
- ✅ Modular src/ layout with feature-based organization
- ✅ Separation of concerns: models, routes, services, dependencies
- ✅ SQLAlchemy ORM integration with all entities
- ✅ Repository pattern for data access layer
- ✅ Database-backed services (auth, organization, project, client, invoice)
- ✅ Dependency injection for database sessions
- ✅ Alembic migrations setup
- ✅ Database initialization script with default admin user
- ✅ Comprehensive architecture documentation

**Testing & Validation:**
- ✅ Admin login (email/password) working
- ✅ Organization CRUD working
- ✅ Phone OTP flow working
- ✅ Data persistence verified

### 🚧 Current Priority (Phase 1 - Core Features)

**Next Up:**
1. **File Attachments & Design Upload System** (~15-18 hours)
   - File upload endpoints (images, PDFs, 3D models)
   - Cloud storage integration (S3 or local for dev)
   - File metadata tracking
   - Preview/download functionality
   - Permission-based access

2. **Comments/Notes on Attachments** (~8-10 hours)
   - Comment model and repository
   - Nested comment threads
   - @mentions support
   - Mark as resolved functionality

3. **Support Ticket System** (~12-15 hours)
   - Ticket CRUD operations
   - Priority and category management
   - Assignment to team members
   - Status tracking (open, in-progress, resolved)
   - Comment threads on tickets

4. **Real-time Chat System** (~20-25 hours)
   - WebSocket setup
   - Project-level chat rooms
   - Direct messaging
   - Message persistence
   - Read receipts and typing indicators

**Phase 1 Estimate:** 55-68 hours total

### 📅 Roadmap

**Phase 2 - Integrations** (~30-35 hours)
- Real SMS/OTP provider (MSG91, Twilio)
- Payment gateway (Razorpay, Stripe)
- Email notifications
- Advanced calendar with reminders
- Push notifications

**Phase 3 - Advanced Features** (~40-50 hours)
- Analytics dashboard
- Document e-signing
- 3D design viewer
- Automated workflows
- Mobile app (React Native)

### ⚠️ Known Issues & Technical Debt

1. **Old service files** - Legacy `*_service.py` files exist alongside new `*_service_new.py`. Need cleanup.
2. **No automated tests** - Test structure exists but no tests written yet
3. **Deprecated datetime** - Using `datetime.utcnow()` instead of `datetime.now(datetime.UTC)`
4. **SQLite limitations** - Calendar attendees stored as JSON string (works fine, just not ideal)

### 🎯 Today's Work (October 16, 2025)

- [x] Set up SQLAlchemy and database models
- [x] Create repository layer
- [x] Implement database-backed services
- [x] Update all routes with dependency injection
- [x] Configure Alembic migrations
- [x] Create database initialization script
- [x] Test core flows (login, org creation, OTP)
- [x] Document architecture and setup
- [x] Create comprehensive README

**Next Session:**
- [ ] Begin Phase 1: File attachment system
- [ ] Or: Address technical debt (remove old files, add tests)
- [ ] Or: Review and test with stakeholders

---

## Directory Structure

```
backend/
├── app/
│   └── main.py                 # FastAPI application entry point
├── src/
│   ├── models/                 # Pydantic models and schemas
│   │   ├── enums.py           # Enum definitions (UserRole, ProjectStatus, etc.)
│   │   ├── user.py            # User models
│   │   ├── organization.py    # Organization models
│   │   ├── project.py         # Project models
│   │   ├── client.py          # Client models
│   │   ├── calendar.py        # Calendar event models
│   │   ├── design.py          # Project design models
│   │   ├── invoice.py         # Invoice models
│   │   └── __init__.py        # Model exports
│   ├── routes/                # API route handlers
│   │   ├── auth.py            # Authentication routes
│   │   ├── admin.py           # Admin routes
│   │   ├── organizations.py   # Organization routes
│   │   ├── projects.py        # Project routes
│   │   ├── clients.py         # Client routes
│   │   └── __init__.py        # Route exports
│   ├── services/              # Business logic layer
│   │   ├── auth_service.py           # Authentication logic
│   │   ├── organization_service.py   # Organization logic
│   │   ├── project_service.py        # Project logic
│   │   ├── client_service.py         # Client logic
│   │   ├── invoice_service.py        # Invoice logic
│   │   └── __init__.py               # Service exports
│   ├── database/              # Database layer
│   │   ├── in_memory.py       # In-memory database implementation
│   │   └── __init__.py        # Database exports
│   ├── dependencies/          # FastAPI dependencies
│   │   ├── auth.py            # Authentication dependencies
│   │   └── __init__.py        # Dependency exports
│   ├── utils/                 # Utility functions
│   │   ├── security.py        # Security utilities (hashing, tokens)
│   │   ├── notifications.py   # Notification utilities (SMS, email)
│   │   └── __init__.py        # Utility exports
│   ├── config/                # Configuration
│   │   ├── settings.py        # Application settings
│   │   └── __init__.py        # Config exports
│   └── core/                  # Core application setup
│       ├── init_data.py       # Initial data setup
│       └── __init__.py        # Core exports
├── tests/
│   ├── unit/                  # Unit tests
│   │   ├── test_auth_service.py
│   │   └── test_organization_service.py
│   └── integration/           # Integration tests
└── pyproject.toml            # Poetry dependencies

```

## Architecture Overview

### Models Layer
The models layer contains all Pydantic models that define the data structures used throughout the application. Models are organized by domain (user, organization, project, etc.).

### Routes Layer
Routes define the API endpoints and handle HTTP request/response. They are thin layers that validate input and delegate business logic to services.

### Services Layer
Services contain the core business logic of the application. Each service is responsible for a specific domain (auth, organizations, projects, etc.). Services interact with the database and implement business rules.

### Database Layer
The database layer provides an abstraction over the data storage. Currently using in-memory dictionaries, but can be easily replaced with a real database (PostgreSQL, MongoDB, etc.).

### Dependencies Layer
Dependencies provide reusable FastAPI dependencies for authentication, authorization, and other cross-cutting concerns.

### Utils Layer
Utilities provide helper functions for security (password hashing, token generation), notifications, and other common operations.

### Config Layer
Configuration management using Pydantic settings. Supports environment variables and .env files.

### Core Layer
Core application initialization, including default data setup.

## API Organization

### Authentication (`/api/auth`)
- POST `/api/auth/login` - Login with email/password
- GET `/api/auth/me` - Get current user
- POST `/api/auth/logout` - Logout
- POST `/api/auth/phone/request-otp` - Request OTP
- POST `/api/auth/phone/verify-otp` - Verify OTP

### Admin (`/api/admin`)
- Organization management
- Member management
- Invoice management

### Organizations (`/api/organizations`)
- Member management for current organization
- Organization-specific operations

### Projects (`/api/organizations/projects` and `/api/projects`)
- Project CRUD
- Team member management
- Calendar events
- Designs
- Invoices

### Clients (`/api/organizations/clients` and `/api/clients`)
- Client CRUD
- Client project access

## Benefits of This Structure

1. **Separation of Concerns**: Each layer has a specific responsibility
2. **Testability**: Business logic in services can be easily unit tested
3. **Maintainability**: Code is organized by domain and function
4. **Scalability**: Easy to add new features without modifying existing code
5. **Type Safety**: Comprehensive use of Pydantic models and type hints
6. **Flexibility**: Database layer can be swapped without changing business logic

## Testing

Unit tests are located in `tests/unit/` and test individual services in isolation. Integration tests in `tests/integration/` test the full API endpoints.

Run tests with:
```bash
poetry run pytest
```

## Running the Application

```bash
cd backend
poetry install
poetry run uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000` with automatic documentation at `http://localhost:8000/docs`.
