from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Form
from pydantic import BaseModel
from typing import Optional, List
import json

import cv2
import numpy as np
import tensorflow as tf

import torch                     
import torch.nn.functional as F  

from pathlib import Path
from app.models.voice_stress_model_ai import human_voice_stress
from app.models.voice_stress_openai import human_voice_stress_openai
from app.models.face_expression_model_ai import human_face_expression
from app.models.face_expression_openai import human_face_expression_openai
from app.models.face_expression_model import model, CLASS_NAMES, human_face_expression_local
from app.utils.extract_w2v_embeddings import extract_w2v_embedding
from app.models.movement_caption import analyze_activity
from app.models.heartrate_measure import analyze_stress
from app.routes.auth import get_current_user_optional
from app.services.firestore_service import FirestoreService

firestore_service = FirestoreService()


router = APIRouter(prefix="/api", tags=["data"])

@router.get("/analyze/biofeedback/latest")
async def get_latest_biofeedback(user_id: str):
    """Get the latest biofeedback analysis for a user"""
    try:
        analyses = firestore_service.get_user_biofeedback_analyses(user_id, limit=1)
        if not analyses:
            return {"status": "success", "results": None}
        return {"status": "success", "results": analyses[0]}
    except Exception as e:
        print(f"[ERROR] Failed to fetch latest biofeedback: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch latest biofeedback: {str(e)}")

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
        # Use local model as requested
        result = human_face_expression_local(image)
        
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
        # Use OpenAI as requested for biofeedback
        result = human_voice_stress_openai(audio)
        
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
def analyze_activity_endpoint(
    payload: ActivityPayload,
    user_id: Optional[str] = None  # Make it optional for backward compatibility
):
    result = analyze_activity([s.dict() for s in payload.accelerometer_data])
    
    if user_id:
        # Save to Firestore as a partial biofeedback analysis
        firestore_service.create_biofeedback_analysis({
            "user_id": user_id,
            "movement": result,
            "created_at": datetime.utcnow().isoformat(),
            "final_assessment": {
                "risk_level": "low" if result.get("activity") in ["Sitting", "Standing"] else "moderate",
                "avg_stress_score": 1.0 if result.get("activity") in ["Sitting", "Standing"] else 2.0,
                "summary": f"Individual movement analysis: {result.get('activity')}"
            }
        })
    return result

@router.post("/analyze/heart-rate")
def analyze_stress_endpoint(
    payload: HRVPayload,
    user_id: Optional[str] = None
):
    result = analyze_stress(payload.rr_intervals)
    
    if user_id:
        # Map stress level to numeric for averaging
        stress_map = {"Relaxed": 1.0, "Normal": 2.0, "Elevated Stress": 3.0, "High Stress": 4.0}
        stress_score = stress_map.get(result.get("stress_level"), 2.0)
        
        # Save to Firestore
        firestore_service.create_biofeedback_analysis({
            "user_id": user_id,
            "heart_rate": result,
            "created_at": datetime.utcnow().isoformat(),
            "final_assessment": {
                "risk_level": result.get("stress_level", "low"),
                "avg_stress_score": stress_score,
                "summary": f"Individual heart rate analysis: {result.get('stress_level')}"
            }
        })
    return result

@router.post("/analyze/biofeedback")
async def analyze_biofeedback(
    user_id: Optional[str] = None,
    accelerometer_data: str = Form(...),  # JSON string
    rr_intervals: str = Form(...),       # JSON string (CSV or list)
    image: Optional[UploadFile] = File(None),
    audio: Optional[UploadFile] = File(None),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Unified endpoint for 4-sensor biofeedback analysis.
    Processes Face (image), Voice (audio), Movement (accel), and Heart Rate (rr).
    """
    from datetime import datetime, timezone
    
    try:
        results = {
            "user_id": user_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sensors": {}
        }

        # 1. Analyze Movement (Accelerometer)
        try:
            acc_list = json.loads(accelerometer_data)
            movement_result = analyze_activity(acc_list)
            results["sensors"]["movement"] = movement_result
        except Exception as e:
            results["sensors"]["movement"] = {"error": str(e)}

        # 2. Analyze Heart Rate (HRV)
        try:
            hr_list = json.loads(rr_intervals)
            hr_result = analyze_stress(hr_list)
            results["sensors"]["heart_rate"] = hr_result
        except Exception as e:
            results["sensors"]["heart_rate"] = {"error": str(e)}

        # 3 & 4. Parallel AI analysis for Face and Voice
        import concurrent.futures
        
        def run_face_analysis(img_file):
            if not img_file:
                return {"error": "No image provided"}
            try:
                print(f"[INFO] Analyzing face expression for user {user_id} (Local Model)...")
                res = human_face_expression_local(img_file)
                print(f"[INFO] Face result: {res.get('expression', 'None')}")
                return res
            except Exception as e:
                print(f"[ERROR] Face analysis failed: {e}")
                return {"error": str(e)}

        def run_voice_analysis(aud_file):
            if not aud_file:
                return {"error": "No audio provided"}
            try:
                print(f"[INFO] Analyzing voice stress for user {user_id} (OpenAI)...")
                res = human_voice_stress_openai(aud_file)
                print(f"[INFO] Voice result: {res.get('level', 'None')}")
                return res
            except Exception as e:
                print(f"[ERROR] Voice analysis failed: {e}")
                return {"error": str(e)}

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_face = executor.submit(run_face_analysis, image)
            future_voice = executor.submit(run_voice_analysis, audio)
            
            # Wait for both (or timeout after 45s)
            results["sensors"]["face"] = future_face.result(timeout=45)
            results["sensors"]["voice"] = future_voice.result(timeout=45)

        # 5. Calculation of Aggregate Assessment
        # Define base weights and extraction of scores
        base_weights = {
            "face": 0.35,
            "voice": 0.35,
            "heart_rate": 0.20,
            "movement": 0.10
        }
        
        sensor_scores = {}
        confidence_score = 0.50 # Base confidence
        
        # Face score mapping
        if "face" in results["sensors"] and not results["sensors"]["face"].get("error"):
            level = results["sensors"]["face"].get("stress_level")
            if level == "high": sensor_scores["face"] = 3.0
            elif level == "medium": sensor_scores["face"] = 2.0
            else: sensor_scores["face"] = 1.0
            confidence_score += 0.15
            
        # Voice score mapping
        if "voice" in results["sensors"] and not results["sensors"]["voice"].get("error"):
            level = results["sensors"]["voice"].get("level")
            if level == "high": sensor_scores["voice"] = 3.0
            elif level == "medium": sensor_scores["voice"] = 2.0
            else: sensor_scores["voice"] = 1.0
            confidence_score += 0.15
            
        # Heart rate score mapping
        if "heart_rate" in results["sensors"] and not results["sensors"]["heart_rate"].get("error"):
            level = results["sensors"]["heart_rate"].get("stress_level")
            if level == "High Stress": sensor_scores["heart_rate"] = 3.0
            elif level == "Elevated Stress": sensor_scores["heart_rate"] = 2.0
            else: sensor_scores["heart_rate"] = 1.0
            confidence_score += 0.10

        # Movement score mapping
        if "movement" in results["sensors"] and not results["sensors"]["movement"].get("error"):
            activity = results["sensors"]["movement"].get("activity")
            if activity == "Running": sensor_scores["movement"] = 2.5
            elif activity == "Walking": sensor_scores["movement"] = 1.5
            else: sensor_scores["movement"] = 1.0
            confidence_score += 0.05

        # Calculate weighted final risk
        if not sensor_scores:
            final_risk = "unknown"
            avg_weighted_score = 0.0
        else:
            # Re-normalize weights based on available sensors
            total_available_weight = sum(base_weights[s] for s in sensor_scores)
            avg_weighted_score = sum(sensor_scores[s] * (base_weights[s] / total_available_weight) for s in sensor_scores)
            
            # Application of updated thresholds
            if avg_weighted_score > 2.6: final_risk = "severe"
            elif avg_weighted_score > 2.1: final_risk = "high"
            elif avg_weighted_score > 1.4: final_risk = "moderate"
            else: final_risk = "low"

        results["final_assessment"] = {
            "risk_level": final_risk,
            "avg_stress_score": round(avg_weighted_score, 2),
            "confidence": round(confidence_score, 2),
            "summary": f"Calculated based on {len(sensor_scores)} contributing sensor factors."
        }

        # Save to Firestore
        firestore_service.create_biofeedback_analysis(results.copy())
        
        # Update user's global risk if the current assessment is higher
        user_ref = firestore_service.db.collection('users').document(user_id)
        user_ref.update({
            'risk_level': final_risk,
            'last_activity': datetime.now(timezone.utc).isoformat() + 'Z'
        })

        return {
            "status": "success",
            "results": results
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Bio-feedback analysis failed: {str(e)}")