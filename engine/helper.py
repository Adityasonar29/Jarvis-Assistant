import os
import subprocess
import regex as re
import time
from datetime import datetime, timedelta


def get_next_day_date(day_name):
    days_of_week = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    today = datetime.today()
    
    if day_name not in days_of_week:
        return None  # Invalid day name

    target_day = days_of_week.index(day_name)
    current_day = today.weekday()

    days_ahead = (target_day - current_day) % 7
    if days_ahead == 0:  # If today is the same day, return next week's same day
        days_ahead = 7

    return today + timedelta(days=days_ahead)


def get_day_time(time_str: str) -> str:
    """Convert time words to actual time."""
    time_mapping = {
        'morning': '09:00 AM',
        'afternoon': '02:00 PM',
        'evening': '06:00 PM',
        'night': '08:00 PM'
    }
    return time_mapping.get(time_str.lower())


def extract_yt_term(command):
    # Define a regular expression pattern to capture the song name
    pattern = r'play\s+(.*?)\s+on\s+youtube'
    # Use re.search to find the match in the command
    match = re.search(pattern, command, re.IGNORECASE)
    # If a match is found, return the extracted song name; otherwise, return None
    return match.group(1) if match else None


def remove_words(input_string, words_to_remove):
    # Split the input string into words
    words = input_string.split()

    # Remove unwanted words
    filtered_words = [word for word in words if word.lower() not in words_to_remove]

    # Join the remaining words back into a string
    result_string = ' '.join(filtered_words)

    return result_string



# key events like receive call, stop call, go back
def keyEvent(key_code):
    command =  f'adb shell input keyevent {key_code}'
    os.system(command)
    time.sleep(1)
    
def keyEvents(key_code):
    command =  f'adb shell input keyevent {key_code}'
    os.system(command)
    time.sleep(1)

# Tap event used to tap anywhere on screen
def tapEvents(x, y):
    command =  f'adb shell input tap {x} {y}'
    os.system(command)
    time.sleep(1)

# Input Event is used to insert text in mobile
def adbInput(massage):
    command =  f'adb shell input text "{massage}"'
    os.system(command)
    time.sleep(1)

# to go complete back
def goback(key_code):
    for i in range(6):
        keyEvent(key_code)

def swipeEvent():
    command =  f'adb shell input swipe 500 2000 500 1000'
    os.system(command)
    time.sleep(1)

def check_device_lock_status_batch():
    try:
        # Run the batch file and capture its output
        result = subprocess.run(
            ["cheak_device_loU.bat"],
            capture_output=True,
            text=True,
            shell=True
        )
        
        # Get the output from the batch file
        status = result.stdout.strip()
        
        if status == "LOCKED":
            print("Device is LOCKED.")
            openPhone()
            print("Device is now been unlock")
        elif status == "UNLOCKED":
            print("Device is UNLOCKED.")
        else:
            print("Unable to determine lock status.")
    except Exception as e:
        print(f"An error occurred: {e}")

def openPhone():
    command =  f'adb shell input keyevent KEYCODE_WAKEUP'
    os.system(command)
    time.sleep(1)
    swipeEvent()
    
    #type pass word
    adbInput("2908")


# To replace space in string with %s for complete massage send
def replace_spaces_with_percent_s(input_string):
    return input_string.replace(' ', '%s')
