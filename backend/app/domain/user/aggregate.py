"""User Domain - User Aggregate"""
from datetime import datetime
from uuid import UUID, uuid4
from dataclasses import field, dataclass
from typing import List

from domain.user.events import UserRegisteredEvent, UserVerifiedEvent


@dataclass
class User:
    """User Aggregate Root"""
    id: UUID = field(default_factory=uuid4)
    email: str = field(default=None)
    username: str = field(default=None)
    password_hash: str = field(default=None)
    is_active: bool = True
    is_verified: bool = False
    two_factor_enabled: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    version: int = 1

    _events: List = field(default_factory=list, repr=False)

    # --- Factory ---

    @classmethod
    def create(cls, email: str, username: str, password_hash: str) -> "User":
        """Create a new user"""
        user = User(
            email=email,
            username=username,
            password_hash=password_hash,
        )
        user._events.append(UserRegisteredEvent(
            user_id=user.id,
            email=email,
        ))
        return user

    # --- Commands ---

    def verify(self) -> None:
        """Verify user email"""
        if self.is_verified:
            return

        self.is_verified = True
        self.updated_at = datetime.utcnow()
        self.version += 1
        self._events.append(UserVerifiedEvent(user_id=self.id))

    def enable_2fa(self) -> None:
        """Enable two-factor authentication"""
        self.two_factor_enabled = True
        self.updated_at = datetime.utcnow()
        self.version += 1

    def disable_2fa(self) -> None:
        """Disable two-factor authentication"""
        self.two_factor_enabled = False
        self.updated_at = datetime.utcnow()
        self.version += 1

    def deactivate(self) -> None:
        """Deactivate user account"""
        self.is_active = False
        self.updated_at = datetime.utcnow()
        self.version += 1

    def activate(self) -> None:
        """Activate user account"""
        self.is_active = True
        self.updated_at = datetime.utcnow()
        self.version += 1

    def update_profile(self, username: str = None, email: str = None) -> None:
        """Update user profile"""
        if username:
            self.username = username
        if email:
            self.email = email
        self.updated_at = datetime.utcnow()
        self.version += 1

    # --- Events ---

    def pull_events(self) -> List:
        events = self._events.copy()
        self._events.clear()
        return events
