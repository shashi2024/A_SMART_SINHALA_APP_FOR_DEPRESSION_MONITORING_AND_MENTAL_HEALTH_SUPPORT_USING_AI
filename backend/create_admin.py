"""
Script to create an admin user in Firestore
"""
from app.services.firestore_service import FirestoreService
from app.routes.auth import get_password_hash

def create_admin():
    """Create an admin user"""
    print("[INFO] Creating admin user...")
    
    # Initialize Firestore service
    firestore_service = FirestoreService()
    
    # Check if admin already exists
    existing_admin = firestore_service.get_user_by_username('admin')
    if existing_admin:
        print("[WARNING] Admin user already exists!")
        response = input("Do you want to update it to admin? (y/n): ")
        if response.lower() != 'y':
            print("[INFO] Cancelled.")
            return
        # Update existing user to admin
        firestore_service.update_user(existing_admin['id'], {'is_admin': True})
        print("[OK] Existing user updated to admin!")
        return
    
    # Create new admin user
    admin_data = {
        'username': 'admin',
        'email': 'admin@hospital.com',
        'hashed_password': get_password_hash('admin123456'),
        'is_active': True,
        'is_admin': True  # This makes them admin!
    }
    
    try:
        user_id = firestore_service.create_user(admin_data)
        print("[OK] Admin user created successfully!")
        print(f"     User ID: {user_id}")
        print("\n[INFO] Login credentials:")
        print("     Username: admin")
        print("     Password: admin123456")
        print("\n[WARNING] Change the password after first login!")
    except Exception as e:
        print(f"[ERROR] Failed to create admin: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_admin()


































































