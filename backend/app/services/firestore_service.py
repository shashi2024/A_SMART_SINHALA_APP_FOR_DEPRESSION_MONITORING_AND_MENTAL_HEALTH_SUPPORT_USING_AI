"""
Firestore database service - replaces SQLAlchemy/MySQL
Use this instead of database.py for all database operations
"""

from firebase_admin import firestore
from app.services.firebase_service import get_firestore_db, is_firebase_initialized, initialize_firebase
from typing import Optional, Dict, List
from datetime import datetime

class FirestoreService:
    """Firestore database service - replaces SQLAlchemy"""
    
    def __init__(self):
        # Lazy initialization - try to initialize Firebase if not already done
        if not is_firebase_initialized():
            # Try to initialize Firebase automatically
            initialize_firebase()
            # If still not initialized, raise error
            if not is_firebase_initialized():
                raise Exception("Firebase not initialized. Check FIREBASE_CREDENTIALS in .env")
        self._db = None
    
    @property
    def db(self):
        """Lazy-load Firestore database"""
        if self._db is None:
            self._db = get_firestore_db()
        return self._db
    
    # ========== USER OPERATIONS ==========
    
    def create_user(self, user_data: Dict) -> str:
        """Create new user, returns user ID"""
        try:
            user_ref = self.db.collection('users').document()
            user_data['id'] = user_ref.id
            user_data['created_at'] = firestore.SERVER_TIMESTAMP
            
            # Remove None values to avoid Firestore errors
            user_data = {k: v for k, v in user_data.items() if v is not None}
            
            user_ref.set(user_data)
            return user_ref.id
        except Exception as e:
            print(f"[ERROR] create_user failed: {e}")
            import traceback
            traceback.print_exc()
            raise
    
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
        try:
            users_ref = self.db.collection('users')
            query = users_ref.where('email', '==', email).limit(1).stream()
            for doc in query:
                return doc.to_dict()
            return None
        except Exception as e:
            print(f"[ERROR] get_user_by_email failed: {e}")
            return None
    
    def update_user(self, user_id: str, updates: Dict):
        """Update user data"""
        self.db.collection('users').document(user_id).update(updates)
    
    def get_all_active_users(self) -> List[Dict]:
        """Get all active users"""
        users_ref = self.db.collection('users')
        query = users_ref.where('is_active', '==', True)
        
        users = []
        for doc in query.stream():
            users.append(doc.to_dict())
        return users
    
    # ========== SESSION OPERATIONS ==========
    
    def create_session(self, session_data: Dict) -> str:
        """Create new session, returns session ID"""
        session_ref = self.db.collection('sessions').document()
        session_data['id'] = session_ref.id
        session_data['start_time'] = firestore.SERVER_TIMESTAMP
        session_ref.set(session_data)
        return session_ref.id
    
    def get_session_by_id(self, session_id: str) -> Optional[Dict]:
        """Get session by ID"""
        doc = self.db.collection('sessions').document(session_id).get()
        if doc.exists:
            return doc.to_dict()
        return None
    
    def get_user_sessions(self, user_id: str, session_type: Optional[str] = None) -> List[Dict]:
        """Get all sessions for a user"""
        sessions_ref = self.db.collection('sessions')
        query = sessions_ref.where('user_id', '==', user_id)
        
        if session_type:
            query = query.where('session_type', '==', session_type)
        
        # Note: Firestore requires index for compound queries
        # For now, get all and sort in memory if needed
        sessions = []
        for doc in query.stream():
            sessions.append(doc.to_dict())
        
        # Sort by start_time descending
        sessions.sort(key=lambda x: x.get('start_time', datetime.min), reverse=True)
        return sessions
    
    def update_session(self, session_id: str, updates: Dict):
        """Update session"""
        if 'end_time' in updates and updates['end_time'] is None:
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
        query = analyses_ref.where('user_id', '==', user_id)
        
        analyses = []
        for doc in query.stream():
            analyses.append(doc.to_dict())
        
        # Sort by created_at descending
        analyses.sort(key=lambda x: x.get('created_at', datetime.min), reverse=True)
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
        query = analyses_ref.where('user_id', '==', user_id)
        
        analyses = []
        for doc in query.stream():
            analyses.append(doc.to_dict())
        
        # Sort by created_at descending
        analyses.sort(key=lambda x: x.get('created_at', datetime.min), reverse=True)
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
        
        alerts = []
        for doc in query.stream():
            alerts.append(doc.to_dict())
        
        # Sort by created_at descending
        alerts.sort(key=lambda x: x.get('created_at', datetime.min), reverse=True)
        return alerts
    
    def resolve_alert(self, alert_id: str):
        """Mark alert as resolved"""
        self.db.collection('admin_alerts').document(alert_id).update({
            'is_resolved': True,
            'resolved_at': firestore.SERVER_TIMESTAMP
        })
    
    # ========== ADMIN DASHBOARD OPERATIONS ==========
    
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



