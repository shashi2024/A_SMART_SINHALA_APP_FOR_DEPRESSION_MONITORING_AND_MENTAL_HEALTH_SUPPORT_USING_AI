import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'app'))

from gtts import gTTS
import io

def test_gtts():
    print("Testing gTTS generation...")
    try:
        text = "හෙලෝ මිත්‍රයා! මම සහනා, ඔබේ මානසික සෞඛ්‍ය සහාය සහකාරිය."
        language = 'si'
        
        tts = gTTS(text=text, lang=language, slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        size = fp.tell()
        
        if size > 0:
            print(f"SUCCESS: Generated {size} bytes of Sinhala audio using gTTS.")
        else:
            print("FAILURE: Generated empty audio.")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_gtts()
