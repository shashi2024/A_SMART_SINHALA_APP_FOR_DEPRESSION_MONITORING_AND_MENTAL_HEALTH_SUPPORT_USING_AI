"""
Script to create a new app user in Firestore with email, password, username, and mobile number
"""
from app.services.firebase_service import initialize_firebase
from app.services.firestore_service import FirestoreService
import bcrypt

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

def create_app_user():
    """Create a new app user with all fields"""
    print("=" * 60)
    print("Create New App User")
    print("=" * 60)
    
    # Initialize Firebase
    try:
        initialize_firebase()
        print("[OK] Firebase initialized")
    except Exception as e:
        print(f"[ERROR] Failed to initialize Firebase: {e}")
        return
    
    # Initialize Firestore service
    firestore_service = FirestoreService()
    
    # User details - matching your login attempt
    username = 'testnew'
    email = 'testnew@test.com'
    password = 'testnew1234'
    phone_number = '+94771234567'  # Sri Lankan format example
    
    print(f"\n[INFO] Creating user with the following details:")
    print(f"  Username: {username}")
    print(f"  Email: {email}")
    print(f"  Password: {password}")
    print(f"  Phone: {phone_number}")
    
    # Check if user already exists
    existing_by_username = firestore_service.get_user_by_username(username)
    existing_by_email = firestore_service.get_user_by_email(email)
    
    if existing_by_username:
        print(f"\n[WARNING] Username '{username}' already exists!")
        user_id = existing_by_username.get('id')
        print(f"[INFO] Updating existing user (ID: {user_id})...")
        
        # Update existing user with new password and details
        hashed_password = get_password_hash(password)
        updates = {
            'hashed_password': hashed_password,
            'email': email,
            'phone_number': phone_number,
            'is_active': True
        }
        firestore_service.update_user(user_id, updates)
        print(f"[OK] User '{username}' updated successfully!")
        print_user_credentials(username, email, password, phone_number)
        return
    
    if existing_by_email:
        print(f"\n[WARNING] Email '{email}' already exists!")
        user_id = existing_by_email.get('id')
        print(f"[INFO] Updating existing user (ID: {user_id})...")
        
        # Update existing user
        hashed_password = get_password_hash(password)
        updates = {
            'hashed_password': hashed_password,
            'username': username,
            'phone_number': phone_number,
            'is_active': True
        }
        firestore_service.update_user(user_id, updates)
        print(f"[OK] User with email '{email}' updated successfully!")
        print_user_credentials(username, email, password, phone_number)
        return
    
    # Create new user
    user_data = {
        'username': username,
        'email': email,
        'hashed_password': get_password_hash(password),
        'phone_number': phone_number,
        'is_active': True,
        'is_admin': False
    }
    
    try:
        user_id = firestore_service.create_user(user_data)
        print(f"\n[OK] User created successfully!")
        print(f"  User ID: {user_id}")
        print_user_credentials(username, email, password, phone_number)
        
        print("\n[INFO] You can now use these credentials to login!")
        print("       You can login with either username or email.")
        
    except Exception as e:
        print(f"\n[ERROR] Failed to create user: {e}")
        import traceback
        traceback.print_exc()

def print_user_credentials(username, email, password, phone_number):
    """Print user credentials in a formatted way"""
    print("\n" + "=" * 60)
    print("USER CREDENTIALS")
    print("=" * 60)
    print(f"Username:    {username}")
    print(f"Email:       {email}")
    print(f"Password:    {password}")
    print(f"Mobile:      {phone_number}")
    print("=" * 60)
    print("\nYou can login with:")
    print(f"  - Username: {username}")
    print(f"  - Email:    {email}")
    print("=" * 60)

if __name__ == "__main__":
    create_app_user()
