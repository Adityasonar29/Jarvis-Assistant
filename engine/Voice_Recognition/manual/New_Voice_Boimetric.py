import os
import librosa
import torch
import torchaudio
import numpy as np
import sounddevice as sd
import wave
from scipy.io import wavfile
from pydub import AudioSegment
from pydub.silence import split_on_silence
import noisereduce as nr
import speechbrain
from speechbrain.inference import EncoderClassifier

from sklearn.metrics.pairwise import cosine_similarity

# Load the pre-trained ECAPA-TDNN model
model = EncoderClassifier.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb")

# Global variables
SAMPLE_RATE = 32000  # 16kHz is standard for voice processing
DURATION = 5  # Recording time for each sample
NUM_SAMPLES = 5  # Number of samples to enroll a user


### ---- Utility Functions ---- ###

def record_audio(filename, duration=DURATION, sample_rate=SAMPLE_RATE):
    """Records an audio sample and saves it to a file."""
    print(f"🎤 Recording {filename} for {duration} seconds... at {sample_rate}Hz")
    audio_data = sd.rec(int(sample_rate * duration), samplerate=sample_rate, channels=1, dtype=np.float32)
    sd.wait()  # Wait for the recording to finish
    wavfile.write(filename, sample_rate, (audio_data * 32767).astype(np.int16))  # Save as 16-bit PCM
    print(f"✅ Saved: {filename}")


def preprocess_audio(file_path):
    """Removes noise and silent parts from the audio file."""
    
    #     # Load audio at our chosen sample rate
    # y, sr = librosa.load(file_path, sr=SAMPLE_RATE, mono=True)
    
    # Load audio
    audio, sr = torchaudio.load(file_path)
    print("Sample Rate: ",sr)
    
     # Fix sample rate issues
    if sr is None or sr > 65535 or sr < 1:
        print("Sample Rate is greater than 65535 ",sr)
        sr = SAMPLE_RATE  # Default to 16kHz
    
    # Noise reduction
    audio_np = audio.numpy().squeeze() # Remove extra dimensions
    
    audio_denoised = nr.reduce_noise(y=audio_np, sr=sr)
    
    # # Apply noise reduction (using the first 0.5 seconds as a noise sample)
    # noise_sample = y[:int(0.5 * sr)]
    # audio_denoised = nr.reduce_noise(y=noise_sample, sr=sr, prop_decrease=0.9, stationary=True)
    
    print("Audio shape:", audio_denoised.shape)
    print(f"Original audio shape: {audio_denoised.shape}")
    
    if np.isnan(audio_denoised).any() or np.isinf(audio_denoised).any():
        raise ValueError("Audio contains NaN or infinite values")

    # Save the denoised audio temporarily
    temp_file = "temp.wav"
    wavfile.write(temp_file, sr, (audio_denoised * 32767).astype(np.int16))

    # Remove silence
    sound = AudioSegment.from_wav(temp_file)
    chunks = split_on_silence(sound, min_silence_len=300, silence_thresh=-40)
    # processed_sound = AudioSegment.empty()
    # for chunk in chunks:
    #     processed_sound += chunk
    if len(chunks) == 0:
        print("Warning: No speech detected! Using original audio.")
        processed_sound = sound
        
    else:
        processed_sound = AudioSegment.empty()
        for chunk in chunks:
            processed_sound += chunk
    
    print(processed_sound)
    processed_sound.export(file_path, format="wav")
    # Save the processed audio
    os.remove(temp_file)

    print(f"Preprocessed and updated: {file_path}")
    return file_path

def extract_features(audio_path):
    """Extracts the speaker embedding using ECAPA-TDNN model."""
    preprocess_audio(audio_path)  # Clean the audio
        #Unlock the above section when we need a high quality audio like we need accurate very very accurate decision then unlock the abuse section
    signal, fs = torchaudio.load(audio_path)  # Load processed audio
    if signal.shape[1] == 0:  # Check if audio is empty after processing
        raise ValueError(f"Error: {audio_path} contains no valid speech!")
    
    signal = signal.float()# Convert to correct format 
    embedding = model.encode_batch(signal)  # Extract features # Extract speaker embedding
    
    return embedding.squeeze().detach().numpy()


### ---- Enrollment & Authentication ---- ###

def enroll_user(user_id):
    """Enrolls a user by recording multiple samples and averaging their embeddings."""
    os.makedirs("voice_data", exist_ok=True)
    enrolled_path = f"voice_data/{user_id}_embedding.npy"
    
    if os.path.exists(enrolled_path):
        print(f"⚠️ User {user_id} is already enrolled. Overwriting data...")

    embeddings = []
    for i in range(NUM_SAMPLES):
        filename = f"voice_data/{user_id}_sample_{i+1}.wav"
        
        record_audio(filename)
        embedding = extract_features(filename)
        embeddings.append(embedding)
        
    if len(embeddings) == 0:
        print(f"❌ Enrollment failed for {user_id} (No valid recordings)")
        return

    # Compute the average embedding for the user
    avg_embedding = np.mean(embeddings, axis=0)
    np.save(f"voice_data/{user_id}_embedding.npy", avg_embedding)
    print(f"✅ User {user_id} enrolled successfully!")


def authenticate_user(user_id):
    """Authenticates a user by comparing a test sample with the enrolled voiceprint."""
    filename = f"voice_data/{user_id}_test.wav"
    record_audio(filename)

    # Extract features from test audio
    try:
        test_embedding = extract_features(filename)
    except ValueError as e:
        print(f"❌ Authentication Failed: {e}")
        return False


    # Load enrolled embedding
    enrolled_embedding_path = f"voice_data/{user_id}_embedding.npy"
    if not os.path.exists(enrolled_embedding_path):
        print(f"⚠️ No enrollment found for user: {user_id}")
        return False

    enrolled_embedding = np.load(enrolled_embedding_path)

    # Compute cosine similarity
    similarity = cosine_similarity([enrolled_embedding], [test_embedding])[0][0]

    # Authentication decision
    # threshold = 0.85  # Adjust for stricter or more lenient authentication

    # **Dynamic threshold adjustment** based on enrolled voice
    threshold = max(0.75, min(0.90, similarity * 0.9))  # Adjust between 0.75 and 0.90
    
    if similarity >= threshold:
        print(f"✅ Access Granted! (Similarity: {similarity:.2f})")
        return True
    else:
        print(f"❌ Access Denied! (Similarity: {similarity:.2f})")
        return False

if __name__=="__main__":
        
    user = "Aditya"

    # Enroll User
    # enroll_user(user)

    # Authenticate User
    authenticate_user(user)
