from app.services.firestore_service import FirestoreService

fs = FirestoreService()
sessions = fs.db.collection('sessions').limit(20).stream()

types = set()
for s in sessions:
    data = s.to_dict()
    types.add(data.get('session_type'))
    print(f"Session ID: {s.id}, Type: {data.get('session_type')}")

print(f"All session types found: {types}")
