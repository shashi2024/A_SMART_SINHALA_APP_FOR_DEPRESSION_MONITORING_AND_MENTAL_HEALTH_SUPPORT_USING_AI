"""
Script to check if a user exists in Firestore
"""
from app.services.firebase_service import initialize_firebase
from app.services.firestore_service import FirestoreService

def check_user():
    """Check if user exists in Firestore"""
    print("=" * 60)
    print("Check User in Firestore")
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
    
    # Check by username
    username = 'testnew'
    print(f"\n[INFO] Checking for username: {username}")
    user_by_username = firestore_service.get_user_by_username(username)
    
    if user_by_username:
        print(f"[OK] User found by username!")
        print(f"  User ID: {user_by_username.get('id')}")
        print(f"  Username: {user_by_username.get('username')}")
        print(f"  Email: {user_by_username.get('email')}")
        print(f"  Phone: {user_by_username.get('phone_number')}")
        print(f"  Is Active: {user_by_username.get('is_active')}")
        print(f"  Has Password Hash: {'Yes' if user_by_username.get('hashed_password') else 'No'}")
    else:
        print(f"[NOT FOUND] User '{username}' not found by username")
    
    # Check by email
    email = 'testnew@test.com'
    print(f"\n[INFO] Checking for email: {email}")
    user_by_email = firestore_service.get_user_by_email(email)
    
    if user_by_email:
        print(f"[OK] User found by email!")
        print(f"  User ID: {user_by_email.get('id')}")
        print(f"  Username: {user_by_email.get('username')}")
        print(f"  Email: {user_by_email.get('email')}")
        print(f"  Phone: {user_by_email.get('phone_number')}")
        print(f"  Is Active: {user_by_email.get('is_active')}")
        print(f"  Has Password Hash: {'Yes' if user_by_email.get('hashed_password') else 'No'}")
    else:
        print(f"[NOT FOUND] User with email '{email}' not found")
    
    # List all users (first 10)
    print(f"\n[INFO] Listing all users in 'users' collection:")
    try:
        db = firestore_service.db
        users_ref = db.collection('users')
        docs = users_ref.limit(10).stream()
        
        user_count = 0
        for doc in docs:
            user_count += 1
            user_data = doc.to_dict()
            print(f"\n  User #{user_count}:")
            print(f"    Document ID: {doc.id}")
            print(f"    User ID: {user_data.get('id')}")
            print(f"    Username: {user_data.get('username')}")
            print(f"    Email: {user_data.get('email')}")
            print(f"    Phone: {user_data.get('phone_number')}")
        
        if user_count == 0:
            print("  [NO USERS FOUND] The 'users' collection is empty or doesn't exist")
        else:
            print(f"\n[INFO] Found {user_count} user(s) in collection")
    except Exception as e:
        print(f"[ERROR] Failed to list users: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    check_user()




























