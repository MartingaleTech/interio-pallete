"""Initialize database with default admin user."""
from datetime import datetime, timezone
import uuid
from sqlalchemy.orm import Session
from src.config.database import engine, Base, SessionLocal
from src.database import models
from src.models.enums import UserRole
from src.utils.security import hash_password


def init_db():
    """Initialize database with tables and default admin user."""
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        admin = db.query(models.User).filter(
            models.User.email == "admin@interiopalette.com"
        ).first()
        
        if not admin:
            admin_id = str(uuid.uuid4())
            admin_data = models.User(
                id=admin_id,
                email="admin@interiopalette.com",
                name="Super Admin",
                role=UserRole.ADMIN,
                phone="9999999999",
                password_hash=hash_password("admin123"),
                created_at=datetime.now(timezone.utc)
            )
            db.add(admin_data)
            db.commit()
            print("✓ Default admin user created:")
            print("  Email: admin@interiopalette.com")
            print("  Password: admin123")
            print("  Phone: 9999999999")
        else:
            print("✓ Admin user already exists")
    
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
