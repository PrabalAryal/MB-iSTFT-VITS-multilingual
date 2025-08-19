import os
import librosa
import argparse
import soundfile as sf

# ...existing code...

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--in_path", default="./nl_audio/")
    parser.add_argument("--out_path", default=None,
                        help="If not set, files will be overwritten in --in_path")
    parser.add_argument("--extensions", default=".wav,.flac,.mp3,.m4a,.ogg",
                        help="Comma-separated list of audio extensions to process")
    args = parser.parse_args()

    in_path = args.in_path
    out_path = args.out_path or in_path
    valid_exts = tuple(ext.strip().lower() for ext in args.extensions.split(","))

    os.makedirs(out_path, exist_ok=True)

    for filename in os.listdir(in_path):
        if not filename.lower().endswith(valid_exts):
            continue
        in_file = os.path.join(in_path, filename)
        out_file = os.path.join(out_path, filename)

        print("Processing:", in_file, "->", out_file)
        try:
            y, sr = librosa.load(in_file, sr=22050, mono=True)
            # write to a temporary file first, then atomically replace the target
            tmp_file = out_file + ".tmp"
            sf.write(tmp_file, y, sr, format='WAV',subtype="PCM_16")
            # atomic replace (safer than writing directly over file)
            os.replace(tmp_file, out_file)
        except Exception as e:
            # remove leftover tmp file if any
            try:
                if os.path.exists(tmp_file):
                    os.remove(tmp_file)
            except Exception:
                pass
            print("Skipped", in_file, "error:", e)