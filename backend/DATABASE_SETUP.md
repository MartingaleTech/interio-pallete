# Database Setup Guide

This guide explains how to set up databases for development, testing, and production environments.

## Overview

The application supports both SQLite (for development/testing) and PostgreSQL (for production). The database configuration is managed through the `DATABASE_URL` environment variable.

## Development Database Setup

### Using SQLite (Default)

SQLite is the default database for local development. No additional setup is required.

1. The database file will be created automatically at `./interio_palette.db`
2. Initialize the database with seed data:
   ```bash
   cd backend
   poetry run python -m src.core.init_db
   ```

This creates:
- Database tables based on SQLAlchemy models
- Default admin user (email: `admin@interiopalette.com`, password: `admin123`)

### Using PostgreSQL for Development

For a production-like environment, you can use PostgreSQL locally:

1. Install PostgreSQL on your system
2. Create a database and user:
   ```sql
   CREATE DATABASE interio_palette_dev;
   CREATE USER interio_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE interio_palette_dev TO interio_user;
   ```

3. Set the DATABASE_URL environment variable:
   ```bash
   export DATABASE_URL="postgresql+psycopg://interio_user:your_password@localhost:5432/interio_palette_dev"
   ```

4. Run migrations:
   ```bash
   cd backend
   poetry run alembic upgrade head
   ```

5. Initialize with seed data:
   ```bash
   poetry run python -m src.core.init_db
   ```

## Test Database Setup

### Automated Test Database

Tests automatically use an in-memory SQLite database with the following configuration:

- **Database URL**: `sqlite+pysqlite:///:memory:`
- **Connection Pool**: StaticPool (ensures all connections share the same in-memory database)
- **Thread Safety**: `check_same_thread=False` (allows FastAPI's TestClient to work correctly)

The test infrastructure is configured in `tests/conftest.py` and automatically:
1. Creates tables before tests run
2. Provides isolated database sessions for each test
3. Cleans up data between tests to avoid conflicts
4. Drops tables after all tests complete

### Running Tests

```bash
cd backend
poetry run pytest                    # Run all tests
poetry run pytest tests/test_routes_auth.py  # Run specific test file
poetry run pytest -v                 # Verbose output
poetry run pytest -k "test_login"    # Run tests matching pattern
```

### Using PostgreSQL for Tests

For more production-like testing, you can use a PostgreSQL test database:

1. Create a test database:
   ```sql
   CREATE DATABASE interio_palette_test;
   GRANT ALL PRIVILEGES ON DATABASE interio_palette_test TO interio_user;
   ```

2. Set the DATABASE_URL before running tests:
   ```bash
   export DATABASE_URL="postgresql+psycopg://interio_user:your_password@localhost:5432/interio_palette_test"
   poetry run pytest
   ```

Note: When using PostgreSQL for tests, the database will be cleaned between test runs but not automatically dropped.

## Production Database Setup

### PostgreSQL Configuration

1. Set up a PostgreSQL database on your production server or cloud provider
2. Create a database and user with appropriate permissions
3. Set the DATABASE_URL environment variable:
   ```bash
   export DATABASE_URL="postgresql+psycopg://user:password@host:5432/dbname"
   ```

4. Run migrations to create tables:
   ```bash
   poetry run alembic upgrade head
   ```

5. Initialize with production data:
   ```bash
   poetry run python -m src.core.init_db
   ```

### Environment Variables

Set these environment variables in your production environment:

```bash
DATABASE_URL="postgresql+psycopg://user:password@host:5432/dbname"
TESTING="false"  # Ensure this is false in production
```

## Database Migrations

### Creating a New Migration

When you modify database models:

```bash
cd backend
poetry run alembic revision --autogenerate -m "Description of changes"
```

### Applying Migrations

```bash
poetry run alembic upgrade head
```

### Rolling Back Migrations

```bash
poetry run alembic downgrade -1  # Rollback one migration
poetry run alembic downgrade <revision>  # Rollback to specific revision
```

## Troubleshooting

### SQLite Threading Errors

If you see errors like "SQLite objects created in a thread can only be used in that same thread":

- Ensure `check_same_thread=False` is set in the database configuration
- For in-memory databases, ensure `StaticPool` is used
- Verify that tests are using the shared engine from `conftest.py`

### UNIQUE Constraint Violations in Tests

If tests fail with UNIQUE constraint violations:

- Ensure the `db_session` fixture in `conftest.py` properly cleans up data between tests
- Check that test fixtures are not creating duplicate data
- Verify that the cleanup logic in `conftest.py` is executing correctly

### Connection Pool Exhaustion

If you see "connection pool exhausted" errors:

- Check for database sessions that are not being properly closed
- Ensure all database operations use the `get_db()` dependency
- Verify that repository methods don't store sessions as instance variables

### Migration Conflicts

If migrations fail to apply:

1. Check the current migration version:
   ```bash
   poetry run alembic current
   ```

2. View migration history:
   ```bash
   poetry run alembic history
   ```

3. If needed, manually resolve conflicts in migration files

## Best Practices

1. **Always use the `get_db()` dependency** for database sessions in route handlers
2. **Never store database sessions** as global variables or instance variables in repositories
3. **Use transactions** for operations that modify multiple tables
4. **Test with PostgreSQL** before deploying to production to catch database-specific issues
5. **Backup production databases** regularly
6. **Use connection pooling** in production for better performance
7. **Monitor database performance** and optimize slow queries

## Configuration Reference

### SQLite Configuration (Development/Testing)

```python
# For file-based SQLite
DATABASE_URL = "sqlite:///./interio_palette.db"

# For in-memory SQLite (tests)
DATABASE_URL = "sqlite+pysqlite:///:memory:"
```

### PostgreSQL Configuration (Production)

```python
# Standard PostgreSQL connection
DATABASE_URL = "postgresql+psycopg://user:password@host:5432/dbname"

# With SSL (recommended for production)
DATABASE_URL = "postgresql+psycopg://user:password@host:5432/dbname?sslmode=require"
```

### Connection Pool Settings

For production PostgreSQL, you may want to configure connection pooling:

```python
from sqlalchemy import create_engine

engine = create_engine(
    DATABASE_URL,
    pool_size=5,          # Number of connections to maintain
    max_overflow=10,      # Maximum number of connections to create beyond pool_size
    pool_timeout=30,      # Seconds to wait before giving up on getting a connection
    pool_recycle=3600,    # Recycle connections after 1 hour
)
```

## Additional Resources

- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [FastAPI Database Documentation](https://fastapi.tiangolo.com/tutorial/sql-databases/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
