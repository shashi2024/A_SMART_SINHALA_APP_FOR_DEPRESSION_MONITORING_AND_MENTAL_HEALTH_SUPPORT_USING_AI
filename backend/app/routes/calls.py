"""
Call routes for real-time voice/video calling
Supports counselor calls and AI practice calls (Duolingo-style)
"""

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
import json

from app.routes.auth import get_current_user
from app.services.call_service import CallService, CallType, CallStatus
from app.services.firestore_service import FirestoreService
from app.services.chatbot_service import ChatbotService
from app.services.voice_call_service import voice_call_service
import base64

router = APIRouter()
call_service = CallService()
firestore_service = FirestoreService()
chatbot_service = ChatbotService()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, call_id: str):
        await websocket.accept()
        self.active_connections[call_id] = websocket
    
    def disconnect(self, call_id: str):
        if call_id in self.active_connections:
            del self.active_connections[call_id]
    
    async def send_personal_message(self, message: dict, call_id: str):
        if call_id in self.active_connections:
            await self.active_connections[call_id].send_json(message)

manager = ConnectionManager()

# ========== Request/Response Models ==========

class CreateCallRequest(BaseModel):
    call_type: str  # "counselor", "ai_practice", "emergency"
    callee_id: Optional[str] = None  # For counselor calls
    language: str = "en"

class CallResponse(BaseModel):
    call_id: str
    caller_id: str
    callee_id: Optional[str]
    call_type: str
    status: str
    language: str
    started_at: str

class WebRTCSignalRequest(BaseModel):
    call_id: str
    offer: Optional[str] = None
    answer: Optional[str] = None
    ice_candidate: Optional[Dict] = None

# ========== REST Endpoints ==========

@router.post("/create", response_model=CallResponse)
async def create_call(
    request: CreateCallRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new call session
    """
    caller_id = current_user.get('id')
    
    # Validate call type
    try:
        call_type = CallType(request.call_type)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid call_type. Must be one of: {[e.value for e in CallType]}"
        )
    
    # For counselor calls, validate callee_id
    if call_type == CallType.COUNSELOR and not request.callee_id:
        raise HTTPException(
            status_code=400,
            detail="callee_id is required for counselor calls"
        )
    
    # Create call
    call_data = call_service.create_call(
        caller_id=caller_id,
        call_type=call_type,
        callee_id=request.callee_id,
        language=request.language
    )
    
    # Map 'id' to 'call_id' for response
    call_data["call_id"] = call_data.pop("id")
    
    # If AI practice call, update status to connected immediately
    if call_type == CallType.AI_PRACTICE:
        call_service.update_call_status(call_data["call_id"], CallStatus.CONNECTED)
        call_data["status"] = CallStatus.CONNECTED.value
    
    return CallResponse(**call_data)

# NOTE: Static routes must come BEFORE dynamic routes like /{call_id}
@router.get("/history")
async def get_call_history(
    call_type: Optional[str] = None,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """Get user's call history"""
    print(f"[DEBUG] get_call_history called, user: {current_user}")
    user_id = current_user.get('id')
    
    call_type_enum = None
    if call_type:
        try:
            call_type_enum = CallType(call_type)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid call_type")
    
    calls = call_service.get_user_calls(user_id, call_type_enum, limit)
    
    return {
        "calls": calls,
        "total": len(calls)
    }

@router.get("/counselors/available")
async def get_available_counselors(
    language: str = "en",
    current_user: dict = Depends(get_current_user)
):
    """Get list of available counselors"""
    counselors = call_service.get_available_counselors(language)
    return {
        "counselors": counselors,
        "language": language
    }

@router.get("/{call_id}", response_model=CallResponse)
async def get_call(
    call_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get call details"""
    call = call_service.get_call(call_id)
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    
    # Verify user is part of the call
    user_id = current_user.get('id')
    if call["caller_id"] != user_id and call.get("callee_id") != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return CallResponse(**call)

@router.post("/{call_id}/end")
async def end_call(
    call_id: str,
    current_user: dict = Depends(get_current_user)
):
    """End a call"""
    call = call_service.get_call(call_id)
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    
    user_id = current_user.get('id')
    if call["caller_id"] != user_id and call.get("callee_id") != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    success = call_service.end_call(call_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to end call")
    
    # Notify other party via WebSocket
    await manager.send_personal_message({
        "type": "call_ended",
        "call_id": call_id
    }, call_id)
    
    return {"message": "Call ended", "call_id": call_id}

@router.post("/{call_id}/reject")
async def reject_call(
    call_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Reject an incoming call"""
    call = call_service.get_call(call_id)
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    
    user_id = current_user.get('id')
    if call.get("callee_id") != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    call_service.update_call_status(call_id, CallStatus.REJECTED)
    
    # Notify caller via WebSocket
    await manager.send_personal_message({
        "type": "call_rejected",
        "call_id": call_id
    }, call_id)
    
    return {"message": "Call rejected", "call_id": call_id}

# ========== WebSocket Endpoint for Real-time Signaling ==========

@router.websocket("/ws/{call_id}")
async def websocket_endpoint(websocket: WebSocket, call_id: str):
    """
    WebSocket endpoint for AI voice chat
    Handles voice messages and returns AI responses
    """
    await manager.connect(websocket, call_id)
    
    # Get call info
    call = call_service.get_call(call_id)
    language = call.get("language", "en") if call else "en"
    user_id = call.get("caller_id", "unknown") if call else "unknown"
    
    try:
        # Send greeting when call connects (for AI practice calls)
        if call and call.get("call_type") == "ai_practice":
            greeting = voice_call_service.get_greeting(language)
            await websocket.send_json({
                "type": "bot_response",
                "text": greeting["text"],
                "audio": greeting.get("audio"),  # Base64 encoded MP3
                "call_id": call_id
            })
            print(f"[CALL] Sent greeting for call {call_id}")
        
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            if message_type == "voice_message":
                # User sent voice audio
                audio_base64 = data.get("audio")
                if audio_base64:
                    try:
                        audio_data = base64.b64decode(audio_base64)
                        
                        # Process voice message (STT -> Chatbot -> TTS)
                        response = voice_call_service.process_voice_message(
                            audio_data=audio_data,
                            user_id=user_id,
                            session_id=call_id,
                            language=language
                        )
                        
                        # Send response back
                        await websocket.send_json({
                            "type": "bot_response",
                            "user_text": response.get("user_text"),
                            "text": response.get("bot_text"),
                            "audio": response.get("bot_audio"),
                            "error": response.get("error"),
                            "call_id": call_id
                        })
                        print(f"[CALL] Processed voice message for call {call_id}")
                        
                    except Exception as e:
                        print(f"[ERROR] Voice processing failed: {e}")
                        await websocket.send_json({
                            "type": "error",
                            "message": "Failed to process voice message",
                            "call_id": call_id
                        })
            
            elif message_type == "text_message":
                # User sent text (fallback)
                text = data.get("text", "")
                if text:
                    try:
                        chat_response = chatbot_service.get_response(
                            message=text,
                            user_id=user_id,
                            session_id=call_id,
                            language=language
                        )
                        bot_text = chat_response.get("response", "")
                        
                        # Generate audio for response
                        audio = voice_call_service.text_to_speech(bot_text, language)
                        audio_base64 = base64.b64encode(audio).decode('utf-8') if audio else None
                        
                        await websocket.send_json({
                            "type": "bot_response",
                            "user_text": text,
                            "text": bot_text,
                            "audio": audio_base64,
                            "call_id": call_id
                        })
                    except Exception as e:
                        print(f"[ERROR] Text processing failed: {e}")
            
            elif message_type == "offer":
                # WebRTC signaling (keep for compatibility)
                call_service.update_call_status(
                    call_id,
                    CallStatus.RINGING,
                    webrtc_offer=data.get("offer")
                )
                await manager.send_personal_message({
                    "type": "offer",
                    "offer": data.get("offer"),
                    "call_id": call_id
                }, call_id)
            
            elif message_type == "answer":
                call_service.update_call_status(
                    call_id,
                    CallStatus.CONNECTED,
                    webrtc_answer=data.get("answer")
                )
                await manager.send_personal_message({
                    "type": "answer",
                    "answer": data.get("answer"),
                    "call_id": call_id
                }, call_id)
            
            elif message_type == "ice_candidate":
                call_service.update_call_status(
                    call_id,
                    CallStatus.CONNECTED,
                    ice_candidate=data.get("candidate")
                )
                await manager.send_personal_message({
                    "type": "ice_candidate",
                    "candidate": data.get("candidate"),
                    "call_id": call_id
                }, call_id)
            
            elif message_type == "call_ended":
                call_service.end_call(call_id)
                await manager.send_personal_message({
                    "type": "call_ended",
                    "call_id": call_id
                }, call_id)
                break
    
    except WebSocketDisconnect:
        manager.disconnect(call_id)
        call_service.end_call(call_id)






