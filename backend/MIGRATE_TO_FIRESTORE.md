# 🔥 Complete Migration: MySQL → Firestore

## ⚠️ Major Change Warning

This will **completely replace** MySQL with Firestore. This is a **significant refactoring** that affects:
- All database models
- All routes/queries
- Authentication (optional)
- Data structure

---

## 📊 Comparison: MySQL vs Firestore

| Feature | MySQL | Firestore |
|---------|-------|-----------|
| **Real-time** | ❌ No | ✅ Yes |
| **Offline** | ❌ No | ✅ Yes |
| **Scalability** | Manual | ✅ Auto |
| **Complex Queries** | ✅ SQL | ⚠️ Limited |
| **Joins** | ✅ Yes | ❌ No (denormalize) |
| **Cost** | Free/Cheap | 💰 Pay per use |
| **Transactions** | ✅ Full ACID | ⚠️ Limited |

---

## 🎯 What Needs to Change

### 1. **Remove MySQL Dependencies**
- Remove `sqlalchemy`, `pymysql` from `requirements.txt`
- Remove `database.py` (SQLAlchemy models)
- Remove MySQL connection code

### 2. **Replace with Firestore**
- Use `firebase-admin` (already installed)
- Create Firestore service
- Replace all `db.query()` with Firestore operations

### 3. **Update All Routes**
- `auth.py` - User registration/login
- `chatbot.py` - Sessions
- `voice.py` - Voice analyses
- `typing.py` - Typing analyses
- `admin.py` - Dashboard queries
- `digital_twin.py` - Digital twin data

### 4. **Data Structure Changes**
- No foreign keys (use document references)
- Denormalize data (store related data together)
- Use subcollections for relationships

---

## 🚀 Migration Steps

### Step 1: Update Requirements

Remove from `requirements.txt`:
```
sqlalchemy==2.0.23
pymysql==1.1.0
```

Keep:
```
firebase-admin==6.2.0
```

### Step 2: Create Firestore Service

Create `backend/app/services/firestore_service.py`:

```python
"""
Firestore database service - replaces SQLAlchemy
"""

from firebase_admin import firestore
from app.services.firebase_service import get_firestore_db
from typing import Optional, Dict, List
from datetime import datetime

class FirestoreService:
    def __init__(self):
        self.db = get_firestore_db()
    
    # ========== USER OPERATIONS ==========
    
    def create_user(self, user_data: Dict) -> str:
        """Create new user, returns user ID"""
        user_ref = self.db.collection('users').document()
        user_data['id'] = user_ref.id
        user_data['created_at'] = firestore.SERVER_TIMESTAMP
        user_ref.set(user_data)
        return user_ref.id
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        users_ref = self.db.collection('users')
        query = users_ref.where('username', '==', username).limit(1).stream()
        for doc in query:
            return doc.to_dict()
        return None
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        doc = self.db.collection('users').document(user_id).get()
        if doc.exists:
            return doc.to_dict()
        return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        users_ref = self.db.collection('users')
        query = users_ref.where('email', '==', email).limit(1).stream()
        for doc in query:
            return doc.to_dict()
        return None
    
    def update_user(self, user_id: str, updates: Dict):
        """Update user data"""
        self.db.collection('users').document(user_id).update(updates)
    
    # ========== SESSION OPERATIONS ==========
    
    def create_session(self, session_data: Dict) -> str:
        """Create new session, returns session ID"""
        session_ref = self.db.collection('sessions').document()
        session_data['id'] = session_ref.id
        session_data['start_time'] = firestore.SERVER_TIMESTAMP
        session_ref.set(session_data)
        return session_ref.id
    
    def get_user_sessions(self, user_id: str, session_type: Optional[str] = None) -> List[Dict]:
        """Get all sessions for a user"""
        sessions_ref = self.db.collection('sessions')
        query = sessions_ref.where('user_id', '==', user_id)
        
        if session_type:
            query = query.where('session_type', '==', session_type)
        
        query = query.order_by('start_time', direction=firestore.Query.DESCENDING)
        
        sessions = []
        for doc in query.stream():
            sessions.append(doc.to_dict())
        return sessions
    
    def update_session(self, session_id: str, updates: Dict):
        """Update session"""
        if 'end_time' in updates:
            updates['end_time'] = firestore.SERVER_TIMESTAMP
        self.db.collection('sessions').document(session_id).update(updates)
    
    # ========== VOICE ANALYSIS OPERATIONS ==========
    
    def create_voice_analysis(self, analysis_data: Dict) -> str:
        """Create voice analysis"""
        analysis_ref = self.db.collection('voice_analyses').document()
        analysis_data['id'] = analysis_ref.id
        analysis_data['created_at'] = firestore.SERVER_TIMESTAMP
        analysis_ref.set(analysis_data)
        return analysis_ref.id
    
    def get_user_voice_analyses(self, user_id: str) -> List[Dict]:
        """Get all voice analyses for a user"""
        analyses_ref = self.db.collection('voice_analyses')
        query = analyses_ref.where('user_id', '==', user_id)\
                           .order_by('created_at', direction=firestore.Query.DESCENDING)
        
        analyses = []
        for doc in query.stream():
            analyses.append(doc.to_dict())
        return analyses
    
    # ========== TYPING ANALYSIS OPERATIONS ==========
    
    def create_typing_analysis(self, analysis_data: Dict) -> str:
        """Create typing analysis"""
        analysis_ref = self.db.collection('typing_analyses').document()
        analysis_data['id'] = analysis_ref.id
        analysis_data['created_at'] = firestore.SERVER_TIMESTAMP
        analysis_ref.set(analysis_data)
        return analysis_ref.id
    
    def get_user_typing_analyses(self, user_id: str) -> List[Dict]:
        """Get all typing analyses for a user"""
        analyses_ref = self.db.collection('typing_analyses')
        query = analyses_ref.where('user_id', '==', user_id)\
                           .order_by('created_at', direction=firestore.Query.DESCENDING)
        
        analyses = []
        for doc in query.stream():
            analyses.append(doc.to_dict())
        return analyses
    
    # ========== DIGITAL TWIN OPERATIONS ==========
    
    def create_or_update_digital_twin(self, user_id: str, twin_data: Dict):
        """Create or update digital twin"""
        twin_ref = self.db.collection('digital_twins').document(user_id)
        twin_data['user_id'] = user_id
        twin_data['last_updated'] = firestore.SERVER_TIMESTAMP
        twin_ref.set(twin_data, merge=True)
    
    def get_digital_twin(self, user_id: str) -> Optional[Dict]:
        """Get digital twin for user"""
        doc = self.db.collection('digital_twins').document(user_id).get()
        if doc.exists:
            return doc.to_dict()
        return None
    
    # ========== ADMIN ALERT OPERATIONS ==========
    
    def create_alert(self, alert_data: Dict) -> str:
        """Create admin alert"""
        alert_ref = self.db.collection('admin_alerts').document()
        alert_data['id'] = alert_ref.id
        alert_data['created_at'] = firestore.SERVER_TIMESTAMP
        alert_data['is_resolved'] = False
        alert_ref.set(alert_data)
        return alert_ref.id
    
    def get_alerts(self, resolved: Optional[bool] = None) -> List[Dict]:
        """Get all alerts"""
        alerts_ref = self.db.collection('admin_alerts')
        query = alerts_ref
        
        if resolved is not None:
            query = query.where('is_resolved', '==', resolved)
        
        query = query.order_by('created_at', direction=firestore.Query.DESCENDING)
        
        alerts = []
        for doc in query.stream():
            alerts.append(doc.to_dict())
        return alerts
    
    def resolve_alert(self, alert_id: str):
        """Mark alert as resolved"""
        self.db.collection('admin_alerts').document(alert_id).update({
            'is_resolved': True,
            'resolved_at': firestore.SERVER_TIMESTAMP
        })
    
    # ========== ADMIN DASHBOARD OPERATIONS ==========
    
    def get_all_users(self) -> List[Dict]:
        """Get all active users"""
        users_ref = self.db.collection('users')
        query = users_ref.where('is_active', '==', True)
        
        users = []
        for doc in query.stream():
            users.append(doc.to_dict())
        return users
    
    def get_user_statistics(self, user_id: str) -> Dict:
        """Get user statistics for dashboard"""
        # Get sessions
        sessions = self.get_user_sessions(user_id)
        total_sessions = len(sessions)
        
        if sessions:
            avg_score = sum(s.get('depression_score', 0) or 0 for s in sessions) / total_sessions
            last_session = max(sessions, key=lambda s: s.get('start_time', datetime.min))
            risk_level = last_session.get('risk_level', 'low')
            last_activity = last_session.get('start_time')
        else:
            user = self.get_user_by_id(user_id)
            avg_score = 0
            risk_level = 'low'
            last_activity = user.get('created_at') if user else datetime.now()
        
        return {
            'total_sessions': total_sessions,
            'average_depression_score': avg_score,
            'risk_level': risk_level,
            'last_activity': last_activity
        }
```

### Step 3: Update Authentication Route

Replace `backend/app/routes/auth.py`:

```python
from app.services.firestore_service import FirestoreService
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
firestore_service = FirestoreService()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get current authenticated user from Firestore"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = firestore_service.get_user_by_username(username)
    if user is None:
        raise credentials_exception
    return user

@router.post("/register", response_model=Token)
async def register(user_data: UserRegister):
    """Register new user in Firestore"""
    # Check if user exists
    if firestore_service.get_user_by_username(user_data.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    if firestore_service.get_user_by_email(user_data.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user_id = firestore_service.create_user({
        'username': user_data.username,
        'email': user_data.email,
        'hashed_password': hashed_password,
        'phone_number': user_data.phone_number,
        'is_active': True,
        'is_admin': False
    })
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_data.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    """Login user from Firestore"""
    user = firestore_service.get_user_by_username(user_data.username)
    if not user or not verify_password(user_data.password, user.get('hashed_password')):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_data.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
```

### Step 4: Update Other Routes

Similar pattern - replace all `db.query()` with `firestore_service` methods.

---

## ⚠️ Important Considerations

### 1. **No Foreign Keys**
- Store `user_id` as string, not integer
- No automatic referential integrity
- Handle relationships manually

### 2. **Denormalization**
- Store frequently accessed data together
- Example: Store user info in session document

### 3. **Query Limitations**
- No complex JOINs
- Limited sorting/grouping
- Use composite indexes for complex queries

### 4. **Cost**
- Free tier: 50K reads/day, 20K writes/day
- After that: Pay per operation
- Can get expensive with high traffic

### 5. **Data Migration**
- Need to migrate existing MySQL data to Firestore
- Create migration script

---

## 💰 Cost Estimate

**Free Tier:**
- 50,000 reads/day
- 20,000 writes/day
- 20,000 deletes/day
- 1 GB storage

**After Free Tier:**
- $0.06 per 100,000 reads
- $0.18 per 100,000 writes
- $0.02 per 100,000 deletes

**For your app:** If you have 100 users, each doing 10 operations/day = 1,000 operations/day = **FREE** ✅

---

## ✅ Pros of Full Firestore Migration

1. ✅ **Real-time updates** - Automatic
2. ✅ **Offline support** - Built-in
3. ✅ **No server management** - Fully managed
4. ✅ **Auto-scaling** - Handles traffic spikes
5. ✅ **Mobile-optimized** - Perfect for Flutter
6. ✅ **Simpler deployment** - No database server

---

## ❌ Cons of Full Firestore Migration

1. ❌ **Cost** - Can get expensive at scale
2. ❌ **Learning curve** - Different query patterns
3. ❌ **Migration effort** - Rewrite all routes
4. ❌ **Less SQL-like** - No complex queries
5. ❌ **No joins** - Must denormalize data

---

## 🎯 Recommendation

**For your project (depression monitoring app):**

✅ **GOOD if:**
- You want real-time + offline (your requirements!)
- You have < 1000 users (stays in free tier)
- You're okay with simpler queries
- You want easier deployment

❌ **NOT GOOD if:**
- You need complex SQL queries
- You have > 10,000 users (cost concerns)
- You need strict data integrity
- You want to keep MySQL Workbench

---

## 🚀 Next Steps

If you want to proceed:

1. ✅ Create `firestore_service.py` (code above)
2. ✅ Update all routes to use Firestore
3. ✅ Remove MySQL dependencies
4. ✅ Migrate existing data (if any)
5. ✅ Test thoroughly
6. ✅ Update frontend (if needed)

**I can help you create the complete migration!** Just let me know if you want to proceed.

















