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
        """Get user by ID - searches by document ID or by id field"""
        if not user_id:
            return None
        
        # First try direct document ID
        doc = self.db.collection('users').document(user_id).get()
        if doc.exists:
            user_data = doc.to_dict()
            if user_data:
                user_data['id'] = doc.id  # Ensure id field is set
            return user_data
        
        # If not found, search by id field
        try:
            users_ref = self.db.collection('users')
            query = users_ref.where('id', '==', user_id).limit(1).stream()
            for doc in query:
                user_data = doc.to_dict()
                if user_data:
                    user_data['id'] = doc.id  # Ensure id field is set
                return user_data
        except Exception as e:
            print(f"[ERROR] get_user_by_id query failed: {e}")
        
        # Fallback: search all documents
        try:
            all_docs = self.db.collection('users').stream()
            for doc in all_docs:
                user_data = doc.to_dict()
                if user_data and (user_data.get('id') == user_id or doc.id == user_id):
                    user_data['id'] = doc.id  # Ensure id field is set
                    return user_data
        except Exception as e:
            print(f"[ERROR] get_user_by_id fallback search failed: {e}")
        
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
        """Get all active users (or all users if is_active field is missing)"""
        try:
            users_ref = self.db.collection('users')
            users = []
            user_ids_seen = set()  # Track user IDs to avoid duplicates
            
            # Get all users first (simpler and more reliable)
            print("[INFO] Fetching all users from Firestore...")
            try:
                all_docs = users_ref.stream()
                for doc in all_docs:
                    try:
                        user_data = doc.to_dict()
                        if not user_data:
                            continue
                        
                        # Ensure id is set (use document ID as fallback)
                        user_id = user_data.get('id') or doc.id
                        user_data['id'] = user_id
                        
                        # Skip if we've already seen this user ID
                        if user_id in user_ids_seen:
                            continue
                        user_ids_seen.add(user_id)
                        
                        # Set default is_active to True if missing
                        if 'is_active' not in user_data:
                            user_data['is_active'] = True
                            # Update the document to include is_active field (async, don't wait)
                            try:
                                users_ref.document(doc.id).update({'is_active': True})
                            except Exception as e:
                                print(f"[WARNING] Failed to update is_active for user {doc.id}: {e}")
                        
                        # Only include if is_active is True or missing (default to True)
                        # Exclude admin users from patient list (they're not patients)
                        if user_data.get('is_active', True) and not user_data.get('is_admin', False):
                            users.append(user_data)
                            
                    except Exception as e:
                        print(f"[ERROR] Error processing user document {doc.id}: {e}")
                        import traceback
                        traceback.print_exc()
                        continue
                        
            except Exception as e:
                print(f"[ERROR] Failed to fetch all users: {e}")
                import traceback
                traceback.print_exc()
                return []
            
            print(f"[INFO] Found {len(users)} active users")
            return users
            
        except Exception as e:
            print(f"[ERROR] Failed to get all active users: {e}")
            import traceback
            traceback.print_exc()
            # Return empty list on error rather than crashing
            return []
    
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
        try:
            sessions_ref = self.db.collection('sessions')
            
            # Get all sessions for the user first
            query = sessions_ref.where('user_id', '==', user_id)
            
            sessions = []
            for doc in query.stream():
                try:
                    session_data = doc.to_dict()
                    if not session_data:
                        continue
                    
                    # Ensure id is set (use document ID as fallback)
                    if 'id' not in session_data:
                        session_data['id'] = doc.id
                    
                    # Filter by session_type if specified
                    if session_type and session_data.get('session_type') != session_type:
                        continue
                    
                    sessions.append(session_data)
                except Exception as e:
                    print(f"[ERROR] Error processing session document {doc.id}: {e}")
                    continue
            
            # Sort by start_time descending (handle various time formats)
            def get_start_time(s):
                start_time = s.get('start_time')
                if isinstance(start_time, datetime):
                    return start_time
                elif isinstance(start_time, str):
                    try:
                        return datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    except:
                        pass
                return datetime.min
            
            sessions.sort(key=get_start_time, reverse=True)
            
            print(f"[INFO] Retrieved {len(sessions)} sessions for user {user_id}")
            return sessions
            
        except Exception as e:
            print(f"[ERROR] Failed to get user sessions: {e}")
            import traceback
            traceback.print_exc()
            return []
    
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
        """Get user statistics for dashboard including mood-based risk"""
        # Get all sessions
        sessions = self.get_user_sessions(user_id)
        total_sessions = len(sessions)
        
        # Get all mood check-ins (not just last 7 days for complete statistics)
        mood_checkins = self.get_user_mood_checkins(
            user_id=user_id,
            limit=200  # Get more mood check-ins for better statistics
        )
        
        # Get recent mood check-ins (last 7 days) for risk calculation
        from datetime import timedelta
        seven_days_ago = (datetime.utcnow() - timedelta(days=7)).date().isoformat()
        recent_mood_checkins = self.get_user_mood_checkins(
            user_id=user_id,
            limit=50,
            start_date=seven_days_ago
        )
        
        # Calculate average depression score correctly (only count sessions with scores)
        avg_score = 0.0
        if sessions:
            scores_with_values = [s.get('depression_score') for s in sessions if s.get('depression_score') is not None]
            if scores_with_values:
                avg_score = sum(scores_with_values) / len(scores_with_values)
        
        # Calculate risk level including mood data
        risk_level = 'low'
        last_activity = None
        
        if sessions:
            last_session = max(sessions, key=lambda s: s.get('start_time', datetime.min))
            session_risk = last_session.get('risk_level', 'low')
            last_activity = last_session.get('start_time')
            
            # Calculate mood-based risk from recent check-ins
            mood_risk = self._calculate_mood_risk_for_stats(recent_mood_checkins)
            
            # Take the higher risk level
            risk_levels_order = ["low", "moderate", "high", "severe"]
            session_index = risk_levels_order.index(session_risk) if session_risk in risk_levels_order else 0
            mood_index = risk_levels_order.index(mood_risk) if mood_risk in risk_levels_order else 0
            final_risk_index = max(session_index, mood_index)
            risk_level = risk_levels_order[final_risk_index]
        else:
            user = self.get_user_by_id(user_id)
            # Use mood risk if no sessions
            risk_level = self._calculate_mood_risk_for_stats(recent_mood_checkins)
            
            # Set last activity to most recent mood check-in or user creation
            if mood_checkins:
                # Get the most recent mood check-in
                recent_checkin = max(mood_checkins, key=lambda m: m.get('created_at', datetime.min))
                last_activity = recent_checkin.get('created_at')
            else:
                last_activity = user.get('created_at') if user else datetime.now()
        
        return {
            'total_sessions': total_sessions,
            'average_depression_score': avg_score,
            'risk_level': risk_level,
            'last_activity': last_activity,
            'total_mood_checkins': len(mood_checkins),
            'recent_mood_checkins': len(recent_mood_checkins)
        }
    
    def _calculate_mood_risk_for_stats(self, mood_checkins: list) -> str:
        """Calculate risk level based on mood check-ins for statistics"""
        if not mood_checkins:
            return "low"
        
        # Count negative moods
        negative_moods = ['Sad', 'Anxious']
        negative_count = sum(1 for checkin in mood_checkins if checkin.get('mood') in negative_moods)
        negative_ratio = negative_count / len(mood_checkins)
        
        # Determine risk based on mood patterns
        if negative_ratio >= 0.7:  # 70% or more negative moods
            return "severe"
        elif negative_ratio >= 0.5:  # 50-70% negative moods
            return "high"
        elif negative_ratio >= 0.3:  # 30-50% negative moods
            return "moderate"
        else:
            return "low"
    
    # ========== CALL OPERATIONS ==========
    
    def create_call(self, call_data: Dict) -> str:
        """Create new call, returns call ID"""
        call_ref = self.db.collection('calls').document(call_data['id'])
        call_data['created_at'] = firestore.SERVER_TIMESTAMP
        call_ref.set(call_data)
        return call_data['id']
    
    def get_call_by_id(self, call_id: str) -> Optional[Dict]:
        """Get call by ID"""
        doc = self.db.collection('calls').document(call_id).get()
        if doc.exists:
            return doc.to_dict()
        return None
    
    def update_call(self, call_id: str, updates: Dict):
        """Update call data"""
        self.db.collection('calls').document(call_id).update(updates)
    
    def get_user_calls(
        self,
        user_id: str,
        call_type: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """Get all calls for a user (as caller or callee)"""
        calls_ref = self.db.collection('calls')
        
        # Get calls where user is caller
        caller_query = calls_ref.where('caller_id', '==', user_id)
        if call_type:
            caller_query = caller_query.where('call_type', '==', call_type)
        
        calls = []
        for doc in caller_query.stream():
            calls.append(doc.to_dict())
        
        # Get calls where user is callee
        callee_query = calls_ref.where('callee_id', '==', user_id)
        if call_type:
            callee_query = callee_query.where('call_type', '==', call_type)
        
        for doc in callee_query.stream():
            calls.append(doc.to_dict())
        
        # Sort by started_at descending
        calls.sort(key=lambda x: x.get('started_at', datetime.min), reverse=True)
        
        return calls[:limit]
    
    def get_available_counselors(self, language: str = "en") -> List[Dict]:
        """Get list of available counselors"""
        # Query users with role 'counselor' and status 'available'
        users_ref = self.db.collection('users')
        query = users_ref.where('role', '==', 'counselor').where('status', '==', 'available')
        
        counselors = []
        for doc in query.stream():
            user_data = doc.to_dict()
            # Filter by language if specified
            if language == "en" or language in user_data.get('languages', []):
                counselors.append({
                    'id': user_data.get('id'),
                    'username': user_data.get('username'),
                    'name': user_data.get('name', user_data.get('username')),
                    'languages': user_data.get('languages', []),
                    'rating': user_data.get('rating', 0),
                    'specializations': user_data.get('specializations', [])
                })
        
        return counselors
    
    # ========== MOOD CHECK-IN OPERATIONS ==========
    
    def create_mood_checkin(self, mood_data: Dict) -> str:
        """Create new mood check-in, returns check-in ID"""
        mood_ref = self.db.collection('mood_checkins').document()
        mood_data['id'] = mood_ref.id
        mood_data['created_at'] = firestore.SERVER_TIMESTAMP
        mood_data['date'] = datetime.now().date().isoformat()  # Store date for easy querying
        mood_ref.set(mood_data)
        return mood_ref.id
    
    def get_user_mood_checkins(
        self,
        user_id: str,
        limit: int = 50,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict]:
        """Get all mood check-ins for a user"""
        try:
            mood_ref = self.db.collection('mood_checkins')
            query = mood_ref.where('user_id', '==', user_id)
            
            # Note: Firestore compound queries need indexes
            # For now, get all user check-ins and filter in memory if dates specified
            checkins = []
            for doc in query.stream():
                try:
                    checkin_data = doc.to_dict()
                    if not checkin_data:
                        continue
                    
                    # Ensure id is set (use document ID as fallback)
                    if 'id' not in checkin_data:
                        checkin_data['id'] = doc.id
                    
                    # Filter by date if specified
                    checkin_date = checkin_data.get('date', '')
                    if start_date and checkin_date < start_date:
                        continue
                    if end_date and checkin_date > end_date:
                        continue
                    
                    checkins.append(checkin_data)
                except Exception as e:
                    print(f"[ERROR] Error processing mood check-in document {doc.id}: {e}")
                    continue
            
            # Sort by created_at descending (handle various time formats)
            def get_created_time(c):
                created_at = c.get('created_at')
                if isinstance(created_at, datetime):
                    return created_at
                elif isinstance(created_at, str):
                    try:
                        return datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    except:
                        pass
                return datetime.min
            
            checkins.sort(key=get_created_time, reverse=True)
            
            print(f"[INFO] Retrieved {len(checkins)} mood check-ins for user {user_id} (limited to {limit})")
            return checkins[:limit]
            
        except Exception as e:
            print(f"[ERROR] Failed to get user mood check-ins: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_all_mood_checkins(
        self,
        limit: int = 100,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> List[Dict]:
        """Get all mood check-ins (for admin panel)"""
        mood_ref = self.db.collection('mood_checkins')
        query = mood_ref
        
        if user_id:
            query = query.where('user_id', '==', user_id)
        if start_date:
            query = query.where('date', '>=', start_date)
        if end_date:
            query = query.where('date', '<=', end_date)
        
        checkins = []
        for doc in query.stream():
            checkins.append(doc.to_dict())
        
        # Sort by created_at descending
        checkins.sort(key=lambda x: x.get('created_at', datetime.min), reverse=True)
        
        return checkins[:limit]



