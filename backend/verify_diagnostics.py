from app.services.firestore_service import FirestoreService
from app.services.phq9_service import PHQ9Service
import asyncio

async def test_diagnostics():
    fs = FirestoreService()
    phq9 = PHQ9Service()
    
    # Get all users
    users = fs.get_all_active_users()
    if not users:
        print("No users found")
        return
        
    user_id = users[0]['id']
    print(f"Testing diagnostics for user: {user_id}")
    
    # Test get_latest_phq9_session
    latest = fs.get_latest_phq9_session(user_id)
    print(f"Latest PHQ-9: {latest}")
    
    # Test get_user_typing_analyses
    typing = fs.get_user_typing_analyses(user_id)
    print(f"Typing Analyses count: {len(typing)}")
    
    print("Verification complete.")

if __name__ == "__main__":
    asyncio.run(test_diagnostics())
