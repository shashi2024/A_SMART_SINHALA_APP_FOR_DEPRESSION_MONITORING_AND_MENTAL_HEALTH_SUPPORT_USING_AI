from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List

import cv2
import numpy as np
import tensorflow as tf

import torch                     
import torch.nn.functional as F  

from pathlib import Path
from app.models.voice_stress_model_ai import human_voice_stress
from app.models.voice_stress_model import stress_model
from app.models.face_expression_model_ai import human_face_expression
from app.models.face_expression_model import model, CLASS_NAMES
from app.utils.extract_w2v_embeddings import extract_w2v_embedding
from app.models.movement_caption import analyze_activity
from app.models.heartrate_measure import analyze_stress


router = APIRouter(prefix="/api", tags=["data"])

class AccelerometerSample(BaseModel):
    x: float
    y: float
    z: float
    timestamp: str

class ActivityPayload(BaseModel):
    timestamp: str
    accelerometer_data: List[AccelerometerSample]

class HRVPayload(BaseModel):
    timestamp: str
    rr_intervals: List[float]

@router.get("/status")
async def service_status():
    """
    Check the status of the biofeedback service
    """
    return {"service": "Biofeedback API", "status": "operational"}

@router.post("/predict-expression")
async def predict_expression(image: UploadFile = File(...)):
    """
    Predict facial expression from an uploaded image
    
    - **image**: Image file (jpg, png, etc.) containing a face
    
    Returns the predicted expression (Angry, Disgust, Fear, Happy, Neutral, Sad, Surprise)
    """
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded. Please check server logs.")
    
    # Validate file type
    if not image.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Uploaded file must be an image")
    
    try:
        # Read image file
        contents = await image.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image file")
        
        # Convert BGR to RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Resize to model input size
        img_size = 128
        resized = cv2.resize(img_rgb, (img_size, img_size))
        
        # Normalize pixel values to [0, 1]
        normalized = resized / 255.0
        
        # Expand dimensions to match model input shape (1, 128, 128, 3)
        input_tensor = np.expand_dims(normalized, axis=0)
        
        # Make prediction
        preds = model.predict(input_tensor, verbose=0)
        predicted_class_idx = np.argmax(preds)
        predicted_class = CLASS_NAMES[predicted_class_idx]
        confidence = float(preds[0][predicted_class_idx])
        
        # Return all class probabilities
        all_predictions = {CLASS_NAMES[i]: float(preds[0][i]) for i in range(len(CLASS_NAMES))}
        
        return {
            "status": "success",
            "predicted_expression": predicted_class,
            "confidence": confidence,
            "all_predictions": all_predictions
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")
    

@router.post("/predict-expression-ai")
async def predict_expression_ai(image: UploadFile = File(...)):
   
    # Validate file type
    if not image.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Uploaded file must be an image")
    
    try:
        # Pass the entire UploadFile object to the AI function
        result = human_face_expression(image)
        
        if not result["status"]:
            raise HTTPException(status_code=500, detail=f"Expression analysis failed: {result['error']}")
        
        return {
            "status": "success",
            "predicted_expression": result["expression"],
            "stress_level": result["stress_level"],
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")


@router.post("/predict-voice-stress")
async def predict_stress(audio: UploadFile = File(...)):
    if audio.content_type not in [
        "audio/mpeg", "audio/wav", "audio/x-wav", "audio/mp3"
    ]:
        raise HTTPException(400, "Uploaded file must be mp3 or wav")

    try:
        audio_bytes = await audio.read()
        embedding = extract_w2v_embedding(audio_bytes)
        print("Embedding shape:", embedding.shape)

        with torch.no_grad():
            outputs = stress_model(embedding)
            probs = F.softmax(outputs.logits, dim=-1)

        return {
            "status": "success",
            "predicted_stress_level": (
                "stressed" if probs[0][1] > probs[0][0] else "not_stressed"
            ),
            "confidence": float(probs.max()),
            "probabilities": {
                "not_stressed": float(probs[0][0]),
                "stressed": float(probs[0][1]),
            }
        }

    except Exception as e:
        raise HTTPException(500, f"Error processing audio: {str(e)}")

@router.post("/predict-voice-stress-ai")
async def predict_stress(audio: UploadFile = File(...)):
    if audio.content_type not in [
        "audio/mpeg", "audio/wav", "audio/x-wav", "audio/mp3"
    ]:
        raise HTTPException(400, "Uploaded file must be mp3 or wav")

    try:
        # Pass the entire UploadFile object
        result = human_voice_stress(audio)
        
        if not result["status"]:
            raise HTTPException(500, f"Stress analysis failed: {result['error']}")
        
        return {
            "status": "success",
            "stress_score": result["score"],
            "stress_level": result["level"],
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Error processing audio: {str(e)}")


@router.post("/analyze/activity")
def analyze_activity_endpoint(payload: ActivityPayload):
    result = analyze_activity([s.dict() for s in payload.accelerometer_data])
    return result

@router.post("/analyze/heart-rate")
def analyze_stress_endpoint(payload: HRVPayload):
    result = analyze_stress(payload.rr_intervals)
    return result