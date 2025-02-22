import os
import json
import scipy
import librosa
import numpy as np
import parselmouth
import noisereduce as nr
import sounddevice as sd
from fastdtw import fastdtw
import scipy.io.wavfile as wav
from scipy.ndimage import zoom
from scipy.spatial.distance import euclidean

# Constants
SAMPLE_RATE = 44100  
DURATION = 5  
TEMPLATES_FILE = "Data\\Voice_Recognition_Samples\\voice_templates.json"
THRESHOLD = 90000
DIRECTORY = "Data\\Voice_Recognition_Samples\\Samples\\"




def match_mfcc_lengths(mfcc1, mfcc2):
    """Resize MFCC arrays to have the same second dimension."""
    if mfcc1.shape[1] > mfcc2.shape[1]:
        mfcc2 = zoom(mfcc2, (1, mfcc1.shape[1] / mfcc2.shape[1]))
    elif mfcc1.shape[1] < mfcc2.shape[1]:
        mfcc1 = zoom(mfcc1, (1, mfcc2.shape[1] / mfcc1.shape[1]))
    return mfcc1, mfcc2


def record_audio(filename_P):
    # Create full path by joining DIRECTORY with filename
    filename = os.path.join(DIRECTORY, filename_P)    
    
    print("🎤 Recording... Speak now!")
    audio_data = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='int16')
    sd.wait()

    # Convert to NumPy array
    audio_data = audio_data.flatten().astype(np.float32)
    
        # Apply noise reduction
    reduced_noise = nr.reduce_noise(
        y=audio_data,
        sr=SAMPLE_RATE,
        prop_decrease=0.75,  # Adjust this value between 0-1 to control noise reduction intensity
        n_std_thresh_stationary=1.5,
        stationary=True
    )
    
    # Apply a high-pass filter (Removes low-frequency noise)
    cutoff_freq = 300  # Hz (Removes sounds below 300Hz)
    b, a = scipy.signal.butter(3, cutoff_freq / (SAMPLE_RATE / 2), btype='high')
    filtered_audio = scipy.signal.lfilter(b, a, audio_data)

    # Apply pre-emphasis filter (boosts high-frequency speech features)
    pre_emphasis = 0.97
    filtered_audio = np.append(filtered_audio[0], filtered_audio[1:] - pre_emphasis * filtered_audio[:-1])
    
    # Ensure directory exists before saving
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    # Save the filtered audio
    wav.write(filename, SAMPLE_RATE, filtered_audio.astype(np.int16))

    print("✅ Recording complete!")


def extract_mfcc(filename_p, num_mfcc=13, fixed_length=50):
    
    # Create full path by joining DIRECTORY with filename
    filename = os.path.join(DIRECTORY, filename_p)
    
    # Load audio
    rate, data = wav.read(filename)

    # Reduce noise
    reduced_noise = nr.reduce_noise(y=data.astype(float), sr=rate, prop_decrease=0.9)

    # Apply Voice Activity Detection (VAD) to remove silence/noisy regions
    voiced_intervals = librosa.effects.split(reduced_noise, top_db=30)
    clean_audio = np.concatenate([reduced_noise[start:end] for start, end in voiced_intervals])

    # Save cleaned audio (optional)
    wav.write ( filename, rate, clean_audio.astype(np.int16))

    # Save cleaned audio (optional)
    # wav.write("cleaned_" + filename, rate, reduced_noise.astype(np.int16))

    # Convert to MFCC
    cleaned_filename = os.path.join(os.getcwd(), filename)
    snd = parselmouth.Sound(cleaned_filename)   
    mfcc = snd.to_mfcc(number_of_coefficients=13, window_length=0.025, time_step=0.01)

    if mfcc is None or mfcc.to_matrix().values.shape[1] == 0:
        print("⚠️ Error: Extracted MFCC is empty!")
        return None
    
    """Extract MFCC features and ensure fixed dimensions."""
    y, sr = librosa.load(filename, sr=44100)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=num_mfcc)

    # Ensure all MFCCs have the same length (pad or truncate)
    if mfcc.shape[1] < fixed_length:
        mfcc = np.pad(mfcc, ((0, 0), (0, fixed_length - mfcc.shape[1])), mode='constant')
    else:
        mfcc = mfcc[:, :fixed_length]

    return mfcc.T  # Just transpose it, no need for `.to_matrix()`




def save_voice_template(mfcc_features, user_id):
    """Safely saves voice template to JSON file."""
    try:
        with open(TEMPLATES_FILE, "r") as f:
            try:
                voice_data = json.load(f)
            except json.JSONDecodeError:
                print("⚠️ JSON file is empty or corrupted. Resetting.")
                voice_data = {}  # Reset if JSON is corrupted
    except FileNotFoundError:
        voice_data = {}  # Create new file if missing

    if user_id not in voice_data:
        voice_data[user_id] = []

    voice_data[user_id].append(mfcc_features.tolist())

    # 🔥 Safely write to JSON file
    temp_file = f"{TEMPLATES_FILE}.tmp"
    with open(temp_file, "w") as f:
        json.dump(voice_data, f, indent=4)
    
    os.replace(temp_file, TEMPLATES_FILE)  # Replace old file atomically
    print(f"✅ Voice template saved for user '{user_id}'!")



def load_voice_templates(user_id):
    """Loads all saved voice templates."""
    try:
        with open(TEMPLATES_FILE, "r") as f:
            voice_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print("⚠️ No saved voice templates found! Returning empty list.")
        return []  # Always return an empty list

    # Ensure the retrieved data is a valid list of MFCCs
    stored_mfccs = voice_data.get(user_id, [])

    if not isinstance(stored_mfccs, list):
        print("⚠️ Warning: Loaded data is not a list! Resetting...")
        return []

    # Convert all stored MFCCs back to NumPy arrays
    return [np.array(mfcc) for mfcc in stored_mfccs if isinstance(mfcc, list)]



def authenticate_voice(new_mfcc, user_id):
    """Compare new voice sample with stored templates using DTW and apply a 90% threshold."""
    stored_mfcc_list = load_voice_templates(user_id)
    distances = []

    if not stored_mfcc_list:
        print("⚠️ No saved voice templates. Please enroll first!")
        return False

    # Ensure new_mfcc has correct shape
    new_mfcc = new_mfcc[:, :13] if new_mfcc.shape[1] > 13 else new_mfcc

    for stored_mfcc in stored_mfcc_list:
        if stored_mfcc is None or stored_mfcc.size == 0:
            continue

        stored_mfcc = stored_mfcc[:, :13] if stored_mfcc.shape[1] > 13 else stored_mfcc

        # Ensure MFCC feature sizes match before DTW
        min_length = min(new_mfcc.shape[0], stored_mfcc.shape[0])
        new_mfcc = new_mfcc[:min_length, :]
        stored_mfcc = stored_mfcc[:min_length, :]

        # Compute DTW distance
        distance, _ = fastdtw(new_mfcc, stored_mfcc, dist=euclidean)
        distances.append(distance)
        print(f"🔍 DTW Distance: {distance:.2f}")

    # 🔥 Normalize distances to a similarity score
    min_distance = min(distances)
    max_distance = max(distances)

    if max_distance == min_distance:
        similarity = 100  # Perfect match
    else:
        similarity = 100 - ((min_distance / max_distance) * 100)  # Convert to percentage

    print(f"⚙️ Voice Similarity: {similarity:.2f}%")

    # ✅ 90% Threshold for Access
    if similarity >= 90:
        print("✅ Authentication Successful! Access Granted.")
        return True

    print("❌ Authentication Failed! Access Denied.")
    return False





if __name__ == "__main__":
    print("🎤 Advanced Multi-Sample Voice Authentication")

    choice = input("Do you want to (1) Enroll a user or (2) Authenticate? ")

    if choice == "1":
        user_id = input("Enter a unique user ID: ")
        for i in range(5):  # 🔥 Require 5 samples instead of 3
            filename = f"{user_id}_sample_{i}.wav"
            record_audio(filename)
            mfcc_features = extract_mfcc(filename)
            if mfcc_features is not None:
                save_voice_template(mfcc_features, user_id)


    elif choice == "2":
        user_id = input("Enter your user ID: ")
        filename = "temp_voice.wav"
        record_audio(filename)
        mfcc_features = extract_mfcc(filename)
        authenticate_voice(mfcc_features, user_id)
