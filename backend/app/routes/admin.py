"""
Admin panel routes for hospital management - Using Firestore
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.routes.auth import get_current_user
from app.services.firestore_service import FirestoreService

router = APIRouter()
firestore_service = FirestoreService()

def require_admin_access(current_user: dict):
    """Check if user has admin or sub-admin access"""
    if not (current_user.get('is_admin', False) or current_user.get('is_sub_admin', False)):
        raise HTTPException(status_code=403, detail="Admin or sub-admin access required")
    return True

def require_full_admin(current_user: dict):
    """Check if user has full admin access (not sub-admin)"""
    if not current_user.get('is_admin', False):
        raise HTTPException(status_code=403, detail="Full administrator access required")
    return True

class AlertResponse(BaseModel):
    id: str  # Changed from int to str for Firestore
    user_id: str  # Changed from int to str
    username: str
    alert_type: str
    severity: str
    message: str
    created_at: datetime

class UserDashboard(BaseModel):
    user_id: str  # Changed from int to str for Firestore
    username: str
    email: str
    total_sessions: int
    average_depression_score: float
    risk_level: str
    last_activity: datetime

class CreateUserRequest(BaseModel):
    username: str
    email: str
    password: str
    phone_number: Optional[str] = None
    is_admin: bool = False
    is_sub_admin: bool = False
    role: Optional[str] = None  # 'doctor' or 'nurse'
    specialization: Optional[str] = None  # Doctor specialization (e.g., 'Cardiologist', 'Psychiatrist')

@router.get("/dashboard")
async def get_dashboard(
    current_user: dict = Depends(get_current_user)
):
    """Get admin dashboard data from Firestore (accessible by admin and sub-admin)"""
    require_admin_access(current_user)
    
    try:
        from datetime import datetime, timedelta
        
        # Get all active users
        users = firestore_service.get_all_active_users()
        dashboard_data = []
        
        # Statistics for key metrics
        total_sessions = 0
        total_patients = len(users)
        clinic_consultations = 0
        video_consultations = 0
        
        # Demographics
        male_count = 0
        female_count = 0
        other_count = 0
        
        # Today's date
        today = datetime.utcnow().date()
        today_start = datetime.combine(today, datetime.min.time())
        
        # Appointment requests (using alerts as pending requests)
        appointment_requests = []
        
        # Today's appointments (sessions)
        today_appointments = []
        
        # New vs old patients
        new_patients = 0
        old_patients = 0
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        for user in users:
            try:
                user_id = user.get('id')
                if not user_id:
                    print(f"[WARNING] User missing ID: {user.get('username', 'Unknown')}")
                    continue
                
                # Get user statistics with error handling
                try:
                    stats = firestore_service.get_user_statistics(user_id)
                except Exception as e:
                    print(f"[ERROR] Failed to get statistics for user {user_id}: {e}")
                    stats = {
                        'total_sessions': 0,
                        'average_depression_score': 0,
                        'risk_level': 'low',
                        'last_activity': user.get('created_at')
                    }
                
                # Count sessions
                user_sessions = stats.get('total_sessions', 0)
                total_sessions += user_sessions
                
                # Get user sessions for today and type analysis
                sessions = firestore_service.get_user_sessions(user_id)
                for session in sessions:
                    session_type = session.get('session_type', 'chatbot')
                    if session_type in ['voice', 'video', 'call']:
                        video_consultations += 1
                    elif session_type in ['clinic', 'in-person']:
                        clinic_consultations += 1
                    
                    # Check if session is today
                    start_time = session.get('start_time')
                    if start_time:
                        session_date = None
                        time_str = 'N/A'
                        
                        # Handle Firestore Timestamp objects
                        if hasattr(start_time, 'timestamp'):
                            try:
                                dt = datetime.fromtimestamp(start_time.timestamp())
                                session_date = dt.date()
                                time_str = dt.strftime('%H:%M')
                            except:
                                pass
                        elif isinstance(start_time, datetime):
                            session_date = start_time.date()
                            time_str = start_time.strftime('%H:%M')
                        elif isinstance(start_time, str):
                            try:
                                dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                                session_date = dt.date()
                                time_str = dt.strftime('%H:%M')
                            except:
                                pass
                        
                        if session_date and session_date == today:
                            today_appointments.append({
                                "user_id": user_id,
                                "username": user.get('username', 'Unknown'),
                                "type": session_type.replace('_', ' ').title(),
                                "time": time_str,
                                "status": "Ongoing" if not session.get('end_time') else "Completed"
                            })
                
                # Demographics (estimate from username/email or default)
                # In a real app, you'd have gender field
                # For now, distribute evenly
                if user_id:
                    hash_val = hash(user_id) % 3
                    if hash_val == 0:
                        male_count += 1
                    elif hash_val == 1:
                        female_count += 1
                    else:
                        other_count += 1
                
                # New vs old patients
                created_at = user.get('created_at')
                user_created = datetime.utcnow()
                
                if created_at:
                    # Handle Firestore Timestamp objects
                    if hasattr(created_at, 'timestamp'):
                        try:
                            user_created = datetime.fromtimestamp(created_at.timestamp())
                        except:
                            pass
                    elif isinstance(created_at, datetime):
                        user_created = created_at
                    elif isinstance(created_at, str):
                        try:
                            user_created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        except:
                            pass
                
                if user_created >= thirty_days_ago:
                    new_patients += 1
                else:
                    old_patients += 1
                
                dashboard_data.append({
                    "user_id": user_id,
                    "username": user.get('username', 'Unknown'),
                    "email": user.get('email', ''),
                    "total_sessions": stats.get('total_sessions', 0),
                    "total_mood_checkins": stats.get('total_mood_checkins', 0),
                    "average_depression_score": stats.get('average_depression_score', 0),
                    "risk_level": stats.get('risk_level', 'low'),
                    "last_activity": stats.get('last_activity')
                })
            except Exception as e:
                print(f"[ERROR] Error processing user {user.get('username', 'Unknown')}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        # Get appointment requests from alerts (unresolved alerts as requests)
        alerts = firestore_service.get_alerts(resolved=False)
        for alert in alerts[:5]:  # Limit to 5
            user_id = alert.get('user_id')
            user = firestore_service.get_user_by_id(user_id) if user_id else None
            username = user.get('username', 'Unknown') if user else 'Unknown'
            
            # Generate a date (use alert created_at or random)
            alert_date = alert.get('created_at')
            date_str = datetime.utcnow().strftime('%d %B %H:%M')
            
            if alert_date:
                # Handle Firestore Timestamp objects
                if hasattr(alert_date, 'timestamp'):
                    try:
                        dt = datetime.fromtimestamp(alert_date.timestamp())
                        date_str = dt.strftime('%d %B %H:%M')
                    except:
                        pass
                elif isinstance(alert_date, datetime):
                    date_str = alert_date.strftime('%d %B %H:%M')
                elif isinstance(alert_date, str):
                    try:
                        dt = datetime.fromisoformat(alert_date.replace('Z', '+00:00'))
                        date_str = dt.strftime('%d %B %H:%M')
                    except:
                        pass
            
            appointment_requests.append({
                "id": alert.get('id'),
                "user_id": user_id,
                "username": username,
                "details": f"{hash(user_id) % 50 + 20} {'Male' if hash(user_id) % 2 == 0 else 'Female'}, {date_str}",
                "status": "Pending"  # Can be "Confirmed" or "Declined"
            })
        
        # Sort today's appointments by time
        today_appointments.sort(key=lambda x: x.get('time', '00:00'))
        
        # Calculate demographics percentages
        total_demo = male_count + female_count + other_count
        if total_demo == 0:
            total_demo = 1
        
        print(f"[INFO] Returning dashboard data: {total_patients} patients, {total_sessions} sessions")
        
        return {
            "users": dashboard_data,
            "statistics": {
                "appointments": total_sessions,  # Using sessions as appointments
                "total_patients": total_patients,
                "clinic_consulting": clinic_consultations,
                "video_consulting": video_consultations,
                "new_patients": new_patients,
                "old_patients": old_patients,
                "new_patients_percent": round((new_patients / total_patients * 100) if total_patients > 0 else 0),
                "old_patients_percent": round((old_patients / total_patients * 100) if total_patients > 0 else 0)
            },
            "demographics": {
                "male": {"count": male_count, "percent": round((male_count / total_demo * 100))},
                "female": {"count": female_count, "percent": round((female_count / total_demo * 100))},
                "other": {"count": other_count, "percent": round((other_count / total_demo * 100))}
            },
            "appointment_requests": appointment_requests[:5],  # Limit to 5
            "today_appointments": today_appointments[:5]  # Limit to 5
        }
        
    except Exception as e:
        print(f"[ERROR] Failed to get dashboard data: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to load dashboard data: {str(e)}")

@router.get("/alerts")
async def get_alerts(
    resolved: Optional[bool] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get admin alerts from Firestore (accessible by admin and sub-admin)"""
    require_admin_access(current_user)
    
    alerts = firestore_service.get_alerts(resolved=resolved)
    
    result = []
    for alert in alerts:
        user_id = alert.get('user_id')
        user = firestore_service.get_user_by_id(user_id) if user_id else None
        
        result.append({
            "id": alert.get('id'),
            "user_id": user_id,
            "username": user.get('username', 'Unknown') if user else "Unknown",
            "alert_type": alert.get('alert_type'),
            "severity": alert.get('severity'),
            "message": alert.get('message'),
            "is_resolved": alert.get('is_resolved', False),
            "created_at": alert.get('created_at')
        })
    
    return {"alerts": result}

@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,  # Changed from int to str
    current_user: dict = Depends(get_current_user)
):
    """Resolve an alert in Firestore (accessible by admin and sub-admin)"""
    require_admin_access(current_user)
    
    # Check if alert exists
    alerts = firestore_service.get_alerts()
    alert_exists = any(a.get('id') == alert_id for a in alerts)
    
    if not alert_exists:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    firestore_service.resolve_alert(alert_id)
    
    return {"message": "Alert resolved", "alert_id": alert_id}

@router.get("/users/{user_id}/profile")
async def get_user_profile(
    user_id: str,  # Changed from int to str
    current_user: dict = Depends(get_current_user)
):
    """Get detailed user profile from Firestore including mood check-ins (accessible by admin and sub-admin)"""
    require_admin_access(current_user)
    
    user = firestore_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get digital twin
    digital_twin = firestore_service.get_digital_twin(user_id)
    
    # Get all sessions
    sessions = firestore_service.get_user_sessions(user_id)
    
    # Get all mood check-ins
    mood_checkins = firestore_service.get_user_mood_checkins(user_id, limit=200)
    
    # Create a mapping of session_id to mood check-ins (for linked check-ins)
    mood_by_session_id = {}
    for checkin in mood_checkins:
        session_id = checkin.get('session_id')
        if session_id:
            # Use the most recent mood for each session
            if session_id not in mood_by_session_id:
                mood_by_session_id[session_id] = checkin.get('mood')
    
    # Helper function to parse datetime from various formats (including Firestore timestamps)
    def parse_datetime(dt_value):
        if dt_value is None:
            return None
        if isinstance(dt_value, datetime):
            return dt_value
        # Handle Firestore Timestamp objects
        if hasattr(dt_value, 'timestamp'):
            try:
                return datetime.fromtimestamp(dt_value.timestamp())
            except:
                pass
        if isinstance(dt_value, str):
            try:
                # Try ISO format
                return datetime.fromisoformat(dt_value.replace('Z', '+00:00'))
            except:
                pass
        return None
    
    # Match mood check-ins to sessions by time proximity (within 1 hour of session start)
    from datetime import timedelta
    sessions_with_mood = []
    for session in sessions:
        session_id = session.get('id')
        session_mood = session.get('mood')  # Check if mood is already in session
        
        # If mood not in session, try to match from mood check-ins by session_id
        if not session_mood and session_id in mood_by_session_id:
            session_mood = mood_by_session_id[session_id]
        
        # If still no mood, try to match by time proximity (within 1 hour of session start)
        if not session_mood:
            session_start = parse_datetime(session.get('start_time'))
            if session_start:
                one_hour_after = session_start + timedelta(hours=1)
                one_hour_before = session_start - timedelta(hours=1)
                
                # Find mood check-ins within 1 hour of session start
                for checkin in mood_checkins:
                    checkin_time = parse_datetime(checkin.get('created_at'))
                    if checkin_time and one_hour_before <= checkin_time <= one_hour_after:
                        session_mood = checkin.get('mood')
                        # Also update the session with this mood for future reference
                        try:
                            firestore_service.update_session(session_id, {'mood': session_mood})
                        except:
                            pass
                        break
        
        sessions_with_mood.append({
            "id": session_id,
            "type": session.get('session_type'),
            "start_time": session.get('start_time'),
            "depression_score": session.get('depression_score'),
            "risk_level": session.get('risk_level'),
            "mood": session_mood  # Include mood from session or matched check-in
        })
    
    # Get user statistics (includes mood-based risk)
    stats = firestore_service.get_user_statistics(user_id)
    
    return {
        "user": {
            "id": user.get('id'),
            "username": user.get('username'),
            "email": user.get('email'),
            "phone_number": user.get('phone_number'),
            "created_at": user.get('created_at')
        },
        "statistics": {
            "total_sessions": stats.get('total_sessions', 0),
            "total_mood_checkins": stats.get('total_mood_checkins', 0),
            "recent_mood_checkins": stats.get('recent_mood_checkins', 0),
            "average_depression_score": stats.get('average_depression_score', 0),
            "risk_level": stats.get('risk_level', 'low'),
            "last_activity": stats.get('last_activity')
        },
        "digital_twin": digital_twin.get('mental_health_profile') if digital_twin else None,
        "sessions": sessions_with_mood,
        "mood_checkins": [
            {
                "id": m.get('id'),
                "mood": m.get('mood'),
                "notes": m.get('notes'),
                "created_at": m.get('created_at'),
                "date": m.get('date')
            }
            for m in mood_checkins[:50]  # Return most recent 50
        ]
    }

@router.get("/mood-checkins")
async def get_all_mood_checkins(
    limit: int = 100,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    user_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get all mood check-ins (accessible by admin and sub-admin)"""
    require_admin_access(current_user)
    
    checkins = firestore_service.get_all_mood_checkins(
        limit=limit,
        start_date=start_date,
        end_date=end_date,
        user_id=user_id
    )
    
    # Enrich with user information
    result = []
    for checkin in checkins:
        user = firestore_service.get_user_by_id(checkin['user_id'])
        result.append({
            'id': checkin['id'],
            'user_id': checkin['user_id'],
            'username': user.get('username', 'Unknown') if user else 'Unknown',
            'email': user.get('email', '') if user else '',
            'mood': checkin['mood'],
            'notes': checkin.get('notes'),
            'created_at': checkin['created_at'],
            'date': checkin.get('date', datetime.now().date().isoformat())
        })
    
    return {"checkins": result}

@router.get("/users")
async def get_all_users(
    current_user: dict = Depends(get_current_user)
):
    """Get all users including admins, sub-admins, doctors, and nurses (accessible by admin and sub-admin)"""
    require_admin_access(current_user)
    
    try:
        # Get all users including admins for the Settings page
        users_ref = firestore_service.db.collection('users')
        users = []
        user_ids_seen = set()
        
        for doc in users_ref.stream():
            try:
                user_data = doc.to_dict()
                if not user_data:
                    continue
                
                # Use document ID as the primary identifier
                doc_id = doc.id
                if doc_id in user_ids_seen:
                    continue
                user_ids_seen.add(doc_id)
                
                # Ensure id field is set to document ID (this is the actual Firestore document ID)
                user_data['id'] = doc_id
                user_data['document_id'] = doc_id  # Also store separately for clarity
                
                # Only include active users (exclude soft-deleted users)
                if user_data.get('is_active', True):  # Default to True if field is missing
                    users.append(user_data)
            except Exception as e:
                print(f"[ERROR] Error processing user document {doc.id}: {e}")
                continue
        
        # Sort by created_at descending
        users.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return {"users": users}
    except Exception as e:
        print(f"[ERROR] Failed to get users: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to retrieve users")

@router.post("/users/create")
async def create_user(
    user_data: CreateUserRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create a new user (full admin only - sub-admins cannot create users)"""
    require_full_admin(current_user)
    
    try:
        # Check if username already exists
        if firestore_service.get_user_by_username(user_data.username):
            raise HTTPException(status_code=400, detail="Username already exists")
        
        # Check if email already exists
        if firestore_service.get_user_by_email(user_data.email):
            raise HTTPException(status_code=400, detail="Email already exists")
        
        # Hash password using the same method as in auth.py
        from app.routes.auth import get_password_hash
        hashed_password = get_password_hash(user_data.password)
        
        # Validate role if provided
        if user_data.role and user_data.role not in ['doctor', 'nurse']:
            raise HTTPException(status_code=400, detail="Role must be 'doctor' or 'nurse'")
        
        # Ensure doctors and nurses are NOT automatically sub-admins unless explicitly set
        # Only allow sub-admin status if explicitly requested AND not a doctor/nurse by default
        is_sub_admin_value = user_data.is_sub_admin
        
        # If role is doctor or nurse, sub-admin must be explicitly set (not automatic)
        # For now, we'll allow it to be set explicitly, but default to False
        if user_data.role in ['doctor', 'nurse']:
            # Doctors and nurses are regular users by default, not sub-admins
            # Only set as sub-admin if explicitly requested
            is_sub_admin_value = user_data.is_sub_admin if user_data.is_sub_admin else False
        
        # Create user data - Use 'hashed_password' to match auth.py login expectation
        user_dict = {
            'username': user_data.username,
            'email': user_data.email,
            'hashed_password': hashed_password,  # Changed from 'password_hash' to 'hashed_password'
            'phone_number': user_data.phone_number,
            'is_admin': user_data.is_admin,
            'is_sub_admin': is_sub_admin_value,  # Use the processed value
            'is_active': True,
            'created_at': datetime.utcnow().isoformat()
        }
        
        # Add role-specific fields
        if user_data.role:
            user_dict['role'] = user_data.role
            if user_data.role == 'doctor' and user_data.specialization:
                user_dict['specialization'] = user_data.specialization
            # These fields will be updated by the user after account creation
            user_dict['description'] = None  # Can be updated later
            user_dict['profile_image_url'] = None  # Can be updated later
        
        # Create user in Firestore
        user_id = firestore_service.create_user(user_dict)
        
        # Return created user (without password)
        created_user = firestore_service.get_user_by_id(user_id)
        if created_user:
            created_user.pop('hashed_password', None)
            created_user.pop('password_hash', None)  # Remove both in case of legacy data
        
        return {
            "message": "User created successfully",
            "user": created_user,
            "user_id": user_id
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Failed to create user: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")

class UpdateUserRequest(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    role: Optional[str] = None
    specialization: Optional[str] = None
    is_sub_admin: Optional[bool] = None
    is_admin: Optional[bool] = None

@router.put("/users/{user_id}")
async def update_user_profile(
    user_id: str,
    user_data: UpdateUserRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update user profile (full admin only - sub-admins cannot edit users)"""
    require_full_admin(current_user)
    
    try:
        # Find the user - user_id should be the document ID from get_all_users
        users_ref = firestore_service.db.collection('users')
        user = None
        doc_id = user_id  # user_id should be the document ID
        
        # Try direct document ID first
        user_doc = users_ref.document(user_id).get()
        if user_doc.exists:
            user = user_doc.to_dict()
        else:
            # Fallback: search by id field
            query = users_ref.where('id', '==', user_id).limit(1).stream()
            for doc in query:
                doc_id = doc.id
                user = doc.to_dict()
                break
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Store the document ID for updates (user_id parameter is the route param, doc_id is the actual document ID)
        actual_doc_id = doc_id
        
        # Prevent editing admin status unless you're a full admin
        if user_data.is_admin is not None and not current_user.get('is_admin', False):
            raise HTTPException(status_code=403, detail="Only full administrators can change admin status")
        
        # Build update dictionary
        updates = {}
        if user_data.username is not None:
            # Check if username already exists (for another user)
            existing_user = firestore_service.get_user_by_username(user_data.username)
            if existing_user:
                existing_doc_id = existing_user.get('id') or existing_user.get('document_id')
                if existing_doc_id and str(existing_doc_id) != str(actual_doc_id):
                    raise HTTPException(status_code=400, detail="Username already exists")
            updates['username'] = user_data.username
        
        if user_data.email is not None:
            # Check if email already exists (for another user)
            existing_user = firestore_service.get_user_by_email(user_data.email)
            if existing_user:
                existing_doc_id = existing_user.get('id') or existing_user.get('document_id')
                if existing_doc_id and str(existing_doc_id) != str(actual_doc_id):
                    raise HTTPException(status_code=400, detail="Email already exists")
            updates['email'] = user_data.email
        
        if user_data.phone_number is not None:
            updates['phone_number'] = user_data.phone_number
        
        if user_data.role is not None:
            if user_data.role not in ['doctor', 'nurse', '']:
                raise HTTPException(status_code=400, detail="Role must be 'doctor', 'nurse', or empty")
            updates['role'] = user_data.role if user_data.role else None
            # Clear specialization if role is not doctor
            if user_data.role != 'doctor':
                updates['specialization'] = None
            # When setting role to doctor or nurse, ensure they are NOT sub-admins by default
            # Only if is_sub_admin is explicitly provided, use it; otherwise default to False
            if user_data.role in ['doctor', 'nurse']:
                if user_data.is_sub_admin is None:
                    # Role changed to doctor/nurse but sub_admin not specified - default to False
                    updates['is_sub_admin'] = False
        
        if user_data.specialization is not None:
            if user_data.role == 'doctor' or user.get('role') == 'doctor':
                updates['specialization'] = user_data.specialization if user_data.specialization else None
            else:
                updates['specialization'] = None
        
        if user_data.is_sub_admin is not None:
            # If explicitly setting sub_admin status, use the provided value
            updates['is_sub_admin'] = user_data.is_sub_admin
        
        if user_data.is_admin is not None:
            updates['is_admin'] = user_data.is_admin
            # If setting as admin, clear sub-admin status (admins cannot be sub-admins)
            if user_data.is_admin:
                updates['is_sub_admin'] = False
        
        if updates:
            # Use the document ID for update
            firestore_service.update_user(actual_doc_id, updates)
        
        # Return updated user using document ID
        updated_doc = users_ref.document(actual_doc_id).get()
        if updated_doc.exists:
            user_dict = updated_doc.to_dict()
            if user_dict:
                user_dict['id'] = actual_doc_id  # Ensure id is set
                user_dict.pop('hashed_password', None)
                user_dict.pop('password_hash', None)  # Remove both for safety
        else:
            raise HTTPException(status_code=404, detail="Updated user not found")
        
        return {
            "message": "User updated successfully",
            "user": user_dict
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Failed to update user: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to update user: {str(e)}")

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a user (full admin only - sub-admins cannot delete users)"""
    require_full_admin(current_user)
    
    # Prevent deleting yourself
    if str(current_user.get('id')) == str(user_id):
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    
    try:
        # Find the user document - user_id should be the document ID from get_all_users
        users_ref = firestore_service.db.collection('users')
        user = None
        doc_id = user_id  # user_id should be the document ID from get_all_users
        
        # Try direct document ID first (user_id should be the document ID)
        try:
            user_doc = users_ref.document(user_id).get()
            if user_doc.exists:
                user = user_doc.to_dict()
                print(f"[INFO] Found user by document ID: {user_id}")
            else:
                # If not found, search by id field (fallback)
                print(f"[WARNING] User not found by document ID {user_id}, searching by id field...")
                query = users_ref.where('id', '==', user_id).limit(1).stream()
                for doc in query:
                    doc_id = doc.id
                    user = doc.to_dict()
                    print(f"[INFO] Found user by id field query: document_id={doc_id}, user_id={user_id}")
                    break
        except Exception as e:
            print(f"[ERROR] Error searching for user {user_id}: {e}")
            raise HTTPException(status_code=404, detail=f"User not found: {str(e)}")
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Prevent deleting main admins (only if not main admin)
        if user.get('is_admin') and not current_user.get('is_admin', False):
            raise HTTPException(status_code=403, detail="Cannot delete main administrator accounts")
        
        # Delete the user document using the document ID
        try:
            users_ref.document(doc_id).delete()
            print(f"[INFO] User document {doc_id} deleted successfully")
        except Exception as e:
            print(f"[ERROR] Failed to delete user document {doc_id}: {e}")
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Failed to delete user: {str(e)}")
        
        return {"message": "User deleted successfully", "user_id": user_id, "document_id": doc_id}
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Failed to delete user: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to delete user")

