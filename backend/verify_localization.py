
import sys
import os

# Add the current directory to sys.path
sys.path.append(os.getcwd())

try:
    from app.services.phq9_service import PHQ9Service
    service = PHQ9Service()
    print("PHQ9Service imported successfully")
    
    score = 10
    interpretation = service.interpret_score(score, language='si')
    print(f"Interpretation (si): {interpretation['recommendation']}")
    
    interpretation = service.interpret_score(score, language='ta')
    print(f"Interpretation (ta): {interpretation['recommendation']}")
    
    print("Verification successful!")
except Exception as e:
    print(f"Verification failed: {e}")
    import traceback
    traceback.print_exc()
