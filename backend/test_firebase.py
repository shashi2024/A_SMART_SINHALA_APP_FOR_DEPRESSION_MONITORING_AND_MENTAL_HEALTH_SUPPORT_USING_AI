"""
Test Firebase connection and services
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app.services.firebase_service import initialize_firebase, is_firebase_initialized
    from app.config import settings
    
    print("=" * 60)
    print("Firebase Connection Test")
    print("=" * 60)
    
    print(f"\nCredentials Path: {settings.FIREBASE_CREDENTIALS}")
    print(f"File Exists: {os.path.exists(settings.FIREBASE_CREDENTIALS) if settings.FIREBASE_CREDENTIALS else False}")
    
    print("\nAttempting to initialize Firebase...")
    
    success = initialize_firebase()
    
    if success and is_firebase_initialized():
        print("\n" + "=" * 60)
        print("✅ Firebase initialized successfully!")
        print("=" * 60)
        print("\nFirebase services available:")
        print("  - Cloud Storage: ✅")
        print("  - Cloud Messaging: ✅")
        print("\nYou can now use Firebase in your application!")
    else:
        print("\n" + "=" * 60)
        print("⚠️  Firebase not initialized")
        print("=" * 60)
        print("\nTo enable Firebase:")
        print("1. Go to https://console.firebase.google.com/")
        print("2. Create a project or select existing one")
        print("3. Go to Project Settings → Service Accounts")
        print("4. Generate new private key")
        print("5. Save the JSON file as 'firebase-credentials.json' in backend/")
        print("6. Update .env file: FIREBASE_CREDENTIALS=./firebase-credentials.json")
        print("\nFirebase is optional - your app works without it!")
    
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("\nMake sure you:")
    print("1. Are in the backend directory")
    print("2. Have activated virtual environment")
    print("3. Have installed requirements: pip install firebase-admin")
    sys.exit(1)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


