import os
import re
from datasets import load_dataset, DatasetDict
import numpy as np
import scipy.io.wavfile

# --- Configuration ---
DATASET_NAME = "PrabalAryal/saskia_may23_39768"
OUTPUT_DIR = "dataset"
AUDIO_FOLDER = "nl_audio"
SPLITS = ["train", "test", "validation"]

# --- Main Script ---
def generate_dutch_dataset_files():
    """
    Generates .txt files and organizes audio files for a TTS dataset
    from a Hugging Face dataset.
    """
    
    # 1. Create necessary directories
    audio_path = os.path.join(OUTPUT_DIR, AUDIO_FOLDER)
    os.makedirs(audio_path, exist_ok=True)
    
    print(f"Creating output directories at '{OUTPUT_DIR}'...")
    print(f"Audio files will be saved in '{audio_path}'...")

    try:
        # 2. Load the dataset from Hugging Face
        print(f"\nLoading dataset '{DATASET_NAME}' from Hugging Face...")
        dataset: DatasetDict = load_dataset(DATASET_NAME)
        print("Dataset loaded successfully.")
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return

    # 3. Process each split (train, test, validation)
    for split_name in SPLITS:
        if split_name not in dataset:
            print(f"Skipping split '{split_name}' as it does not exist in the dataset.")
            continue
            
        print(f"\nProcessing '{split_name}' split...")
        
        split_data = dataset[split_name]
        output_txt_file = os.path.join(OUTPUT_DIR, f"dutch_{split_name}.txt")
        
        with open(output_txt_file, 'w', encoding='utf-8') as f:
            for i, item in enumerate(split_data):
                # Get the transcription (text) from the dataset item
                transcription = item['sentence']
                
                # Get the audio data
                audio_array = item['audio']['array']
                sampling_rate = item['audio']['sampling_rate']
                
                # Normalize audio to 16-bit integer format for .wav file
                # This is a common practice for TTS models
                max_amplitude = np.iinfo(np.int16).max
                audio_int16 = (audio_array * max_amplitude).astype(np.int16)

                # Generate a sequential filename for the audio file
                # Using a 5-digit format (e.g., 00001.wav) to handle large datasets
                audio_filename = f"{i+1:05d}.wav"
                
                # Define the full path to save the audio file
                audio_filepath = os.path.join(audio_path, audio_filename)
                
                # Write the audio array to a .wav file
                scipy.io.wavfile.write(audio_filepath, sampling_rate, audio_int16)
                
                # Create the line in the required format: relative_path|transcription
                relative_audio_path = os.path.join(AUDIO_FOLDER, audio_filename)
                line = f"{relative_audio_path}|{transcription}"
                
                # Write the line to the output text file
                f.write(line + '\n')
                
        print(f"Successfully generated {output_txt_file}")

    print("\nScript finished. Dataset files are ready for use.")

if __name__ == "__main__":
    generate_dutch_dataset_files()