import uuid
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict
from pydantic import BaseModel, EmailStr, Field
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt  # Import PyJWT directly
import json
import os

from .storage import load_users, save_users, get_user_by_username
from jose import JWTError, jwt
from passlib.context import CryptContext

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=100)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    username: str
    password: str

class UserProfile(UserBase):
    id: str
    created_at: datetime
    last_login: Optional[datetime] = None

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    print(f"\n[Auth] Verifying password...")
    try:
        result = pwd_context.verify(plain_password, hashed_password)
        print(f"[Auth] Password verification {'successful' if result else 'failed'}")
        return result
    except Exception as e:
        print(f"[Auth] Error verifying password: {str(e)}")
        return False

def get_password_hash(password: str) -> str:
    """Generate password hash"""
    print(f"\n[Auth] Generating password hash...")
    try:
        hashed = pwd_context.hash(password)
        print(f"[Auth] Password hash generated successfully")
        return hashed
    except Exception as e:
        print(f"[Auth] Error generating password hash: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating password hash"
        )

def create_access_token(data: dict) -> str:
    """Create JWT access token"""
    print(f"\n[Auth] Creating access token for user: {data.get('sub')}")
    try:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        print(f"[Auth] Access token created successfully")
        return token
    except Exception as e:
        print(f"[Auth] Error creating access token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating access token"
        )

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = {"username": username}
    except jwt.InvalidTokenError as e:
        print(f"JWT decode error: {str(e)}")  # Debug log
        raise credentials_exception
        
    user = get_user_by_username(username)
    if user is None:
        raise credentials_exception
        
    # Return user without hashed password
    user_response = user.copy()
    del user_response["hashed_password"]
    return user_response

def authenticate_user(username: str, password: str) -> Optional[Dict]:
    """Authenticate a user"""
    print(f"\n[Auth] Attempting to authenticate user: {username}")
    try:
        user = get_user_by_username(username)
        if not user:
            print(f"[Auth] User not found: {username}")
            return None
        
        print(f"[Auth] User found, verifying password...")
        if not verify_password(password, user["hashed_password"]):
            print(f"[Auth] Invalid password for user: {username}")
            return None
        
        print(f"[Auth] Authentication successful for user: {username}")
        return user
    except Exception as e:
        print(f"[Auth] Error during authentication: {str(e)}")
        import traceback
        print(f"[Auth] Stack trace:\n{traceback.format_exc()}")
        return None

def create_user(username: str, email: str, password: str) -> Dict:
    """Create a new user"""
    print(f"\n[Auth] Attempting to create new user: {username}")
    try:
        # Check if username already exists
        existing_user = get_user_by_username(username)
        if existing_user:
            print(f"[Auth] Username already exists: {username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # Create new user
        users = load_users()
        hashed_password = get_password_hash(password)
        new_user = {
            "username": username,
            "email": email,
            "hashed_password": hashed_password,
            "created_at": datetime.utcnow().isoformat()
        }
        users.append(new_user)
        save_users(users)
        print(f"[Auth] User created successfully: {username}")
        return new_user
    except HTTPException as he:
        print(f"[Auth] HTTP Exception during user creation: {str(he.detail)}")
        raise he
    except Exception as e:
        print(f"[Auth] Error creating user: {str(e)}")
        import traceback
        print(f"[Auth] Stack trace:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user"
        ) 