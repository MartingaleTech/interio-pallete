from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from src.models import User, UserRole
from src.config.database import get_db
from src.repositories import UserRepository, TokenRepository
from src.utils.mappers import db_user_to_pydantic

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get the current authenticated user from the token."""
    token = credentials.credentials
    token_repo = TokenRepository(db)
    user_repo = UserRepository(db)
    
    user_id = token_repo.get_user_id(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    db_user = user_repo.get_by_id(user_id)
    if not db_user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return db_user_to_pydantic(db_user)


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


async def get_current_user_ws(token: str, db: Session):
    """Get the current authenticated user from token for WebSocket connections."""
    token_repo = TokenRepository(db)
    user_repo = UserRepository(db)
    
    user_id = token_repo.get_user_id(token)
    if not user_id:
        return None
    
    db_user = user_repo.get_by_id(user_id)
    if not db_user:
        return None
    
    return db_user_to_pydantic(db_user)
