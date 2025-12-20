"""
Test Firestore connection
"""
import os
import sys
# Fix encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from app.services.firebase_service import initialize_firebase, get_firestore_db
from firebase_admin import firestore

def test_connection():
    """Test Firebase/Firestore connection"""
    print("[TEST] Testing Firebase connection...")
    
    # Initialize Firebase
    result = initialize_firebase()
    if not result:
        print("[ERROR] Failed to initialize Firebase")
        print("        Check FIREBASE_CREDENTIALS in .env file")
        return False
    
    print("[OK] Firebase initialized successfully!")
    
    # Test Firestore
    try:
        db = get_firestore_db()
        print("[OK] Firestore connection successful!")
        
        # Test write
        test_ref = db.collection('_test').document('connection')
        test_ref.set({'status': 'connected', 'timestamp': 'test'})
        print("[OK] Firestore write test successful!")
        
        # Test read
        doc = test_ref.get()
        if doc.exists:
            print("[OK] Firestore read test successful!")
        
        # Cleanup
        test_ref.delete()
        print("[OK] Test cleanup complete!")
        
        print("\n[SUCCESS] All tests passed! Firestore is ready to use!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Firestore test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_connection()

