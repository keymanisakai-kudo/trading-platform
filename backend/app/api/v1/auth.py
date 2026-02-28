"""Auth API - DDD Style"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr

from app.api.v1.deps import get_current_user, get_db
from app.infrastructure.persistence.repositories import (
    SQLAlchemyUserRepository,
    SQLAlchemyWalletRepository,
)
from app.application.users.commands import (
    RegisterCommand,
    RegisterHandler,
    LoginCommand,
    LoginHandler,
    RefreshTokenCommand,
    RefreshTokenHandler,
)
from app.application.users.queries import (
    GetCurrentUserQuery,
    GetCurrentUserHandler,
)
from app.domain.user.aggregate import User


router = APIRouter(prefix="/auth", tags=["Authentication"])


# Request/Response Models
class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    is_verified: bool
    two_factor_enabled: bool


@router.post("/register", response_model=TokenResponse)
async def register(
    request: RegisterRequest,
    db=Depends(get_db),
):
    """Register a new user"""
    user_repo = SQLAlchemyUserRepository(db)
    wallet_repo = SQLAlchemyWalletRepository(db)
    
    handler = RegisterHandler(user_repo, wallet_repo)
    
    command = RegisterCommand(
        email=request.email,
        username=request.username,
        password=request.password,
    )
    
    result = await handler.handle(command)
    
    if result.user_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.message,
        )
    
    await db.commit()
    
    return TokenResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db=Depends(get_db),
):
    """Login with email and password"""
    user_repo = SQLAlchemyUserRepository(db)
    
    handler = LoginHandler(user_repo)
    
    command = LoginCommand(
        email=form_data.username,  # OAuth2 uses username field for email
        password=form_data.password,
    )
    
    result = await handler.handle(command)
    
    if result.user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result.message,
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return TokenResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str = Query(..., description="Refresh token"),
):
    """Refresh access token"""
    handler = RefreshTokenHandler()
    
    command = RefreshTokenCommand(refresh_token=refresh_token)
    
    result = await handler.handle(command)
    
    if not result.access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result.message,
        )
    
    return TokenResponse(
        access_token=result.access_token,
        refresh_token="",  # Don't return new refresh token
    )


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    """Get current user info"""
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        username=current_user.username,
        is_verified=current_user.is_verified,
        two_factor_enabled=current_user.two_factor_enabled,
    )
