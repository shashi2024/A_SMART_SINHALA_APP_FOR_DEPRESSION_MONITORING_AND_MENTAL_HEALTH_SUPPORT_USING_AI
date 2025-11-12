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

from app.routes import auth, chatbot, voice, typing, admin, digital_twin
from app.database import init_db
from app.config import settings

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

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await init_db()

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

