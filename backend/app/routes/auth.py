"""
Authentication routes - Using Firestore
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, field_validator, model_validator
from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
import bcrypt
import os
from app.config import settings
from app.services.firestore_service import FirestoreService

router = APIRouter()
security = HTTPBearer()
firestore_service = FirestoreService()

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    phone_number: str  # Made mandatory
    twitter_username: Optional[str] = None

class UserLogin(BaseModel):
    username: Optional[str] = None  # Can be username
    email: Optional[str] = None  # Allow email login
    password: str
    
    @model_validator(mode='after')
    def validate_username_or_email(self):
        """Ensure either username or email is provided"""
        if not self.username and not self.email:
            raise ValueError("Either username or email must be provided")
        return self

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

async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[dict]:
    """
    Get current authenticated user from Firestore (optional)
    Returns None if no token is provided (for anonymous users)
    """
    if credentials is None:
        return None
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None
    
    user = firestore_service.get_user_by_username(username)
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
        
        # Add phone_number and twitter_username
        user_data_dict['phone_number'] = user_data.phone_number
        if user_data.twitter_username:
            user_data_dict['twitter_username'] = user_data.twitter_username
        
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
    """Login user from Firestore - supports both username and email"""
    # Debug logging
    print(f"[DEBUG] Login attempt - username: {user_data.username}, email: {user_data.email}")
    
    # Try to find user by username or email
    # If username contains @, treat it as email (handles cases where frontend sends email as username)
    user = None
    login_identifier = None
    
    # Check if username is actually an email (contains @)
    if user_data.username and '@' in user_data.username:
        # Username field contains email, look it up as email
        user = firestore_service.get_user_by_email(user_data.username)
        login_identifier = user_data.username
        print(f"[DEBUG] Username field contains email, looking up by email: {user_data.username}, found: {user is not None}")
    elif user_data.email:
        # Email field is set, use it
        user = firestore_service.get_user_by_email(user_data.email)
        login_identifier = user_data.email
        print(f"[DEBUG] Looking up by email: {user_data.email}, found: {user is not None}")
    elif user_data.username:
        # Username field is set and doesn't contain @, use as username
        user = firestore_service.get_user_by_username(user_data.username)
        login_identifier = user_data.username
        print(f"[DEBUG] Looking up by username: {user_data.username}, found: {user is not None}")
    
    # Check if user exists
    if not user:
        print(f"[DEBUG] User not found for identifier: {login_identifier}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password - check both 'hashed_password' and 'password_hash' for compatibility
    stored_hash = user.get('hashed_password') or user.get('password_hash', '')
    if not stored_hash:
        print(f"[DEBUG] No password hash found for user: {user.get('username')}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    password_valid = verify_password(user_data.password, stored_hash)
    print(f"[DEBUG] Password verification result: {password_valid}")
    
    if not password_valid:
        print(f"[DEBUG] Password verification failed for user: {user.get('username')}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # If user has old 'password_hash' field, migrate it to 'hashed_password' for consistency
    if user.get('password_hash') and not user.get('hashed_password'):
        try:
            from app.services.firestore_service import FirestoreService
            firestore_service_temp = FirestoreService()
            user_id = user.get('id') or user.get('user_id')
            if user_id:
                # Get the actual document ID for update
                users_ref = firestore_service_temp.db.collection('users')
                user_doc = users_ref.document(user_id).get()
                if not user_doc.exists:
                    # Try to find by query
                    query = users_ref.where('username', '==', user.get('username')).limit(1).stream()
                    for doc in query:
                        user_id = doc.id
                        break
                
                if user_id:
                    firestore_service_temp.update_user(user_id, {
                        'hashed_password': user.get('password_hash'),
                        'password_hash': None  # Remove old field
                    })
                    print(f"[INFO] Migrated password hash for user: {user.get('username')}")
        except Exception as e:
            print(f"[WARNING] Failed to migrate password hash: {e}")
            # Continue with login even if migration fails
    
    # Use the username from the user document for the token (not the login identifier)
    username_for_token = user.get('username')
    if not username_for_token:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User data error: username not found"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": username_for_token}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return {
        "id": current_user.get('id'),
        "username": current_user.get('username'),
        "email": current_user.get('email'),
        "phone_number": current_user.get('phone_number'),
        "twitter_username": current_user.get('twitter_username'),
        "is_admin": current_user.get('is_admin', False),
        "is_sub_admin": current_user.get('is_sub_admin', False),
        "role": current_user.get('role'),
        "specialization": current_user.get('specialization'),
        "description": current_user.get('description'),
        "profile_image_url": current_user.get('profile_image_url'),
    }

class ProfileUpdateRequest(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    description: Optional[str] = None
    profile_image_url: Optional[str] = None
    phone_number: Optional[str] = None

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str

@router.post("/profile/upload-image")
async def upload_profile_image(
    image_file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload profile image for user"""
    try:
        user_id = current_user.get('id')
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID not found")
        
        # Validate image file
        allowed_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp']
        file_ext = image_file.filename.split('.')[-1].lower() if '.' in image_file.filename else ''
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join(settings.UPLOAD_DIR, 'profile_images')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file with user ID prefix
        file_path = os.path.join(
            upload_dir,
            f"{user_id}_{datetime.now().timestamp()}.{file_ext}"
        )
        
        with open(file_path, "wb") as buffer:
            content = await image_file.read()
            buffer.write(content)
        
        # Generate URL (in production, this would be a CDN or storage bucket URL)
        profile_image_url = f"/uploads/profile_images/{os.path.basename(file_path)}"
        
        # Update user profile with image URL
        firestore_service.update_user(user_id, {'profile_image_url': profile_image_url})
        
        return {
            "message": "Profile image uploaded successfully",
            "profile_image_url": profile_image_url
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Failed to upload profile image: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to upload profile image")

@router.put("/profile")
async def update_profile(
    profile_data: ProfileUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update user profile (username, email, description, profile image URL, phone number)"""
    try:
        user_id = current_user.get('id')
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID not found")
        
        updates = {}
        
        # Handle username update
        if profile_data.username is not None:
            # Check if username already exists (for another user)
            existing_user = firestore_service.get_user_by_username(profile_data.username)
            if existing_user:
                existing_user_id = existing_user.get('id')
                if existing_user_id and str(existing_user_id) != str(user_id):
                    raise HTTPException(status_code=400, detail="Username already exists")
            updates['username'] = profile_data.username
        
        # Handle email update
        if profile_data.email is not None:
            # Check if email already exists (for another user)
            existing_user = firestore_service.get_user_by_email(profile_data.email)
            if existing_user:
                existing_user_id = existing_user.get('id')
                if existing_user_id and str(existing_user_id) != str(user_id):
                    raise HTTPException(status_code=400, detail="Email already exists")
            updates['email'] = profile_data.email
        
        if profile_data.description is not None:
            updates['description'] = profile_data.description
        if profile_data.profile_image_url is not None:
            updates['profile_image_url'] = profile_data.profile_image_url
        if profile_data.phone_number is not None:
            updates['phone_number'] = profile_data.phone_number
        
        if updates:
            firestore_service.update_user(user_id, updates)
        
        # Return updated user
        updated_user = firestore_service.get_user_by_id(user_id)
        if updated_user:
            updated_user.pop('hashed_password', None)
            updated_user.pop('password_hash', None)
        
        return {
            "message": "Profile updated successfully",
            "user": updated_user
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Failed to update profile: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to update profile")

@router.post("/change-password")
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: dict = Depends(get_current_user)
):
    """Change user password - requires current password verification"""
    try:
        user_id = current_user.get('id')
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID not found")
        
        # Get current user data with password hash
        user = firestore_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Verify current password
        stored_hash = user.get('hashed_password') or user.get('password_hash', '')
        if not stored_hash:
            raise HTTPException(status_code=400, detail="Password not set for this user")
        
        password_valid = verify_password(password_data.current_password, stored_hash)
        if not password_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current password is incorrect"
            )
        
        # Validate new password (minimum length)
        if len(password_data.new_password) < 6:
            raise HTTPException(
                status_code=400,
                detail="New password must be at least 6 characters long"
            )
        
        # Hash new password and update
        new_hashed_password = get_password_hash(password_data.new_password)
        firestore_service.update_user(user_id, {
            'hashed_password': new_hashed_password
        })
        
        return {"message": "Password changed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Failed to change password: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to change password")

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

