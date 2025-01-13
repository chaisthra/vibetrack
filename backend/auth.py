import uuid
import bcrypt
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt  # Import PyJWT directly
import json

from .storage import load_users, save_users, get_user_by_username

# Security configurations
SECRET_KEY = "your-secret-key-here"  # In production, use a secure secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

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
    try:
        # Add debug logging
        print(f"Verifying password for length: {len(plain_password)}")
        
        # Ensure we're working with bytes
        if isinstance(hashed_password, str):
            hashed_password = hashed_password.encode('utf-8')
        
        plain_password_bytes = plain_password.encode('utf-8')
        
        # Add more debug logging
        print(f"Hashed password length: {len(hashed_password)}")
        print(f"Plain password bytes length: {len(plain_password_bytes)}")
        
        return bcrypt.checkpw(plain_password_bytes, hashed_password)
    except Exception as e:
        print(f"Password verification error: {str(e)}")
        print(f"Hashed password: {hashed_password[:10]}... (truncated)")
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    try:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        # Use PyJWT's encode method with explicit string encoding
        encoded_jwt = jwt.encode(
            to_encode,
            SECRET_KEY,
            algorithm=ALGORITHM
        )
        # PyJWT might return bytes in some versions, so ensure we return a string
        if isinstance(encoded_jwt, bytes):
            return encoded_jwt.decode('utf-8')
        return encoded_jwt
    except Exception as e:
        print(f"Token creation error: {str(e)}")  # Debug log
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create access token"
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

def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt"""
    try:
        # Generate salt and hash password
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        # Return hash as string
        return hashed.decode('utf-8')
    except Exception as e:
        print(f"Error hashing password: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not process password"
        )

def create_user(user_data: dict) -> dict:
    try:
        # Check if username already exists
        existing_user = get_user_by_username(user_data["username"])
        if existing_user:
            raise ValueError("Username already registered")
            
        # Hash the password
        hashed_password = get_password_hash(user_data["password"])
        
        # Create new user object
        new_user = {
            "username": user_data["username"],
            "email": user_data["email"],
            "hashed_password": hashed_password,
            "created_at": datetime.utcnow().isoformat(),
            "settings": {
                "theme": "dark",
                "notifications_enabled": True
            },
            "elevenlabs_key": None
        }
        
        if "full_name" in user_data:
            new_user["full_name"] = user_data["full_name"]
            
        # Load existing users and add new user
        users = load_users()
        if not isinstance(users, list):
            users = []
        users.append(new_user)
        
        # Save updated users list
        save_users(users)
        
        # Return user data without password
        user_response = new_user.copy()
        del user_response["hashed_password"]
        return user_response
        
    except ValueError as ve:
        print(f"User creation error: {str(ve)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        print(f"User creation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create user"
        )

def authenticate_user(username: str, password: str) -> Optional[dict]:
    try:
        print(f"\n=== Authentication attempt for user: {username} ===")
        
        # Get user data
        user = get_user_by_username(username)
        if not user:
            print("❌ User not found in database")
            return None
        
        print("✓ User found in database")
        print(f"User data: {json.dumps({k:v for k,v in user.items() if k != 'hashed_password'}, indent=2)}")
        
        # Verify password
        print("\nAttempting password verification...")
        if not verify_password(password, user["hashed_password"]):
            print("❌ Password verification failed")
            return None
        
        print("✓ Password verified successfully")
        
        # Update last login
        print("\nUpdating last login timestamp...")
        users = load_users()
        for u in users:
            if u["username"] == username:
                u["last_login"] = datetime.utcnow().isoformat()
                break
        save_users(users)
        print("✓ Last login updated")
        
        # Return user without hashed password
        user_response = user.copy()
        del user_response["hashed_password"]
        print("\n=== Authentication successful ===")
        return user_response
        
    except Exception as e:
        print(f"❌ Authentication error: {str(e)}")
        import traceback
        print(f"Stack trace:\n{traceback.format_exc()}")
        return None 