from datetime import datetime
from typing import List
import uuid
from fastapi import HTTPException
from src.models import Client, ClientCreate, User, UserRole
from src.database import get_clients_db, get_users_db, get_passwords_db
from src.utils import hash_password


def create_client(user: User, client: ClientCreate) -> Client:
    """Create a new client."""
    clients_db = get_clients_db()
    users_db = get_users_db()
    passwords_db = get_passwords_db()
    
    if not user.org_id:
        raise HTTPException(status_code=400, detail="User is not associated with an organization")
    
    client_id = str(uuid.uuid4())
    client_user_id = str(uuid.uuid4())
    
    client_user = User(
        id=client_user_id,
        email=client.email,
        name=client.name,
        role=UserRole.CLIENT,
        org_id=user.org_id,
        created_at=datetime.now().isoformat(),
        phone=client.phone
    )
    users_db[client_user_id] = client_user
    passwords_db[client_user_id] = hash_password(client.password)
    
    new_client = Client(
        id=client_id,
        org_id=user.org_id,
        name=client.name,
        email=client.email,
        phone=client.phone,
        address=client.address,
        created_at=datetime.now().isoformat()
    )
    clients_db[client_id] = new_client
    
    return new_client


def get_clients_for_org(user: User) -> List[Client]:
    """Get all clients for a user's organization."""
    clients_db = get_clients_db()
    
    if not user.org_id:
        raise HTTPException(status_code=400, detail="User is not associated with an organization")
    
    clients = [c for c in clients_db.values() if c.org_id == user.org_id]
    return clients
