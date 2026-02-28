"""Integration Tests for Auth API"""
import pytest
from decimal import Decimal
from uuid import uuid4
from unittest.mock import AsyncMock, patch

from domain.user.aggregate import User


class TestRegisterHandler:
    """Test RegisterHandler"""

    @pytest.mark.asyncio
    async def test_register_success(self):
        """Test successful registration"""
        from application.users.commands import RegisterCommand, RegisterHandler

        user_id = uuid4()
        
        # Mock repositories
        mock_user_repo = AsyncMock()
        mock_user_repo.exists_by_email = AsyncMock(return_value=False)
        mock_user_repo.exists_by_username = AsyncMock(return_value=False)
        mock_user_repo.save = AsyncMock()

        mock_wallet_repo = AsyncMock()
        mock_wallet_repo.save = AsyncMock()

        handler = RegisterHandler(mock_user_repo, mock_wallet_repo)

        command = RegisterCommand(
            email="newuser@example.com",
            username="newuser",
            password="password123",
        )

        with patch('application.users.commands.get_password_hash', return_value="hashed"):
            with patch('application.users.commands.create_access_token', return_value="access_token"):
                with patch('application.users.commands.create_refresh_token', return_value="refresh_token"):
                    result = await handler.handle(command)

        assert result.user_id is not None
        assert result.access_token == "access_token"
        assert result.refresh_token == "refresh_token"
        assert "success" in result.message.lower()

    @pytest.mark.asyncio
    async def test_register_email_exists(self):
        """Test registration with existing email"""
        from application.users.commands import RegisterCommand, RegisterHandler

        mock_user_repo = AsyncMock()
        mock_user_repo.exists_by_email = AsyncMock(return_value=True)

        mock_wallet_repo = AsyncMock()

        handler = RegisterHandler(mock_user_repo, mock_wallet_repo)

        command = RegisterCommand(
            email="existing@example.com",
            username="newuser",
            password="password123",
        )

        result = await handler.handle(command)

        assert result.user_id is None
        assert "email" in result.message.lower()

    @pytest.mark.asyncio
    async def test_register_username_exists(self):
        """Test registration with existing username"""
        from application.users.commands import RegisterCommand, RegisterHandler

        mock_user_repo = AsyncMock()
        mock_user_repo.exists_by_email = AsyncMock(return_value=False)
        mock_user_repo.exists_by_username = AsyncMock(return_value=True)

        mock_wallet_repo = AsyncMock()

        handler = RegisterHandler(mock_user_repo, mock_wallet_repo)

        command = RegisterCommand(
            email="new@example.com",
            username="existinguser",
            password="password123",
        )

        result = await handler.handle(command)

        assert result.user_id is None
        assert "username" in result.message.lower()


class TestLoginHandler:
    """Test LoginHandler"""

    @pytest.mark.asyncio
    async def test_login_success(self):
        """Test successful login"""
        from application.users.commands import LoginCommand, LoginHandler

        user_id = uuid4()
        user = User(
            id=user_id,
            email="test@example.com",
            username="testuser",
            password_hash="hashed_password",
            is_active=True,
        )

        mock_user_repo = AsyncMock()
        mock_user_repo.get_by_email = AsyncMock(return_value=user)

        handler = LoginHandler(mock_user_repo)

        command = LoginCommand(
            email="test@example.com",
            password="correct_password",
        )

        with patch('application.users.commands.verify_password', return_value=True):
            with patch('application.users.commands.create_access_token', return_value="access_token"):
                with patch('application.users.commands.create_refresh_token', return_value="refresh_token"):
                    result = await handler.handle(command)

        assert result.user_id == user_id
        assert result.access_token == "access_token"
        assert "success" in result.message.lower()

    @pytest.mark.asyncio
    async def test_login_invalid_email(self):
        """Test login with invalid email"""
        from application.users.commands import LoginCommand, LoginHandler

        mock_user_repo = AsyncMock()
        mock_user_repo.get_by_email = AsyncMock(return_value=None)

        handler = LoginHandler(mock_user_repo)

        command = LoginCommand(
            email="wrong@example.com",
            password="password",
        )

        result = await handler.handle(command)

        assert result.user_id is None
        assert "invalid" in result.message.lower()

    @pytest.mark.asyncio
    async def test_login_invalid_password(self):
        """Test login with invalid password"""
        from application.users.commands import LoginCommand, LoginHandler

        user = User(
            id=uuid4(),
            email="test@example.com",
            username="testuser",
            password_hash="hashed_password",
            is_active=True,
        )

        mock_user_repo = AsyncMock()
        mock_user_repo.get_by_email = AsyncMock(return_value=user)

        handler = LoginHandler(mock_user_repo)

        command = LoginCommand(
            email="test@example.com",
            password="wrong_password",
        )

        with patch('application.users.commands.verify_password', return_value=False):
            result = await handler.handle(command)

        assert result.user_id is None
        assert "invalid" in result.message.lower()

    @pytest.mark.asyncio
    async def test_login_inactive_user(self):
        """Test login with inactive user"""
        from application.users.commands import LoginCommand, LoginHandler

        user = User(
            id=uuid4(),
            email="test@example.com",
            username="testuser",
            password_hash="hashed_password",
            is_active=False,  # Inactive
        )

        mock_user_repo = AsyncMock()
        mock_user_repo.get_by_email = AsyncMock(return_value=user)

        handler = LoginHandler(mock_user_repo)

        command = LoginCommand(
            email="test@example.com",
            password="password",
        )

        with patch('application.users.commands.verify_password', return_value=True):
            result = await handler.handle(command)

        assert result.user_id is None
        assert "disabled" in result.message.lower()


class TestGetCurrentUserHandler:
    """Test GetCurrentUserHandler"""

    @pytest.mark.asyncio
    async def test_get_current_user_success(self):
        """Test getting current user"""
        from application.users.queries import GetCurrentUserQuery, GetCurrentUserHandler

        user_id = uuid4()
        user = User(
            id=user_id,
            email="test@example.com",
            username="testuser",
            password_hash="hashed",
            is_verified=True,
            two_factor_enabled=False,
        )

        mock_user_repo = AsyncMock()
        mock_user_repo.get_by_id = AsyncMock(return_value=user)

        handler = GetCurrentUserHandler(mock_user_repo)

        query = GetCurrentUserQuery(user_id=user_id)

        result = await handler.handle(query)

        assert result.user_id == user_id
        assert result.email == "test@example.com"
        assert result.username == "testuser"
        assert result.is_verified is True

    @pytest.mark.asyncio
    async def test_get_current_user_not_found(self):
        """Test getting non-existent user"""
        from application.users.queries import GetCurrentUserQuery, GetCurrentUserHandler

        mock_user_repo = AsyncMock()
        mock_user_repo.get_by_id = AsyncMock(return_value=None)

        handler = GetCurrentUserHandler(mock_user_repo)

        query = GetCurrentUserQuery(user_id=uuid4())

        result = await handler.handle(query)

        assert result.user_id is None
        assert "not found" in result.message.lower()


class TestRefreshTokenHandler:
    """Test RefreshTokenHandler"""

    @pytest.mark.asyncio
    async def test_refresh_token_success(self):
        """Test successful token refresh"""
        from application.users.commands import RefreshTokenCommand, RefreshTokenHandler

        handler = RefreshTokenHandler()

        command = RefreshTokenCommand(
            refresh_token="valid_refresh_token",
        )

        with patch('application.users.commands.decode_token') as mock_decode:
            mock_decode.return_value = {
                "sub": str(uuid4()),
                "type": "refresh",
            }
            
            with patch('application.users.commands.create_access_token', return_value="new_access_token"):
                result = await handler.handle(command)

        assert result.access_token == "new_access_token"
        assert "refreshed" in result.message.lower()

    @pytest.mark.asyncio
    async def test_refresh_token_invalid(self):
        """Test refresh with invalid token"""
        from application.users.commands import RefreshTokenCommand, RefreshTokenHandler

        handler = RefreshTokenHandler()

        command = RefreshTokenCommand(
            refresh_token="invalid_token",
        )

        with patch('application.users.commands.decode_token', return_value=None):
            result = await handler.handle(command)

        assert result.access_token == ""
        assert "invalid" in result.message.lower()
