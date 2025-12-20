"""
Authentication routes - Using Firestore
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
import bcrypt
from app.config import settings
from app.services.firestore_service import FirestoreService

router = APIRouter()
security = HTTPBearer()
firestore_service = FirestoreService()

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    phone_number: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password using bcrypt"""
    try:
        password_bytes = plain_password.encode('utf-8')
        # Bcrypt has 72-byte limit, truncate if necessary
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
        return bcrypt.checkpw(password_bytes, hashed_password.encode('utf-8'))
    except Exception as e:
        print(f"[ERROR] Password verification failed: {e}")
        return False

def get_password_hash(password: str) -> str:
    """Hash password using bcrypt"""
    password_bytes = password.encode('utf-8')
    # Bcrypt has 72-byte limit, truncate if necessary
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    # Generate salt and hash
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get current authenticated user from Firestore"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = firestore_service.get_user_by_username(username)
    if user is None:
        raise credentials_exception
    return user

@router.post("/register", response_model=Token)
async def register(user_data: UserRegister):
    """Register new user in Firestore"""
    try:
        # Check if user exists
        if firestore_service.get_user_by_username(user_data.username):
            raise HTTPException(status_code=400, detail="Username already registered")
        if firestore_service.get_user_by_email(user_data.email):
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        user_data_dict = {
            'username': user_data.username,
            'email': user_data.email,
            'hashed_password': hashed_password,
            'is_active': True,
            'is_admin': False
        }
        
        # Only add phone_number if provided
        if user_data.phone_number:
            user_data_dict['phone_number'] = user_data.phone_number
        
        user_id = firestore_service.create_user(user_data_dict)
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_data.username}, expires_delta=access_token_expires
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"[ERROR] Registration failed: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    """Login user from Firestore"""
    user = firestore_service.get_user_by_username(user_data.username)
    if not user or not verify_password(user_data.password, user.get('hashed_password', '')):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_data.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return {
        "id": current_user.get('id'),
        "username": current_user.get('username'),
        "email": current_user.get('email'),
        "is_admin": current_user.get('is_admin', False)
    }

class FCMTokenUpdate(BaseModel):
    fcm_token: str

@router.post("/fcm-token")
async def update_fcm_token(
    token_data: FCMTokenUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update user's FCM token for push notifications in Firestore"""
    try:
        user_id = current_user.get('id')
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID not found")
        
        # Update FCM token in Firestore
        firestore_service.update_user(user_id, {
            'fcm_token': token_data.fcm_token
        })
        
        # Also update real-time data
        from app.services.firebase_service import update_user_realtime_data
        update_user_realtime_data(user_id, {
            'fcm_token': token_data.fcm_token
        })
        
        return {"message": "FCM token updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update FCM token: {str(e)}")

