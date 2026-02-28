"""Tests for User Aggregate"""
import pytest
from uuid import uuid4

from domain.user.aggregate import User


class TestUserCreate:
    """Test User creation"""

    def test_create_user(self):
        """Test creating a user"""
        user = User.create(
            email="test@example.com",
            username="testuser",
            password_hash="hashed_password",
        )

        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.password_hash == "hashed_password"
        assert user.is_active is True
        assert user.is_verified is False
        assert user.two_factor_enabled is False

    def test_create_user_emits_event(self):
        """Test user creation emits event"""
        user = User.create(
            email="test@example.com",
            username="testuser",
            password_hash="hashed_password",
        )

        events = user.pull_events()
        assert len(events) == 1
        assert events[0].__class__.__name__ == "UserRegisteredEvent"
        assert events[0].email == "test@example.com"


class TestUserVerify:
    """Test user verification"""

    def test_verify_user(self, sample_user):
        """Test verifying a user"""
        sample_user.verify()

        assert sample_user.is_verified is True

    def test_verify_already_verified(self, sample_user):
        """Test verifying an already verified user"""
        sample_user.verify()
        sample_user.verify()  # Should not raise

        assert sample_user.is_verified is True

    def test_verify_emits_event(self, sample_user):
        """Test verify emits event"""
        sample_user.verify()

        events = sample_user.pull_events()
        assert len(events) == 1
        assert events[0].__class__.__name__ == "UserVerifiedEvent"


class TestUser2FA:
    """Test two-factor authentication"""

    def test_enable_2fa(self, sample_user):
        """Test enabling 2FA"""
        sample_user.enable_2fa()

        assert sample_user.two_factor_enabled is True

    def test_disable_2fa(self, sample_user):
        """Test disabling 2FA"""
        sample_user.enable_2fa()
        sample_user.disable_2fa()

        assert sample_user.two_factor_enabled is False


class TestUserStatus:
    """Test user status changes"""

    def test_deactivate(self, sample_user):
        """Test deactivating user"""
        sample_user.deactivate()

        assert sample_user.is_active is False

    def test_activate(self, sample_user):
        """Test activating user"""
        sample_user.deactivate()
        sample_user.activate()

        assert sample_user.is_active is True


class TestUserProfile:
    """Test user profile updates"""

    def test_update_username(self, sample_user):
        """Test updating username"""
        sample_user.update_profile(username="newusername")

        assert sample_user.username == "newusername"

    def test_update_email(self, sample_user):
        """Test updating email"""
        sample_user.update_profile(email="new@example.com")

        assert sample_user.email == "new@example.com"

    def test_update_both(self, sample_user):
        """Test updating both fields"""
        sample_user.update_profile(
            username="newusername",
            email="new@example.com",
        )

        assert sample_user.username == "newusername"
        assert sample_user.email == "new@example.com"


class TestVersioning:
    """Test optimistic locking"""

    def test_version_increments(self, sample_user):
        """Test version increments on changes"""
        initial_version = sample_user.version
        
        sample_user.verify()
        
        assert sample_user.version == initial_version + 1

    def test_version_increments_on_profile_update(self, sample_user):
        """Test version increments on profile update"""
        initial_version = sample_user.version
        
        sample_user.update_profile(username="newusername")
        
        assert sample_user.version == initial_version + 1
