# app/models/voice_stress_model.py
import torch
from transformers import AutoConfig, AutoModelForAudioClassification, Wav2Vec2Model
import shutil
from pathlib import Path

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
TARGET_SR = 16000
REPO = "forwarder1121/voice-based-stress-recognition"

# --------------------------------------------------
# Clear cached transformers modules to force fresh download
# --------------------------------------------------
cache_dir = Path.home() / ".cache" / "huggingface" / "modules" / "transformers_modules"
repo_cache = cache_dir / "forwarder1121"
if repo_cache.exists():
    print(f"Clearing cached module: {repo_cache}")
    shutil.rmtree(repo_cache, ignore_errors=True)

# --------------------------------------------------
# Monkey patch AutoConfig globally to always use trust_remote_code
# --------------------------------------------------
_original_autoconfig_from_pretrained = AutoConfig.from_pretrained

def _patched_autoconfig_from_pretrained(pretrained_model_name_or_path, **kwargs):
    """Wrapper that always adds trust_remote_code=True"""
    kwargs['trust_remote_code'] = True
    return _original_autoconfig_from_pretrained(pretrained_model_name_or_path, **kwargs)

# Apply the patch
AutoConfig.from_pretrained = _patched_autoconfig_from_pretrained

print("✓ Monkey patch applied to AutoConfig.from_pretrained")

# --------------------------------------------------
# Load StudentNet with custom architecture
# --------------------------------------------------
try:
    print(f"\nLoading stress model from {REPO}...")
    
    stress_model = AutoModelForAudioClassification.from_pretrained(
        REPO,
        trust_remote_code=True,
    ).to(DEVICE)
    
    stress_model.eval()
    print("✓ Stress model (StudentNet) loaded successfully")
    print(f"  Model type: {type(stress_model).__name__}")
    print(f"  Device: {DEVICE}")
    
except Exception as e:
    print(f"❌ Error loading stress model: {e}")
    import traceback
    traceback.print_exc()
    raise

# --------------------------------------------------
# Load Transformers wav2vec2 (feature extractor)
# --------------------------------------------------
try:
    print(f"\nLoading Wav2Vec2 feature extractor (Transformers)...")
    
    # Using facebook/wav2vec2-large as a compatible alternative to wav2vec_large.pt
    wav2vec2 = Wav2Vec2Model.from_pretrained("facebook/wav2vec2-large").to(DEVICE)
    wav2vec2.eval()
    
    print("✓ Wav2Vec2 feature extractor loaded successfully")
    print(f"  Device: {DEVICE}")
    
except Exception as e:
    print(f"❌ Error loading wav2vec model: {e}")
    import traceback
    traceback.print_exc()
    raise

print(f"\n{'='*70}")
print(f"✅ All models loaded successfully!")
print(f"{'='*70}\n")
