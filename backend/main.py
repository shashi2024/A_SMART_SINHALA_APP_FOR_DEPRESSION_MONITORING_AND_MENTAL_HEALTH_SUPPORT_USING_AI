"""
Main FastAPI application for Depression Monitoring System
Handles API endpoints for chatbot, voice analysis, typing patterns, and admin panel
"""

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
from datetime import datetime

from app.config import settings
from app.services.firebase_service import initialize_firebase

# Initialize Firebase BEFORE importing routes (routes need FirestoreService)
# This ensures Firebase is ready when routes are imported
initialize_firebase()

from app.routes import auth, chatbot, voice, typing, admin, digital_twin, calls, mood, sessions

app = FastAPI(
    title="Depression Monitoring API",
    description="AI-powered depression detection and mental health support system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(chatbot.router, prefix="/api/chatbot", tags=["Chatbot"])
app.include_router(voice.router, prefix="/api/voice", tags=["Voice Analysis"])
app.include_router(typing.router, prefix="/api/typing", tags=["Typing Analysis"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin Panel"])
app.include_router(digital_twin.router, prefix="/api/digital-twin", tags=["Digital Twin"])
app.include_router(calls.router, prefix="/api/calls", tags=["Calls"])
app.include_router(mood.router, prefix="/api/mood", tags=["Mood Check-in"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["Sessions"])

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    # Firebase is already initialized before routes import
    # Just verify it's working
    from app.services.firebase_service import is_firebase_initialized
    if not is_firebase_initialized():
        print("⚠️  Warning: Firebase not initialized. Firestore features will not work.")
        print("   Please set FIREBASE_CREDENTIALS in .env file")
    else:
        print("✅ Firebase ready for use")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Depression Monitoring API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )

