import pyttsx3
import speech_recognition as sr

def speak(text):
    text = str(text)
    engine = pyttsx3.init("sapi5")
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)
    engine.setProperty('rate', 174)
    #eel.DisplayMassage(text)
    engine.say(text)
    #eel.receiverText(text)#=> this is for canvas(chat box)
    engine.runAndWait()

def takecommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("listening...")
        #eel.DisplayMassage('listening..')
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source)
        #todo:add a listenning time out 
        #todo also add the show hood command if  listenning time out
        audio = r.listen(source, 10, 6)
    try:
        print("recognizing....")
        #eel.DisplayMassage('recognizing..')
        query = r.recognize_google(audio, language="en-in")
        print(f"User said:{query}")
        #eel.DisplayMassage(query)
        time.sleep(2)
        
    except Exception as e:
        return ""
    return query.lower()    

from engine.helper import check_device_lock_status_batch, keyEvents
import sounddevice as sd
from scipy.io.wavfile import write
import time
import os
import numpy as np
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
import subprocess

def start_adb_connection():
    """
    Ensures the ADB connection is established with the phone.
    """
    try:
        # Check ADB devices
        devices = subprocess.check_output(["adb", "devices"]).decode()
        if "device" not in devices:
            print("No device found. Ensure USB debugging is enabled.")
            return False
        print("ADB connection established.")
        return True
    except Exception as e:
        print(f"ADB connection failed: {e}")
        return False

# Call the function for testing
def check_call_state():
    """
    Check the call state of the phone using ADB.
    Returns 'IDLE'    -->The phone is not in a call, and there is no       
                        incoming or outgoing call activity, 
            'RINGING' --> The phone is receiving an incoming call, and the ringtone 
                        is playing. The user has not yet answered or rejected the call,
        or  'OFFHOOK' -->The phone is in an active call. This includes both
                        outgoing calls (where the user has dialed a number) and ongoing calls
                        (where the user is speaking to someone). 
    """
    try:
        # Use the optimized ADB command with findstr
        output = subprocess.check_output(
            ["adb", "shell", "dumpsys telephony.registry | grep mCallState"],
            shell=True  # Allows using the pipe operator
        ).decode()
        # print(output)  # Debugging: Check the filtered output

        # Check each line for call state
        if "mCallState=1" in output:
            print("The phone is ringing")
            return "RINGING"
        elif "mCallState=2" in output:
            print("The phone is on call")
            return "OFFHOOK"
        elif "mCallState=0" in output:
            print("The phone does not have any call")
            return "IDLE"
    except Exception as e:
        print(f"Error checking call state: {e}")
    return "IDLE"



def record_call_via_adb():
    """
    Records audio during a call using ADB.
    Automatically stops when the call ends.
    """
    timestamp = int(time.time())
    phone_output_file = f"/sdcard/call_record_{timestamp}.mp4"
    #change the file location to jarvis after testing
    pc_output_file = f"Call_Surounding_recording//call_record_{timestamp}.mp4"

    try:
        print("Waiting for a call to start...")
        while check_call_state() != "OFFHOOK":
            time.sleep(1)

        print("Call detected. Starting recording...")
        process = subprocess.Popen(
            ["adb", "shell", "screenrecord", "--output-format=h264", phone_output_file],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        while check_call_state() == "OFFHOOK":
            time.sleep(1)

        print("Call ended. Stopping recording...")
        process.terminate()
        time.sleep(1)  # Allow screenrecord to terminate gracefully

        print("Pulling the recording to the local machine...")
        subprocess.run(["adb", "pull", phone_output_file, pc_output_file])

        print("Cleaning up the phone storage...")
        subprocess.run(["adb", "shell", "rm", phone_output_file])

        print(f"Recording saved locally as {pc_output_file} and deleted from the phone.")
    except Exception as e:
        print(f"Error during recording: {e}")

def record_surrounding_audio(duration=60):
    """
    Records surrounding audio using the phone's microphone for a given duration.
    """
    timestamp = int(time.time())
    phone_output_file = f"/sdcard/audio_record_{timestamp}.mp3"
    pc_output_file = f"I:/MyCodingHelper/Projects/python_projects/Jarvis/Call_Surounding_recording/audio_record_{timestamp}.mp4"

    try:
        print(f"Recording surrounding audio for {duration} seconds...")
        subprocess.run([
            "adb", "shell", "screenrecord", "--output-format=h264", phone_output_file
        ], timeout=duration)

        print("Pulling the recording to the local machine...")
        subprocess.run(["adb", "pull", phone_output_file, pc_output_file])

        print("Cleaning up the phone storage...")
        subprocess.run(["adb", "shell", "rm", phone_output_file])

        print(f"Recording saved locally as {pc_output_file}.")
    except subprocess.TimeoutExpired:
        print("Recording completed.")
    except Exception as e:
        print(f"Error during recording: {e}")
    
def record_surrounding_audio1(duration=60):
    """
    Records surrounding audio using the phone's microphone for a given duration.
    Saves the audio in MP3 format.
    """
    import os
    timestamp = int(time.time())
    phone_output_file = f"/sdcard/audio_record_{timestamp}.mp4"
    pc_output_file = f"Call_Surounding_recording//audio_record_{timestamp}.mp4"
    mp3_output_file = pc_output_file.replace(".mp4", ".mp3")

    try:
        print(f"Recording surrounding audio for {duration} seconds...")
        subprocess.run([
            "adb", "shell", "screenrecord", "--output-format=h264", phone_output_file
        ], timeout=duration)

        print("Pulling the recording to the local machine...")
        subprocess.run(["adb", "pull", phone_output_file, pc_output_file])

        print("Cleaning up the phone storage...")
        subprocess.run(["adb", "shell", "rm", phone_output_file])

        print("Converting MP4 to MP3...")
        subprocess.run(["ffmpeg", "-i", pc_output_file, mp3_output_file])
        print(f"Audio recording saved locally as {mp3_output_file}.")
        
        # Optional: Remove the MP4 file after conversion
        os.remove(pc_output_file)

    except subprocess.TimeoutExpired:
        print("Recording completed.")
    except Exception as e:
        print(f"Error during recording: {e}")


def main():
    # Step 1: Start ADB connection
    if not start_adb_connection():
        return

    # Step 2: Choose action
    print("Select an option:")
    print("1. Record during call")
    print("2. Record surrounding audio")
    choice = input("Enter your choice (1/2): ")

    if choice == "1":
        record_call_via_adb()
    elif choice == "2":
        record_duration = int(input("Enter recording duration in seconds: "))
        record_surrounding_audio(record_duration)
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    # start_adb_connection()
    main()
    # check_call_state()
    # record_call_via_adb()

##image
#front cam-->
#adb shell am start -a android.media.action.IMAGE_CAPTURE --ei android.intent.extras.CAMERA_FACING 1
#back cam-->
#adb shell am start -a android.media.action.IMAGE_CAPTURE --ei android.intent.extras.CAMERA_FACING 0
#chang cam for -->
#adb shell am start -a android.media.action.STILL_IMAGE_CAPTURE --ei android.intent.extras.CAMERA_FACING 1
##video
#adb shell am start -a android.media.action.VIDEO_CAPTURE --ei android.intent.extras.CAMERA_FACING 1