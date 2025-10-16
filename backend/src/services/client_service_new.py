from datetime import datetime
from typing import List
import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.models import ClientCreate, User, UserRole
from src.repositories import ClientRepository, UserRepository
from src.utils import hash_password
from src.utils.mappers import db_client_to_pydantic


def add_client(db: Session, user: User, client: ClientCreate):
    """Add a new client to the organization."""
    client_repo = ClientRepository(db)
    user_repo = UserRepository(db)
    
    if not user.org_id:
        raise HTTPException(status_code=400, detail="User is not associated with an organization")
    
    if client_repo.get_by_email(client.email):
        raise HTTPException(status_code=400, detail="Client with this email already exists")
    
    client_id = str(uuid.uuid4())
    client_data = {
        "id": client_id,
        "org_id": user.org_id,
        "name": client.name,
        "email": client.email,
        "phone": client.phone,
        "address": client.address,
        "created_at": datetime.utcnow()
    }
    db_client = client_repo.create(client_data)
    
    user_id = str(uuid.uuid4())
    user_data = {
        "id": user_id,
        "email": client.email,
        "name": client.name,
        "role": UserRole.CLIENT,
        "phone": client.phone,
        "created_at": datetime.utcnow()
    }
    user_repo.create(user_data, hash_password(client.password))
    
    return db_client_to_pydantic(db_client)


def get_clients_for_org(db: Session, user: User) -> List:
    """Get all clients for a user's organization."""
    client_repo = ClientRepository(db)
    
    if not user.org_id:
        raise HTTPException(status_code=400, detail="User is not associated with an organization")
    
    db_clients = client_repo.get_by_org_id(user.org_id)
    return [db_client_to_pydantic(c) for c in db_clients]
