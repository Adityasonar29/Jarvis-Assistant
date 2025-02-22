import tkinter as tk
from tkinter import messagebox
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import librosa
import os
import joblib
from sklearn.mixture import GaussianMixture

# ------------------ Voice Recording ------------------
def record_voice(filename, duration=5, sample_rate=16000):
    print("Recording... Speak now!")
    audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype=np.int16)
    sd.wait()
    wav.write(filename, sample_rate, audio_data)
    print(f"Voice sample saved as {filename}")
    messagebox.showinfo("Success", f"Voice sample saved as {filename}")

# ------------------ Feature Extraction ------------------
def extract_features(filename):
    audio, sample_rate = librosa.load(filename, sr=None)
    mfcc_features = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=13)
    return np.mean(mfcc_features.T, axis=0)  # Average over time

# ------------------ Train Model ------------------
def train_model():
    user_name = entry_username.get().strip()
    if not user_name:
        messagebox.showerror("Error", "Please enter a username")
        return
    
    voice_sample = f"{user_name}.wav"
    if not os.path.exists(voice_sample):
        messagebox.showerror("Error", "No voice sample found! Please record first.")
        return
    
    features = extract_features(voice_sample)
    features = np.array(features).reshape(1, -1)

    model = GaussianMixture(n_components=3, covariance_type='diag', n_init=10)
    model.fit(features)

    os.makedirs("models", exist_ok=True)
    model_filename = f"models/{user_name}_model.pkl"
    joblib.dump(model, model_filename)
    messagebox.showinfo("Success", f"Model trained and saved for {user_name}")

# ------------------ Authenticate User ------------------
def authenticate_user():
    user_name = entry_username.get().strip()
    if not user_name:
        messagebox.showerror("Error", "Please enter a username")
        return

    model_filename = f"models/{user_name}_model.pkl"
    if not os.path.exists(model_filename):
        messagebox.showerror("Error", "User model not found! Train the model first.")
        return

    record_voice("test_voice.wav")
    model = joblib.load(model_filename)
    input_features = extract_features("test_voice.wav")
    score = model.score([input_features])
    
    threshold = -50  # Adjust this value for better accuracy
    if score > threshold:
        messagebox.showinfo("Success", "Authentication Successful! Access Granted.")
    else:
        messagebox.showerror("Failed", "Authentication Failed! Access Denied.")

# ------------------ GUI Design ------------------
root = tk.Tk()
root.title("Voice Authentication System")
root.geometry("400x300")

tk.Label(root, text="Voice Authentication", font=("Arial", 16)).pack(pady=10)

tk.Label(root, text="Enter Username:").pack()
entry_username = tk.Entry(root)
entry_username.pack()

tk.Button(root, text="Record Voice", command=lambda: record_voice(entry_username.get() + ".wav")).pack(pady=5)
tk.Button(root, text="Train Model", command=train_model).pack(pady=5)
tk.Button(root, text="Authenticate", command=authenticate_user).pack(pady=5)

root.mainloop()
