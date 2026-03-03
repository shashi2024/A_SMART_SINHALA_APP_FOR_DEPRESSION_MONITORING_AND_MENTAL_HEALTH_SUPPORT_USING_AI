# app/models/face_expression_model.py
import cv2
import numpy as np
import tensorflow as tf
from pathlib import Path

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

# Load the model at import time
print("Loading face expression model...")
load_model_safe()
print(f"{'='*50}")
print("Face expression model loading complete!")
print(f"{'='*50}\n")
