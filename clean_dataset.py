import os
import torch
import torchaudio # Import torchaudio for a more robust check

# You may need to copy these imports from your original script
from mel_processing import spectrogram_torch
from utils import load_wav_to_torch, load_filepaths_and_text
from text import text_to_sequence, cleaned_text_to_sequence
import commons

class HParams:
    def __init__(self, **kwargs):
        # Using a fixed HParams object to simulate your config
        self.text_cleaners = ['dutch_cleaners']
        self.max_wav_value = 32768.0
        self.sampling_rate = 22050
        self.filter_length = 1024
        self.hop_length = 256
        self.win_length = 1024
        self.cleaned_text = True
        self.add_blank = True
        self.min_text_len = 1
        self.max_text_len = 190

class TextAudioLoader(torch.utils.data.Dataset):
    def __init__(self, audiopaths_and_text, hparams):
        self.audiopaths_and_text = load_filepaths_and_text(audiopaths_and_text)
        self.hparams = hparams
        # No shuffling or filtering on init to capture all files
    
    def check_file(self, audiopath, text):
        try:
            # Check if file exists
            if not os.path.exists(audiopath):
                return False, f"File not found: {audiopath}"
            
            # Check text length
            if not (self.hparams.min_text_len <= len(text) and len(text) <= self.hparams.max_text_len):
                return False, f"Text length out of range for {audiopath}: {len(text)}"

            # Get audio information without loading the entire file
            audio_info = torchaudio.info(audiopath)
            num_frames = audio_info.num_frames
            
            if num_frames < self.hparams.win_length:
                return False, f"Audio file is too short ({num_frames} samples) for win_length ({self.hparams.win_length}) at {audiopath}"

            # Now, attempt to load and process the audio
            audio, sampling_rate = load_wav_to_torch(audiopath)
            if sampling_rate != self.hparams.sampling_rate:
                return False, f"SR mismatch for {audiopath}: {sampling_rate} != {self.hparams.sampling_rate}"
            
            audio_norm = audio / self.hparams.max_wav_value
            audio_norm = audio_norm.unsqueeze(0)
            
            spec = spectrogram_torch(audio_norm, self.hparams.filter_length, self.hparams.sampling_rate, self.hparams.hop_length, self.hparams.win_length, center=False)
            spec = torch.squeeze(spec, 0)
            
            if spec.dim() < 2 or spec.size(1) < 1:
                return False, f"Spectrogram generation failed for {audiopath}. Spectrogram size: {spec.size()}"
            
            # All checks passed
            return True, "Success"
            
        except Exception as e:
            return False, f"Unexpected error processing {audiopath}: {e}"

def main():
    hps = HParams()
    filelist = 'filelists/dutch_train.txt.cleaned'
    
    loader = TextAudioLoader(filelist, hps)
    
    good_files = []
    bad_files = []
    
    print("--- Starting Data Validation ---")
    for audiopath, text in loader.audiopaths_and_text:
        is_good, reason = loader.check_file(audiopath, text)
        if is_good:
            good_files.append([audiopath, text])
        else:
            bad_files.append([audiopath, text])
            print(f"Skipping: {reason}")
            
    print(f"\n--- Data Validation Results ---")
    print(f"Total files: {len(loader.audiopaths_and_text)}")
    print(f"Good files: {len(good_files)}")
    print(f"Bad files: {len(bad_files)}")

    if good_files:
        with open(filelist, 'w', encoding='utf-8') as f:
            for item in good_files:
                f.write(f"{item[0]}|{item[1]}\n")
        print(f"Cleaned filelist saved to {filelist}. Ready for training.")
    else:
        print("WARNING: No good files were found. The filelist was not overwritten.")
        
    if bad_files:
        print("\n--- Problematic Files (and reason) ---")
        for bad_file, _ in bad_files:
            print(f"- {bad_file}")

if __name__ == "__main__":
    main()