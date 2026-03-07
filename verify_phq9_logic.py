
import sys
import os
from datetime import datetime

def test_logic():
    # Simulate numeric keys from user/service
    answers = {1: 1, 2: 2, 3: 0, 4: 1, 5: 1, 6: 0, 7: 1, 8: 1, 9: 0}
    
    # Simulating the fix: Converting keys to strings
    phq9_answers_string_keys = {str(k): v for k, v in answers.items()}
    
    updates = {
        'phq9_answers': phq9_answers_string_keys,
        'phq9_score': int(sum(answers.values())),
        'phq9_completed_at': datetime.utcnow().isoformat()
    }
    
    print(f"Updates to Firestore: {updates}")
    
    # Verify all keys in phq9_answers are strings
    for k in updates['phq9_answers'].keys():
        if not isinstance(k, str):
            print(f"ERROR: Key {k} (type: {type(k)}) is not a string!")
            return False
            
    print("Verification Successful: All keys in phq9_answers are strings.")
    return True

if __name__ == "__main__":
    if test_logic():
        # Exit with a success code
        print("Test Passed")
    else:
        # Exit with a failure code
        sys.exit(1)
