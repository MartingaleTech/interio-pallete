from datetime import datetime, timedelta
from typing import List, Optional
import uuid
from fastapi import HTTPException
from src.models import (
    Organization, OrganizationCreate, OrganizationUpdate,
    User, UserRole, OrgMemberCreate, SubscriptionStatus
)
from src.database import (
    get_organizations_db, get_users_db, get_passwords_db,
    get_projects_db
)
from src.utils import hash_password


def create_organization(org: OrganizationCreate) -> Organization:
    """Create a new organization with an owner user."""
    organizations_db = get_organizations_db()
    users_db = get_users_db()
    passwords_db = get_passwords_db()
    
    org_id = str(uuid.uuid4())
    owner_id = str(uuid.uuid4())
    
    owner_user = User(
        id=owner_id,
        email=org.owner_email,
        name=org.owner_name,
        role=UserRole.ORG_OWNER,
        org_id=org_id,
        created_at=datetime.now().isoformat(),
        phone=org.owner_phone
    )
    users_db[owner_id] = owner_user
    passwords_db[owner_id] = hash_password(org.owner_password)
    
    subscription_start = datetime.now()
    subscription_end = subscription_start + timedelta(days=365)
    
    new_org = Organization(
        id=org_id,
        name=org.name,
        email=org.email,
        phone=org.phone,
        address=org.address,
        city=org.city,
        state=org.state,
        pincode=org.pincode,
        owner_id=owner_id,
        subscription_status=SubscriptionStatus.ACTIVE,
        subscription_plan=org.subscription_plan,
        subscription_start=subscription_start.isoformat(),
        subscription_end=subscription_end.isoformat(),
        created_at=datetime.now().isoformat()
    )
    organizations_db[org_id] = new_org
    
    return new_org


def get_all_organizations() -> List[Organization]:
    """Get all organizations."""
    organizations_db = get_organizations_db()
    return list(organizations_db.values())


def get_organization_by_id(org_id: str) -> Organization:
    """Get an organization by ID."""
    organizations_db = get_organizations_db()
    if org_id not in organizations_db:
        raise HTTPException(status_code=404, detail="Organization not found")
    return organizations_db[org_id]


def update_organization(org_id: str, updates: OrganizationUpdate) -> Organization:
    """Update an organization."""
    organizations_db = get_organizations_db()
    if org_id not in organizations_db:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    org = organizations_db[org_id]
    update_data = updates.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(org, field, value)
    
    organizations_db[org_id] = org
    return org


def delete_organization(org_id: str) -> dict:
    """Delete an organization and all related data."""
    organizations_db = get_organizations_db()
    users_db = get_users_db()
    passwords_db = get_passwords_db()
    projects_db = get_projects_db()
    
    if org_id not in organizations_db:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    del organizations_db[org_id]
    
    for user_id, user in list(users_db.items()):
        if user.org_id == org_id:
            del users_db[user_id]
            if user_id in passwords_db:
                del passwords_db[user_id]
    
    for project_id, project in list(projects_db.items()):
        if project.org_id == org_id:
            del projects_db[project_id]
    
    return {"message": "Organization deleted successfully"}


def get_organization_members(org_id: str) -> List[User]:
    """Get all members of an organization."""
    organizations_db = get_organizations_db()
    users_db = get_users_db()
    
    if org_id not in organizations_db:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    members = [u for u in users_db.values() if u.org_id == org_id]
    return members


def add_organization_member(org_id: str, member: OrgMemberCreate) -> User:
    """Add a member to an organization."""
    organizations_db = get_organizations_db()
    users_db = get_users_db()
    passwords_db = get_passwords_db()
    
    if org_id not in organizations_db:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    member_id = str(uuid.uuid4())
    new_member = User(
        id=member_id,
        email=member.email,
        name=member.name,
        role=UserRole.ORG_MEMBER,
        org_id=org_id,
        created_at=datetime.now().isoformat(),
        phone=member.phone
    )
    users_db[member_id] = new_member
    passwords_db[member_id] = hash_password(member.password)
    
    return new_member


def remove_organization_member(org_id: str, user_id: str) -> dict:
    """Remove a member from an organization."""
    organizations_db = get_organizations_db()
    users_db = get_users_db()
    passwords_db = get_passwords_db()
    
    if org_id not in organizations_db:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = users_db[user_id]
    if user.org_id != org_id:
        raise HTTPException(status_code=400, detail="User is not a member of this organization")
    
    if user.role == UserRole.ORG_OWNER:
        raise HTTPException(status_code=400, detail="Cannot remove organization owner")
    
    del users_db[user_id]
    if user_id in passwords_db:
        del passwords_db[user_id]
    
    return {"message": "Member removed successfully"}


def get_members_for_user_org(user: User) -> List[User]:
    """Get members for the user's organization."""
    users_db = get_users_db()
    
    if not user.org_id:
        raise HTTPException(status_code=400, detail="User is not part of an organization")
    
    members = [u for u in users_db.values() if u.org_id == user.org_id]
    return members


def add_member_to_user_org(user: User, member: OrgMemberCreate) -> User:
    """Add a member to the user's organization."""
    users_db = get_users_db()
    passwords_db = get_passwords_db()
    
    if not user.org_id:
        raise HTTPException(status_code=400, detail="User is not part of an organization")
    
    if user.role not in [UserRole.ORG_OWNER, UserRole.ORG_MEMBER]:
        raise HTTPException(status_code=403, detail="Not authorized to add members")
    
    for existing_user in users_db.values():
        if existing_user.email == member.email:
            raise HTTPException(status_code=400, detail="Email already exists")
    
    member_id = str(uuid.uuid4())
    first_name = member.first_name or ''
    last_name = member.last_name or ''
    member_name = f"{first_name} {last_name}".strip() if first_name or last_name else member.name
    
    new_member = User(
        id=member_id,
        email=member.email,
        name=member_name,
        role=member.role if member.role else UserRole.ORG_MEMBER,
        org_id=user.org_id,
        created_at=datetime.now().isoformat(),
        phone=member.phone,
        first_name=first_name if first_name else None,
        last_name=last_name if last_name else None
    )
    users_db[member_id] = new_member
    passwords_db[member_id] = hash_password(member.password)
    
    return new_member


def update_member_in_user_org(user: User, member_id: str, member: OrgMemberCreate) -> User:
    """Update a member in the user's organization."""
    users_db = get_users_db()
    passwords_db = get_passwords_db()
    
    if not user.org_id:
        raise HTTPException(status_code=400, detail="User is not part of an organization")
    
    if user.role not in [UserRole.ORG_OWNER, UserRole.ORG_MEMBER]:
        raise HTTPException(status_code=403, detail="Not authorized to update members")
    
    if member_id not in users_db:
        raise HTTPException(status_code=404, detail="Member not found")
    
    existing_member = users_db[member_id]
    if existing_member.org_id != user.org_id:
        raise HTTPException(status_code=403, detail="Member not in your organization")
    
    first_name = member.first_name or ''
    last_name = member.last_name or ''
    member_name = f"{first_name} {last_name}".strip() if first_name or last_name else member.name
    
    existing_member.email = member.email
    existing_member.name = member_name
    existing_member.phone = member.phone
    existing_member.role = member.role if member.role else existing_member.role
    existing_member.first_name = first_name if first_name else None
    existing_member.last_name = last_name if last_name else None
    
    if member.password:
        passwords_db[member_id] = hash_password(member.password)
    
    return existing_member


def remove_member_from_user_org(user: User, member_id: str) -> dict:
    """Remove a member from the user's organization."""
    users_db = get_users_db()
    passwords_db = get_passwords_db()
    
    if not user.org_id:
        raise HTTPException(status_code=400, detail="User is not part of an organization")
    
    if user.role not in [UserRole.ORG_OWNER, UserRole.ORG_MEMBER]:
        raise HTTPException(status_code=403, detail="Not authorized to remove members")
    
    if member_id not in users_db:
        raise HTTPException(status_code=404, detail="Member not found")
    
    member = users_db[member_id]
    if member.org_id != user.org_id:
        raise HTTPException(status_code=403, detail="Member not in your organization")
    
    if member.role == UserRole.ORG_OWNER:
        raise HTTPException(status_code=400, detail="Cannot remove organization owner")
    
    del users_db[member_id]
    if member_id in passwords_db:
        del passwords_db[member_id]
    
    return {"message": "Member removed successfully"}
