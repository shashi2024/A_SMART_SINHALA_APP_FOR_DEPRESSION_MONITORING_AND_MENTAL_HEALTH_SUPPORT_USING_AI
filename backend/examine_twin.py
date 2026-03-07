from app.services.firestore_service import FirestoreService
import json

fs = FirestoreService()
t = fs.db.collection('digital_twins').document('Gck0QZP6s5xQRYmIoL3D').get()

if t.exists:
    data = t.to_dict()
    print(f"Twin Data for Gck0QZP6s5xQRYmIoL3D:")
    for k, v in data.items():
        if isinstance(v, str) and (v.startswith('{') or v.startswith('[')):
            try:
                print(f"{k}: {json.dumps(json.loads(v), indent=2)}")
            except:
                print(f"{k}: {v}")
        else:
            print(f"{k}: {v}")
else:
    print("Twin not found")
