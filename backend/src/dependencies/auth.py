from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.models import User, UserRole
from src.database import get_users_db, get_tokens_db

security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get the current authenticated user from the token."""
    token = credentials.credentials
    tokens_db = get_tokens_db()
    users_db = get_users_db()
    
    if token not in tokens_db:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user_id = tokens_db[token]
    if user_id not in users_db:
        raise HTTPException(status_code=401, detail="User not found")
    
    return users_db[user_id]


async def require_admin(user: User = Depends(get_current_user)) -> User:
    """Require the current user to be an admin."""
    if user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


async def require_org_access(user: User = Depends(get_current_user)) -> User:
    """Require the current user to have organization access."""
    if user.role not in [UserRole.ORG_OWNER, UserRole.ORG_MEMBER]:
        raise HTTPException(status_code=403, detail="Organization access required")
    return user
