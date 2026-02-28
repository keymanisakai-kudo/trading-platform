"""User Domain - Repository Interface"""
from typing import Protocol, Optional
from uuid import UUID


class IUserRepository(Protocol):
    """User Repository Interface"""

    async def save(self, user) -> object:
        """Save or update user"""
        ...

    async def get_by_id(self, user_id: UUID) -> Optional[object]:
        """Get user by ID"""
        ...

    async def get_by_email(self, email: str) -> Optional[object]:
        """Get user by email"""
        ...

    async def get_by_username(self, username: str) -> Optional[object]:
        """Get user by username"""
        ...

    async def exists_by_email(self, email: str) -> bool:
        """Check if email exists"""
        ...

    async def exists_by_username(self, username: str) -> bool:
        """Check if username exists"""
        ...
