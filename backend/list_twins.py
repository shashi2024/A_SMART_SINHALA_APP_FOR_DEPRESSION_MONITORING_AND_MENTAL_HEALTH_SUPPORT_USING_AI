from app.services.firestore_service import FirestoreService

fs = FirestoreService()
twins = fs.db.collection('digital_twins').limit(5).stream()

for t in twins:
    print(f"Twin User ID: {t.id}")
    print(f"Data: {t.to_dict()}")
