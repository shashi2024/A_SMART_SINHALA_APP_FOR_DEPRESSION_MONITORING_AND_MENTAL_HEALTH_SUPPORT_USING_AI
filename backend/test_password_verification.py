"""
Script to test password verification for the testnew user
"""
from app.services.firebase_service import initialize_firebase
from app.services.firestore_service import FirestoreService
from app.routes.auth import verify_password, get_password_hash
import bcrypt

def test_password():
    """Test password verification"""
    print("=" * 60)
    print("Test Password Verification")
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
    
    # Get user
    email = 'testnew@test.com'
    password = 'testnew1234'
    
    print(f"\n[INFO] Testing password for email: {email}")
    print(f"[INFO] Password to test: {password}")
    
    user = firestore_service.get_user_by_email(email)
    
    if not user:
        print(f"[ERROR] User not found!")
        return
    
    print(f"\n[OK] User found:")
    print(f"  User ID: {user.get('id')}")
    print(f"  Username: {user.get('username')}")
    print(f"  Email: {user.get('email')}")
    
    stored_hash = user.get('hashed_password')
    if not stored_hash:
        print(f"[ERROR] No password hash stored!")
        return
    
    print(f"\n[INFO] Stored password hash: {stored_hash[:50]}...")
    
    # Test password verification using the auth function
    print(f"\n[TEST] Verifying password using verify_password() function...")
    try:
        result = verify_password(password, stored_hash)
        print(f"[RESULT] verify_password() returned: {result}")
        
        if result:
            print("[OK] Password verification PASSED!")
        else:
            print("[FAIL] Password verification FAILED!")
            
            # Let's try to create a new hash and see if it matches
            print("\n[DEBUG] Testing password hashing...")
            new_hash = get_password_hash(password)
            print(f"[INFO] New hash for same password: {new_hash[:50]}...")
            
            # Test if new hash matches stored hash
            print("\n[TEST] Testing if new hash verifies with stored hash...")
            test_result = verify_password(password, new_hash)
            print(f"[RESULT] New hash verification: {test_result}")
            
            # Try direct bcrypt comparison
            print("\n[DEBUG] Trying direct bcrypt comparison...")
            try:
                password_bytes = password.encode('utf-8')
                if len(password_bytes) > 72:
                    password_bytes = password_bytes[:72]
                stored_hash_bytes = stored_hash.encode('utf-8')
                direct_result = bcrypt.checkpw(password_bytes, stored_hash_bytes)
                print(f"[RESULT] Direct bcrypt.checkpw(): {direct_result}")
            except Exception as e:
                print(f"[ERROR] Direct bcrypt check failed: {e}")
                import traceback
                traceback.print_exc()
                
    except Exception as e:
        print(f"[ERROR] Password verification failed with exception: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_password()



