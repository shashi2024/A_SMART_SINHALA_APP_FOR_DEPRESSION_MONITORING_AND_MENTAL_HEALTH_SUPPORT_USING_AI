"""
Script to update/create admin user in Firestore (non-interactive)
"""
from app.services.firebase_service import initialize_firebase
from app.services.firestore_service import FirestoreService
import bcrypt

def get_password_hash(password: str) -> str:
    """Hash password using bcrypt"""
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def update_admin():
    """Update or create admin user"""
    print("=" * 60)
    print("Update/Create Admin User")
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
    
    # Admin credentials
    username = 'admin'
    password = 'admin123456'
    email = 'admin@hospital.com'
    
    # Check if admin already exists
    existing_admin = firestore_service.get_user_by_username(username)
    
    if existing_admin:
        print(f"[INFO] Admin user '{username}' already exists!")
        print(f"[INFO] Updating password and ensuring admin privileges...")
        
        # Update existing user
        hashed_password = get_password_hash(password)
        updates = {
            'hashed_password': hashed_password,
            'is_admin': True,
            'is_active': True,
            'email': email,
        }
        firestore_service.update_user(existing_admin['id'], updates)
        print(f"[OK] Admin user updated successfully!")
    else:
        print(f"[INFO] Creating new admin user...")
        
        # Create new admin user
        admin_data = {
            'username': username,
            'email': email,
            'hashed_password': get_password_hash(password),
            'is_active': True,
            'is_admin': True,
        }
        
        try:
            user_id = firestore_service.create_user(admin_data)
            print(f"[OK] Admin user created successfully!")
            print(f"  User ID: {user_id}")
        except Exception as e:
            print(f"[ERROR] Failed to create admin: {e}")
            import traceback
            traceback.print_exc()
            return
    
    print("\n" + "=" * 60)
    print("ADMIN CREDENTIALS")
    print("=" * 60)
    print(f"Username: {username}")
    print(f"Password: {password}")
    print(f"Email:    {email}")
    print("=" * 60)
    print("\n[INFO] You can now login with these credentials!")

if __name__ == "__main__":
    update_admin()



