from datetime import datetime, timedelta
from typing import List
import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.models import (
    OrganizationCreate, OrganizationUpdate,
    User, UserRole, OrgMemberCreate, SubscriptionStatus
)
from src.repositories import UserRepository, OrganizationRepository, ProjectRepository
from src.utils import hash_password
from src.utils.mappers import db_user_to_pydantic, db_organization_to_pydantic


def create_organization(db: Session, org: OrganizationCreate):
    """Create a new organization with an owner user."""
    user_repo = UserRepository(db)
    org_repo = OrganizationRepository(db)
    
    org_id = str(uuid.uuid4())
    owner_id = str(uuid.uuid4())
    
    owner_data = {
        "id": owner_id,
        "email": org.owner_email,
        "name": org.owner_name,
        "role": UserRole.ORG_OWNER,
        "org_id": org_id,
        "created_at": datetime.now(timezone.utc),
        "phone": org.owner_phone
    }
    db_owner = user_repo.create(owner_data, hash_password(org.owner_password))
    
    subscription_start = datetime.now(timezone.utc)
    subscription_end = subscription_start + timedelta(days=365)
    
    org_data = {
        "id": org_id,
        "name": org.name,
        "email": org.email,
        "phone": org.phone,
        "address": org.address,
        "city": org.city,
        "state": org.state,
        "pincode": org.pincode,
        "owner_id": owner_id,
        "subscription_status": SubscriptionStatus.ACTIVE,
        "subscription_plan": org.subscription_plan,
        "subscription_start": subscription_start,
        "subscription_end": subscription_end,
        "created_at": datetime.now(timezone.utc)
    }
    db_org = org_repo.create(org_data)
    
    return db_organization_to_pydantic(db_org)


def get_all_organizations(db: Session) -> List:
    """Get all organizations."""
    org_repo = OrganizationRepository(db)
    db_orgs = org_repo.get_all()
    return [db_organization_to_pydantic(org) for org in db_orgs]


def get_organization_by_id(db: Session, org_id: str):
    """Get an organization by ID."""
    org_repo = OrganizationRepository(db)
    db_org = org_repo.get_by_id(org_id)
    if not db_org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return db_organization_to_pydantic(db_org)


def update_organization(db: Session, org_id: str, updates: OrganizationUpdate):
    """Update an organization."""
    org_repo = OrganizationRepository(db)
    
    if not org_repo.get_by_id(org_id):
        raise HTTPException(status_code=404, detail="Organization not found")
    
    update_data = updates.model_dump(exclude_unset=True)
    db_org = org_repo.update(org_id, **update_data)
    
    return db_organization_to_pydantic(db_org)


def delete_organization(db: Session, org_id: str) -> dict:
    """Delete an organization and all related data."""
    org_repo = OrganizationRepository(db)
    user_repo = UserRepository(db)
    project_repo = ProjectRepository(db)
    
    if not org_repo.get_by_id(org_id):
        raise HTTPException(status_code=404, detail="Organization not found")
    
    users = user_repo.get_by_org_id(org_id)
    for user in users:
        user_repo.delete(user.id)
    
    projects = project_repo.get_by_org_id(org_id)
    for project in projects:
        project_repo.delete(project.id)
    
    org_repo.delete(org_id)
    
    return {"message": "Organization deleted successfully"}


def get_organization_members(db: Session, org_id: str) -> List[User]:
    """Get all members of an organization."""
    org_repo = OrganizationRepository(db)
    user_repo = UserRepository(db)
    
    if not org_repo.get_by_id(org_id):
        raise HTTPException(status_code=404, detail="Organization not found")
    
    db_users = user_repo.get_by_org_id(org_id)
    return [db_user_to_pydantic(u) for u in db_users]


def add_organization_member(db: Session, org_id: str, member: OrgMemberCreate) -> User:
    """Add a member to an organization."""
    org_repo = OrganizationRepository(db)
    user_repo = UserRepository(db)
    
    if not org_repo.get_by_id(org_id):
        raise HTTPException(status_code=404, detail="Organization not found")
    
    member_id = str(uuid.uuid4())
    member_data = {
        "id": member_id,
        "email": member.email,
        "name": member.name,
        "role": UserRole.ORG_MEMBER,
        "org_id": org_id,
        "created_at": datetime.now(timezone.utc),
        "phone": member.phone
    }
    db_member = user_repo.create(member_data, hash_password(member.password))
    
    return db_user_to_pydantic(db_member)


def remove_organization_member(db: Session, org_id: str, user_id: str) -> dict:
    """Remove a member from an organization."""
    org_repo = OrganizationRepository(db)
    user_repo = UserRepository(db)
    
    if not org_repo.get_by_id(org_id):
        raise HTTPException(status_code=404, detail="Organization not found")
    
    db_user = user_repo.get_by_id(user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if db_user.org_id != org_id:
        raise HTTPException(status_code=400, detail="User is not a member of this organization")
    
    if db_user.role == UserRole.ORG_OWNER:
        raise HTTPException(status_code=400, detail="Cannot remove organization owner")
    
    user_repo.delete(user_id)
    
    return {"message": "Member removed successfully"}


def get_members_for_user_org(db: Session, user: User) -> List[User]:
    """Get members for the user's organization."""
    user_repo = UserRepository(db)
    
    if not user.org_id:
        raise HTTPException(status_code=400, detail="User is not part of an organization")
    
    db_users = user_repo.get_by_org_id(user.org_id)
    return [db_user_to_pydantic(u) for u in db_users]


def add_member_to_user_org(db: Session, user: User, member: OrgMemberCreate) -> User:
    """Add a member to the user's organization."""
    user_repo = UserRepository(db)
    
    if not user.org_id:
        raise HTTPException(status_code=400, detail="User is not part of an organization")
    
    if user.role not in [UserRole.ORG_OWNER, UserRole.ORG_MEMBER]:
        raise HTTPException(status_code=403, detail="Not authorized to add members")
    
    if user_repo.get_by_email(member.email):
        raise HTTPException(status_code=400, detail="Email already exists")
    
    member_id = str(uuid.uuid4())
    first_name = member.first_name or ''
    last_name = member.last_name or ''
    member_name = f"{first_name} {last_name}".strip() if first_name or last_name else member.name
    
    member_data = {
        "id": member_id,
        "email": member.email,
        "name": member_name,
        "role": member.role if member.role else UserRole.ORG_MEMBER,
        "org_id": user.org_id,
        "created_at": datetime.now(timezone.utc),
        "phone": member.phone,
        "first_name": first_name if first_name else None,
        "last_name": last_name if last_name else None
    }
    db_member = user_repo.create(member_data, hash_password(member.password))
    
    return db_user_to_pydantic(db_member)


def update_member_in_user_org(db: Session, user: User, member_id: str, member: OrgMemberCreate) -> User:
    """Update a member in the user's organization."""
    user_repo = UserRepository(db)
    
    if not user.org_id:
        raise HTTPException(status_code=400, detail="User is not part of an organization")
    
    if user.role not in [UserRole.ORG_OWNER, UserRole.ORG_MEMBER]:
        raise HTTPException(status_code=403, detail="Not authorized to update members")
    
    db_member = user_repo.get_by_id(member_id)
    if not db_member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    if db_member.org_id != user.org_id:
        raise HTTPException(status_code=403, detail="Member not in your organization")
    
    first_name = member.first_name or ''
    last_name = member.last_name or ''
    member_name = f"{first_name} {last_name}".strip() if first_name or last_name else member.name
    
    update_data = {
        "email": member.email,
        "name": member_name,
        "phone": member.phone,
        "role": member.role if member.role else db_member.role,
        "first_name": first_name if first_name else None,
        "last_name": last_name if last_name else None
    }
    
    if member.password:
        db_member.password_hash = hash_password(member.password)
    
    db_updated = user_repo.update(member_id, **update_data)
    
    return db_user_to_pydantic(db_updated)


def remove_member_from_user_org(db: Session, user: User, member_id: str) -> dict:
    """Remove a member from the user's organization."""
    user_repo = UserRepository(db)
    
    if not user.org_id:
        raise HTTPException(status_code=400, detail="User is not part of an organization")
    
    if user.role not in [UserRole.ORG_OWNER, UserRole.ORG_MEMBER]:
        raise HTTPException(status_code=403, detail="Not authorized to remove members")
    
    db_member = user_repo.get_by_id(member_id)
    if not db_member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    if db_member.org_id != user.org_id:
        raise HTTPException(status_code=403, detail="Member not in your organization")
    
    if db_member.role == UserRole.ORG_OWNER:
        raise HTTPException(status_code=400, detail="Cannot remove organization owner")
    
    user_repo.delete(member_id)
    
    return {"message": "Member removed successfully"}
