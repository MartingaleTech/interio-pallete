from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.orm import Session
from src.models import User, OrgMemberCreate, SupportTicket, SupportTicketCreate
from src.services import organization_service_new, admin_service_new
from src.dependencies.auth_new import get_current_user
from src.config.database import get_db

router = APIRouter(prefix="/api/organizations", tags=["organizations"])


@router.get("/members", response_model=List[User])
async def get_organization_members(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get all members of the current user's organization."""
    return organization_service_new.get_members_for_user_org(db, user)


@router.post("/members", response_model=User)
async def add_organization_member(
    member: OrgMemberCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Add a member to the current user's organization."""
    return organization_service_new.add_member_to_user_org(db, user, member)


@router.put("/members/{member_id}", response_model=User)
async def update_organization_member(
    member_id: str,
    member: OrgMemberCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Update a member in the current user's organization."""
    return organization_service_new.update_member_in_user_org(db, user, member_id, member)


@router.delete("/members/{member_id}")
async def remove_organization_member(
    member_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Remove a member from the current user's organization."""
    return organization_service_new.remove_member_from_user_org(db, user, member_id)


@router.post("/support-tickets", response_model=SupportTicket)
async def create_support_ticket(
    ticket: SupportTicketCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Create a support ticket for the organization."""
    if not user.org_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="User is not part of an organization")
    
    return admin_service_new.create_support_ticket(db, user.org_id, user.id, ticket)


@router.get("/support-tickets", response_model=List[SupportTicket])
async def get_organization_support_tickets(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get support tickets for the organization."""
    if not user.org_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="User is not part of an organization")
    
    return admin_service_new.get_support_tickets_for_org(db, user.org_id)
