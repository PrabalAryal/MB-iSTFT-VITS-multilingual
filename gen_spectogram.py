import os
import torch
import numpy as np
import librosa
import torch.nn.functional as F
from utils import load_wav_to_torch
from mel_processing import spectrogram_torch

DATA_DIR = "nl_audio"
FILTER_LENGTH = 1024
HOP_LENGTH = 256
WIN_LENGTH = 1024
SAMPLING_RATE = 22050
MAX_WAV_VALUE = 32768.0
MIN_FRAMES = 32

freq_bins = FILTER_LENGTH // 2 + 1

def ensure_min_length(audio, min_frames=MIN_FRAMES):
    """Pad audio to ensure minimum number of spectrogram frames"""
    min_length = WIN_LENGTH + (min_frames - 1) * HOP_LENGTH
    
    # Handle empty or invalid audio
    if audio is None or audio.numel() == 0:
        return torch.zeros(min_length)
        
    # If audio is too short, pad it
    if audio.size(-1) < min_length:
        # Calculate needed padding
        pad_length = min_length - audio.size(-1)
        
        # For very short audio, repeat the content multiple times first
        if audio.size(-1) < WIN_LENGTH:
            repeats = (WIN_LENGTH + audio.size(-1) - 1) // audio.size(-1)
            audio = audio.repeat(repeats)
            
        # Then apply reflection padding
        audio = F.pad(audio, (0, pad_length), mode='reflect')
        
    return audio


def save_spec_tensor(spec: torch.Tensor, path: str):
    """Save spectrogram tensor ensuring proper format"""
    # Validate input
    if spec is None:
        raise ValueError("Cannot save None spectrogram")
    
    # ensure float32 and 2D (freq_bins, frames)
    spec = spec.float()
    if spec.dim() == 1:
        spec = spec.unsqueeze(1)
    if spec.dim() != 2:
        raise RuntimeError(f"Spec has unexpected dim {spec.dim()}")
    
    # Validate shape
    if spec.size(0) != freq_bins:
        raise ValueError(f"Expected {freq_bins} frequency bins, got {spec.size(0)}")
    
    # Ensure minimum frames through spectrogram padding
    if spec.size(1) < MIN_FRAMES:
        pad_frames = MIN_FRAMES - spec.size(1)
        # Reflect pad if enough frames, otherwise repeat
        if spec.size(1) > 1:
            spec = F.pad(spec, (0, pad_frames), mode='reflect')
        else:
            spec = spec.repeat(1, MIN_FRAMES)
    
    torch.save(spec, path)
    return tuple(spec.shape)

def fallback_librosa(wav_path, audio_tensor):
    y = audio_tensor.numpy().astype(np.float32)
    D = np.abs(librosa.stft(y, n_fft=FILTER_LENGTH, hop_length=HOP_LENGTH, win_length=WIN_LENGTH, center=False))
    return torch.from_numpy(D.astype(np.float32))

def orient_spec(spec: torch.Tensor):
    # Accepts 1D/2D/3D tensors and returns 2D (freq_bins, frames) or None on failure
    if spec is None:
        return None
    # squeeze batch if present
    if spec.dim() == 3 and spec.size(0) == 1:
        spec = spec.squeeze(0)
    # If still 3D -> unsupported
    if spec.dim() == 3:
        return None
    # If 1D -> bad
    if spec.dim() == 1:
        return None
    # dim == 2: decide orientation
    h, w = spec.shape
    # case: already (freq_bins, frames)
    if h == freq_bins:
        return spec
    # case: (1, freq_bins) -> transpose to (freq_bins,1)
    if h == 1 and w == freq_bins:
        return spec.t()
    # case: (frames, freq_bins) -> transpose
    if w == freq_bins and h != freq_bins:
        return spec.t()
    # case: (freq_bins, 1) already handled by h==freq_bins
    # other unexpected shapes -> fail
    return None

def process_all():
    written = 0
    errors = 0
    
    for root, _, files in os.walk(DATA_DIR):
        for f in files:
            if not f.lower().endswith(".wav"):
                continue
            wav = os.path.join(root, f)
            spec_path = wav.replace(".wav", ".spec.pt")
            
            try:
                # Load and process audio
                audio, sr = load_wav_to_torch(wav)
                if sr != SAMPLING_RATE:
                    print(f"SKIP SR MISMATCH {wav} {sr}")
                    errors += 1
                    continue

                # Ensure minimum length and normalize
                audio = ensure_min_length(audio)
                audio_len = audio.numel()
                
                # Debug info
                expected_frames = ((audio_len - WIN_LENGTH) // HOP_LENGTH) + 1
                print(f"\nProcessing {wav}")
                print(f"Audio samples: {audio_len}")
                print(f"Expected frames: {expected_frames}")
                
                # Generate spectrogram
                audio_norm = (audio / MAX_WAV_VALUE).unsqueeze(0)
                raw = spectrogram_torch(audio_norm, FILTER_LENGTH, SAMPLING_RATE, HOP_LENGTH, WIN_LENGTH, center=False)
                
                if raw is None or raw.numel() == 0:
                    raise RuntimeError("Failed to generate spectrogram")
                    
                print(f"Raw spec shape: {tuple(raw.shape)} dim={raw.dim()}")

                # Try primary method first, fall back if needed
                spec = orient_spec(raw)
                if spec is None:
                    print("Falling back to librosa STFT")
                    spec = fallback_librosa(wav, audio)
                
                if spec is None:
                    raise RuntimeError("Failed to generate spectrogram with both methods")
                    
                shape = save_spec_tensor(spec, spec_path)
                print(f"WROTE {spec_path} {shape}")
                written += 1
                
            except Exception as e:
                print(f"ERROR processing {wav}: {str(e)}")
                errors += 1
                continue
                
    print(f"\nDone. Wrote {written} specs. Errors: {errors}")
    
    
    
if __name__ == "__main__":
    process_all()