from datetime import datetime
import uuid
from src.models import User, UserRole
from src.database import get_users_db, get_passwords_db
from src.utils import hash_password


def initialize_admin_user():
    """Initialize the default admin user."""
    users_db = get_users_db()
    passwords_db = get_passwords_db()
    
    admin_id = str(uuid.uuid4())
    admin_user = User(
        id=admin_id,
        email="admin@designerconnect.com",
        name="Admin",
        role=UserRole.ADMIN,
        created_at=datetime.now().isoformat(),
        phone="9999999999"
    )
    users_db[admin_id] = admin_user
    passwords_db[admin_id] = hash_password("admin123")
