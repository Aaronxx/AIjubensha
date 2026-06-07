"""Authentication service."""
from datetime import datetime, timedelta
from typing import Optional
from uuid import uuid4
import hashlib

from jose import jwt, JWTError

try:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False

from ..core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from ..models.user import UserCreate, UserLogin, UserInDB, Token


def _fallback_hash(password: str) -> str:
    """Fallback hash using SHA256 (for testing only, not production)."""
    return hashlib.sha256(f"{password}{SECRET_KEY}".encode()).hexdigest()


class AuthService:
    """Handles user authentication and token management."""

    def __init__(self):
        # In-memory user store for MVP (replace with database in production)
        self._users: dict[str, UserInDB] = {}
        self._email_index: dict[str, str] = {}  # email -> user_id

    def _hash_password(self, password: str) -> str:
        """Hash a password."""
        if BCRYPT_AVAILABLE:
            try:
                return pwd_context.hash(password)
            except Exception:
                pass
        return _fallback_hash(password)

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        if BCRYPT_AVAILABLE and hashed_password.startswith("$"):
            try:
                return pwd_context.verify(plain_password, hashed_password)
            except Exception:
                pass
        # Fallback verification
        return _fallback_hash(plain_password) == hashed_password

    def create_access_token(self, user_id: str) -> str:
        """Create a JWT access token."""
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {
            "sub": user_id,
            "exp": expire,
            "iat": datetime.utcnow()
        }
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    def verify_token(self, token: str) -> Optional[str]:
        """Verify a JWT token and return user_id."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id is None:
                return None
            return user_id
        except JWTError:
            return None

    async def register(self, user_data: UserCreate) -> dict:
        """Register a new user."""
        # Check if email already exists
        if user_data.email in self._email_index:
            return {
                "success": False,
                "error": "Email already registered"
            }

        # Check if username already exists
        for user in self._users.values():
            if user.username == user_data.username:
                return {
                    "success": False,
                    "error": "Username already taken"
                }

        # Validate password strength
        if len(user_data.password) < 6:
            return {
                "success": False,
                "error": "Password must be at least 6 characters"
            }

        # Create new user
        user_id = str(uuid4())
        now = datetime.utcnow()

        user = UserInDB(
            id=user_id,
            username=user_data.username,
            email=user_data.email,
            hashed_password=self._hash_password(user_data.password),
            nickname=user_data.nickname or user_data.username,
            is_active=True,
            is_vip=False,
            stars=0,
            created_at=now,
            updated_at=now
        )

        # Store user
        self._users[user_id] = user
        self._email_index[user.email] = user_id

        return {
            "success": True,
            "user_id": user_id,
            "username": user.username,
            "email": user.email,
            "nickname": user.nickname,
            "created_at": user.created_at.isoformat()
        }

    async def login(self, login_data: UserLogin) -> dict:
        """Authenticate a user and return token."""
        # Find user by email
        user_id = self._email_index.get(login_data.email)
        if not user_id:
            return {
                "success": False,
                "error": "User not found"
            }

        user = self._users.get(user_id)
        if not user:
            return {
                "success": False,
                "error": "User not found"
            }

        # Verify password
        if not self._verify_password(login_data.password, user.hashed_password):
            return {
                "success": False,
                "error": "Invalid password"
            }

        # Create token
        access_token = self.create_access_token(user.id)

        return {
            "success": True,
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "nickname": user.nickname,
                "is_vip": user.is_vip,
                "stars": user.stars
            }
        }

    async def get_user(self, user_id: str) -> Optional[UserInDB]:
        """Get user by ID."""
        return self._users.get(user_id)

    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """Get user by email."""
        user_id = self._email_index.get(email)
        if user_id:
            return self._users.get(user_id)
        return None


# Singleton instance
auth_service = AuthService()
