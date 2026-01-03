"""
Script to create a test user in Firestore for chatbot testing
"""
from app.services.firebase_service import initialize_firebase
from app.services.firestore_service import FirestoreService
from app.routes.auth import get_password_hash

def create_test_user():
    """Create a test user for chatbot testing"""
    print("[INFO] Creating test user...")
    
    # Initialize Firebase
    initialize_firebase()
    
    # Initialize Firestore service
    firestore_service = FirestoreService()
    
    # Test user credentials
    username = 'test'
    password = 'test1234'
    email = 'test@example.com'
    
    # Check if test user already exists
    existing_user = firestore_service.get_user_by_username(username)
    if existing_user:
        print(f"[WARNING] User '{username}' already exists!")
        response = input("Do you want to update the password? (y/n): ")
        if response.lower() != 'y':
            print("[INFO] Cancelled.")
            return
        
        # Update existing user password
        hashed_password = get_password_hash(password)
        firestore_service.update_user(existing_user['id'], {
            'hashed_password': hashed_password,
            'is_active': True
        })
        print(f"[OK] User '{username}' password updated successfully!")
        print(f"\n[INFO] Login credentials:")
        print(f"     Username: {username}")
        print(f"     Password: {password}")
        return
    
    # Create new test user
    user_data = {
        'username': username,
        'email': email,
        'hashed_password': get_password_hash(password),
        'is_active': True,
        'is_admin': False
    }
    
    try:
        user_id = firestore_service.create_user(user_data)
        print(f"[OK] Test user created successfully!")
        print(f"     User ID: {user_id}")
        print(f"\n[INFO] Login credentials:")
        print(f"     Username: {username}")
        print(f"     Password: {password}")
        print(f"     Email: {email}")
        print(f"\n[INFO] You can now use these credentials to test the chatbot!")
    except Exception as e:
        print(f"[ERROR] Failed to create test user: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_test_user()

