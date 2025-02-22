import sounddevice as sd
import numpy as np
import librosa
import json
import pickle
import scipy.io.wavfile as wav
from sklearn.metrics.pairwise import cosine_similarity

# Constants
SAMPLE_RATE = 22050  # Sample rate for recording
DURATION = 5  # Record duration (seconds)
FILENAME = "auth_voice.wav"  # Temporary file for authentication
FEATURES_FILE = "voice_templates.json"
TEMPLATE_FILE = "voice_template.pkl"  # Stored voice template
THRESHOLD = 0.85  # Similarity threshold for authentication

def record_audio(filename, duration=5, sample_rate=22050):
    print("🎤 Recording... Speak now!")
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype=np.float32)
    sd.wait()  # Wait until recording is finished
    wav.write(filename, sample_rate, (audio * 32767).astype(np.int16))  # Save as WAV file
    print("✅ Recording complete! Audio saved.")

def extract_mfcc(filename):
    print("🔍 Extracting MFCC features...")
    audio, sr = librosa.load(filename, sr=SAMPLE_RATE)
    mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
    return np.mean(mfcc, axis=1)  # Get the average MFCC features

def load_template(template_file=TEMPLATE_FILE):
    with open(template_file, "rb") as f:
        return pickle.load(f)  # Load stored voice template

def compare_features(new_features, stored_features):
    similarity = cosine_similarity([new_features], [stored_features])[0][0]  # Compute cosine similarity
    print(f"🔹 Similarity Score: {similarity:.4f}")

    if similarity >= THRESHOLD:
        print("✅ Access Granted! Voice Matched.")
    else:
        print("❌ Access Denied! Voice Not Recognized.")

# **Run Authentication Process**
# record_audio(FILENAME, DURATION, SAMPLE_RATE)  # Step 1: Record new voice
def Authenticate():
    new_mfcc_features = extract_mfcc(FILENAME)  # Step 2: Extract features
    stored_mfcc_features = load_template()  # Step 3: Load stored template
    compare_features(new_mfcc_features, stored_mfcc_features)  # Step 4: Compare features
