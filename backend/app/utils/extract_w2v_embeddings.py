def extract_w2v_embedding(audio_bytes: bytes):
    import io
    import librosa
    import torch

    from app.models.voice_stress_model import wav2vec2, TARGET_SR, DEVICE

    # Load audio
    audio_buf = io.BytesIO(audio_bytes)
    audio, _ = librosa.load(audio_buf, sr=TARGET_SR, mono=True)

    # Convert to tensor - ensure it's the right shape and type
    waveform = torch.tensor(audio, dtype=torch.float32).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        # Transformers wav2vec2 feature extraction
        outputs = wav2vec2(waveform)
        
        # Get last hidden state: (batch, time, features)
        z = outputs.last_hidden_state
        
        # Average pool over time dimension to get fixed-size embedding (batch, features)
        embedding = z.mean(dim=1)
        
        print(f"✓ Embedding shape: {embedding.shape}")  # Should match StudentNet input

    return embedding
