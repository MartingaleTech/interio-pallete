from fastapi import APIRouter, Depends
from typing import List
from src.models import User, OrgMemberCreate
from src.services import (
    get_members_for_user_org, add_member_to_user_org,
    update_member_in_user_org, remove_member_from_user_org
)
from src.dependencies import get_current_user

router = APIRouter(prefix="/api/organizations", tags=["organizations"])


@router.get("/members", response_model=List[User])
async def get_organization_members(user: User = Depends(get_current_user)):
    """Get all members of the current user's organization."""
    return get_members_for_user_org(user)


@router.post("/members", response_model=User)
async def add_organization_member(member: OrgMemberCreate, user: User = Depends(get_current_user)):
    """Add a member to the current user's organization."""
    return add_member_to_user_org(user, member)


@router.put("/members/{member_id}", response_model=User)
async def update_organization_member(member_id: str, member: OrgMemberCreate, user: User = Depends(get_current_user)):
    """Update a member in the current user's organization."""
    return update_member_in_user_org(user, member_id, member)


@router.delete("/members/{member_id}")
async def remove_organization_member(member_id: str, user: User = Depends(get_current_user)):
    """Remove a member from the current user's organization."""
    return remove_member_from_user_org(user, member_id)
