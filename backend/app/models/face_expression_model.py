# app/models/face_expression_model.py
import cv2
import numpy as np
import tensorflow as tf
from pathlib import Path
from typing import Any

# Model paths
MODEL_PATH_H5 = Path(__file__).parent.parent.parent / "models" / "Bio_Feedback" / "best_expression_model.h5"
MODEL_PATH_KERAS = Path(__file__).parent.parent.parent / "models" / "Bio_Feedback" / "best_model.keras"
MODEL_PATH_EXPRESSION_KERAS = Path(__file__).parent.parent.parent / "models" / "Bio_Feedback" / "best_expression_model.keras"

# Global variables
model = None
CLASS_NAMES = ["angry", "fear", "happy", "neutral", "sad", "surprise"]

def load_model_safe():
    """Safely load the Keras model with multiple fallback methods"""
    global model
    # Log model directory contents for debugging
    model_dir = Path(__file__).parent.parent.parent / "models" / "Bio_Feedback"
    try:
        entries = [p.name for p in model_dir.glob("*")]
        print(f"Model dir: {model_dir}")
        print(f"Contents: {entries}")
    except Exception as e:
        print(f"Could not list model dir {model_dir}: {e}")

    # Prefer native Keras 3 loader for .keras format
    if MODEL_PATH_KERAS.exists():
        try:
            import os as _os
            _os.environ.setdefault("KERAS_BACKEND", "tensorflow")
            import keras

            # Compatibility shim for models saved with differing InputLayer configs
            class CompatInputLayer(keras.layers.InputLayer):
                def __init__(self, *args, batch_shape=None, batch_input_shape=None, dtype=None, sparse=False, ragged=False, name=None, **kwargs):
                    # Normalize batch shape args to Keras 3 signature
                    bs = None
                    shp = None
                    if batch_shape is not None:
                        # batch_shape like [None, H, W, C]
                        try:
                            bs = batch_shape[0]
                            shp = batch_shape[1:]
                        except Exception:
                            pass
                    elif batch_input_shape is not None:
                        try:
                            bs = batch_input_shape[0]
                            shp = batch_input_shape[1:]
                        except Exception:
                            pass
                    # Remove any unknown args before calling super
                    if 'batch_shape' in kwargs:
                        kwargs.pop('batch_shape', None)
                    if 'batch_input_shape' in kwargs:
                        kwargs.pop('batch_input_shape', None)
                    super().__init__(shape=shp, batch_size=bs, dtype=dtype, sparse=sparse, ragged=ragged, name=name, **kwargs)

            custom_objects = {"InputLayer": CompatInputLayer}
            model = keras.models.load_model(str(MODEL_PATH_KERAS), custom_objects=custom_objects)
            print("✓ Model loaded successfully from .keras using Keras 3!")
            return True
        except Exception as e2:
            print(f"✗ Keras (.keras) loading failed: {e2}")

    # Fallback: HDF5 (from Google Colab training)
    if MODEL_PATH_H5.exists():
        try:
            model = tf.keras.models.load_model(str(MODEL_PATH_H5), compile=False)
            print("✓ Model loaded successfully from HDF5!")
            return True
        except Exception as e1:
            print(f"✗ HDF5 loading failed: {e1}")

    # Try expression keras if best_model failed
    if model is None and MODEL_PATH_EXPRESSION_KERAS.exists():
        try:
            import os as _os
            _os.environ.setdefault("KERAS_BACKEND", "tensorflow")
            import keras
            from .face_expression_model import CompatInputLayer
            custom_objects = {"InputLayer": CompatInputLayer}
            model = keras.models.load_model(str(MODEL_PATH_EXPRESSION_KERAS), custom_objects=custom_objects)
            print("✓ Model loaded successfully from expression .keras using Keras 3!")
            return True
        except Exception as e3:
            print(f"✗ Keras (expression .keras) loading failed: {e3}")

    print("\n⚠️  Model files not found or could not be loaded!")
    print(f"Expected .h5 file at: {MODEL_PATH_H5}")
    print(f"Expected .keras file at: {MODEL_PATH_KERAS}")
    print(f"Expected expression .keras file at: {MODEL_PATH_EXPRESSION_KERAS}")
    return False

def human_face_expression_local(image_file: Any) -> dict:
    """Analyze an image using the local TensorFlow model."""
    global model
    if model is None:
        if not load_model_safe():
            return {"status": False, "error": "Local model not loaded", "expression": None}

    try:
        import numpy as np
        import cv2

        # 1. Read image from UploadFile or file-like object
        if hasattr(image_file, "file"):
            image_file.file.seek(0)
            contents = image_file.file.read()
            image_file.file.seek(0)
        elif hasattr(image_file, "read"):
            image_file.seek(0)
            contents = image_file.read()
            image_file.seek(0)
        else:
            return {"status": False, "error": "Invalid image input"}

        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return {"status": False, "error": "Could not decode image"}

        # 2. Preprocessing (Resize to 128x128 to match model training)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        resized = cv2.resize(img_rgb, (128, 128))
        normalized = resized / 255.0
        input_tensor = np.expand_dims(normalized, axis=0)

        # 3. Predict
        preds = model.predict(input_tensor, verbose=0)
        idx = np.argmax(preds)
        expression = CLASS_NAMES[idx]
        
        # Stress mapping
        stress_level_map = {
            "angry": "high",
            "fear": "high",
            "happy": "low",
            "neutral": "low",
            "sad": "medium",
            "surprise": "medium"
        }

        return {
            "status": True,
            "error": None,
            "expression": expression,
            "stress_level": stress_level_map.get(expression, "medium")
        }
    except Exception as e:
        return {"status": False, "error": str(e), "expression": None}

# Load the model at import time
print("Loading face expression model...")
load_model_safe()
print(f"{'='*50}")
print("Face expression model loading complete!")
print(f"{'='*50}\n")
