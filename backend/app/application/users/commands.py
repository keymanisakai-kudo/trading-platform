"""Application Layer - Users Commands"""
from dataclasses import dataclass
from uuid import UUID
from typing import Optional, TYPE_CHECKING

from domain.user.aggregate import User
from domain.user.repositories import IUserRepository
from domain.wallet.aggregate import Wallet
from domain.wallet.value_objects import Currency
from domain.wallet.repositories import IWalletRepository

if TYPE_CHECKING:
    pass


@dataclass
class RegisterCommand:
    """注册命令"""
    email: str
    username: str
    password: str


@dataclass
class RegisterResult:
    """注册结果"""
    user_id: Optional[UUID]
    access_token: str
    refresh_token: str
    message: str


class RegisterHandler:
    def __init__(
        self,
        user_repository: IUserRepository,
        wallet_repository: IWalletRepository,
    ):
        self.user_repository = user_repository
        self.wallet_repository = wallet_repository

    async def handle(self, command: RegisterCommand) -> RegisterResult:
        # 1. Check if email exists
        if await self.user_repository.exists_by_email(command.email):
            return RegisterResult(
                user_id=None,
                access_token="",
                refresh_token="",
                message="Email already registered",
            )

        # 2. Check if username exists
        if await self.user_repository.exists_by_username(command.username):
            return RegisterResult(
                user_id=None,
                access_token="",
                refresh_token="",
                message="Username already taken",
            )

        # 3. Hash password
        from app.core.security import get_password_hash
        password_hash = get_password_hash(command.password)

        # 4. Create user
        user = User.create(
            email=command.email,
            username=command.username,
            password_hash=password_hash,
        )

        # 5. Save user
        await self.user_repository.save(user)

        # 6. Create default wallet (USDT)
        wallet = Wallet.create(user_id=user.id, currency=Currency.USDT)
        await self.wallet_repository.save(wallet)

        # 7. Generate tokens
        from app.core.security import create_access_token, create_refresh_token
        access_token = create_access_token(str(user.id))
        refresh_token = create_refresh_token(str(user.id))

        return RegisterResult(
            user_id=user.id,
            access_token=access_token,
            refresh_token=refresh_token,
            message="User registered successfully",
        )


@dataclass
class LoginCommand:
    """登录命令"""
    email: str
    password: str


@dataclass
class LoginResult:
    """登录结果"""
    user_id: Optional[UUID]
    access_token: str
    refresh_token: str
    message: str


class LoginHandler:
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    async def handle(self, command: LoginCommand) -> LoginResult:
        # 1. Find user by email
        user = await self.user_repository.get_by_email(command.email)

        if not user:
            return LoginResult(
                user_id=None,
                access_token="",
                refresh_token="",
                message="Invalid email or password",
            )

        # 2. Verify password
        from app.core.security import verify_password
        if not verify_password(command.password, user.password_hash):
            return LoginResult(
                user_id=None,
                access_token="",
                refresh_token="",
                message="Invalid email or password",
            )

        # 3. Check if active
        if not user.is_active:
            return LoginResult(
                user_id=None,
                access_token="",
                refresh_token="",
                message="User account is disabled",
            )

        # 4. Generate tokens
        from app.core.security import create_access_token, create_refresh_token
        access_token = create_access_token(str(user.id))
        refresh_token = create_refresh_token(str(user.id))

        return LoginResult(
            user_id=user.id,
            access_token=access_token,
            refresh_token=refresh_token,
            message="Login successful",
        )


@dataclass
class RefreshTokenCommand:
    """刷新 Token 命令"""
    refresh_token: str


@dataclass
class RefreshTokenResult:
    """刷新结果"""
    access_token: str
    message: str


class RefreshTokenHandler:
    async def handle(self, command: RefreshTokenCommand) -> RefreshTokenResult:
        from app.core.security import decode_token, create_access_token
        
        # Decode refresh token
        payload = decode_token(command.refresh_token)
        if payload is None:
            return RefreshTokenResult(
                access_token="",
                message="Invalid refresh token",
            )
        
        token_type = payload.get("type")
        if token_type != "refresh":
            return RefreshTokenResult(
                access_token="",
                message="Invalid token type",
            )
        
        user_id = payload.get("sub")
        if user_id is None:
            return RefreshTokenResult(
                access_token="",
                message="Invalid token payload",
            )
        
        # Generate new access token
        access_token = create_access_token(user_id)
        
        return RefreshTokenResult(
            access_token=access_token,
            message="Token refreshed",
        )
