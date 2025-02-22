import calendar
import random
import sys
import os

from plyer import notification
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import os
from shlex import quote
import re
import sqlite3
import struct
import subprocess
import time as timer
import webbrowser
import numpy as np
import sounddevice as sd
from playsound import playsound
import eel
import pyaudio
import pyautogui
from engine.command import speak
from engine.config import ASSISTANT_NAME
from datetime import datetime, timedelta

# Playing assiatnt sound function
import pywhatkit as kit
import pvporcupine


from engine.helper import extract_yt_term, get_day_time, get_next_day_date, remove_words, tapEvents
from hugchat import hugchat

from kaushik_Adv_jar.backend.Text_To_Speech import TextToSpeech

con = sqlite3.connect("jarvis.db")
cursor = con.cursor()

@eel.expose
def playAssistanatSound():
    music_dir = "www\\assets\\audio\\start_sound.mp3"
    playsound(music_dir)

@eel.expose    
def openCommand(query):
    query = query.replace(ASSISTANT_NAME, "")
    query = query.replace("open", "")


    app_name =query.lower()

    if app_name != "":

        try:
            cursor.execute(
                "SELECT path FROM sys_command WHERE LOWER(name) = LOWER(?);", (app_name,))
            results = cursor.fetchall()

            if len(results) != 0:
                speak("Opening "+query)
                os.startfile(results[0][0])

            elif len(results) == 0: 
                cursor.execute(
                'SELECT url FROM web_command WHERE LOWER(name) = LOWER(?);', (app_name,))
                results = cursor.fetchall()
                
                if len(results) != 0:
                    speak("Opening "+query)
                    webbrowser.open(results[0][0])

                else:
                    speak("Opening "+query)
                    try:
                        os.system('start '+query)
                    except:
                        speak("not found")
        except Exception as e:
            print(e)
            speak("some thing went wrong")

       

def PlayYoutube(query):
    search_term = extract_yt_term(query)
    speak("Playing "+search_term+" on YouTube")
    kit.playonyt(search_term)

def check_reminders():
    """Check for due reminders and send notifications."""
    try:
        conn = sqlite3.connect('jarvis.db')
        cursor = conn.cursor()
        
        # Get current time and date
        now = datetime.now()
        current_time = now.strftime("%I:%M %p")
        current_date = now.strftime("%d/%m/%Y")
        
        # Query for reminders that are due
        cursor.execute('''
            SELECT id, message, time, date, recurrence, end_date 
            FROM reminders 
            WHERE date = ? AND time = ?
        ''', (current_date, current_time))
        
        due_reminders = cursor.fetchall()
        
        for reminder in due_reminders:
            id, message, time, date, recurrence, end_date = reminder
            try:
                notification.notify(
                    app_name='Jarvis',
                    title='📅 Reminder by Jarvis',
                    message=f"{message}\nTime: {time}\nDate: {date}",
                    app_icon=None,
                    timeout=10
                )
                print(f"✨ Notification sent for: {message}")
                TextToSpeech(f"{message} on {time}")
                
                            # Handle recurrence
                if recurrence:
                    # Calculate next occurrence
                    next_date = datetime.strptime(date, "%d/%m/%Y")
                    
                    if recurrence == "daily":
                        next_date += timedelta(days=1)
                    elif recurrence == "weekly":
                        next_date += timedelta(days=7)
                    elif recurrence == "monthly":
                        next_date += timedelta(days=30)
                                # Check if end_date is reached
                    if end_date and next_date > datetime.strptime(end_date, "%d/%m/%Y"):
                        cursor.execute('DELETE FROM reminders WHERE id = ?', (id,))
                    else:
                        # Update to next occurrence
                        cursor.execute('''
                            UPDATE reminders 
                            SET date = ? 
                            WHERE id = ?
                        ''', (next_date.strftime("%d/%m/%Y"), id))
                else:
                # Optionally remove the reminder after it's shown
                    cursor.execute('DELETE FROM reminders WHERE id = ?', (id,))
                    conn.commit()
                    timer.sleep(2)
            
            except Exception as e:
                print(f"❌ Notification error: {e}")
            
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    finally:
        conn.close()
                

def hotword():
    porcupine=None
    paud=None
    audio_stream=None
    try:
       
        # pre trained keywords    
        porcupine=pvporcupine.create(keywords=["jarvis","alexa"]) 
        paud=pyaudio.PyAudio()
        audio_stream=paud.open(rate=porcupine.sample_rate,channels=1,format=pyaudio.paInt16,input=True,frames_per_buffer=porcupine.frame_length)
        
        # loop for streaming
        while True:
            keyword=audio_stream.read(porcupine.frame_length)
            keyword=struct.unpack_from("h"*porcupine.frame_length,keyword)

            # processing keyword comes from mic 
            keyword_index=porcupine.process(keyword)

            # checking first keyword detetcted for not
            if keyword_index>=0:
                print("hotword detected")

 
                # pressing shorcut key win+j
                import pyautogui as autogui
                autogui.keyDown("win")
                autogui.press("j")
                timer.sleep(2)
                autogui.keyUp("win")
                
    except:
        if porcupine is not None:
            porcupine.delete()
        if audio_stream is not None:
            audio_stream.close()
        if paud is not None:
            paud.terminate()

# find contacts
def findMail(query):
    
    words_to_remove = [ASSISTANT_NAME,'send', 'mail','to','answer','of']
    query = remove_words(query, words_to_remove)

    try:
        query = query.strip().lower()
        cursor.execute("SELECT email FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?", ('%' + query + '%', query + '%'))
        results = cursor.fetchall()
        print(results[0][0])
        email_id_str = str(results[0][0])

        return email_id_str, query
    except:
        try:
            speak('mail not exist in contacts')  
        except:
            TextToSpeech('mail not exist in contacts')
        return 0, 0
    
# send email
def sendMail(email,subject, body, attachment = None):
    import smtplib
    from engine.config import MY_PASS_GMAIL_OPENING,MI_MAIL
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from email import encoders
    from email.mime.base import MIMEBase

    # Email setup
    sender_email = MI_MAIL
    receiver_email = email
    password = MY_PASS_GMAIL_OPENING  # Use an app-specific password for Gmail

    # Creating the email
    message = MIMEMultipart(body, "plain")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email

    # File attachment
    file_path = attachment  # Replace with your file path
    if file_path:
        try:
            file_name = file_path.split("/")[-1]  # Extract the file name
            with open(file_path, "rb") as file:
                # Create a MIMEBase instance
                part = MIMEBase("application", "octet-stream")
                part.set_payload(file.read())

            # Encode the payload in Base64
            encoders.encode_base64(part)

            # Add headers for the attachment
            part.add_header(
                "Content-Disposition",
                f"attachment; filename={file_name}",
            )
            # Attach the file to the message
            message.attach(part)
            print(f"Attached file: {file_name}")
        except Exception as e:
            print(f"Error attaching file: {e}")
    else:
        print("No attachment provided.")
        
    # Send the email
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  # Encrypts the connection
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")
# find contacts
# con.close()
def findContact(query):
    words_to_remove = [ASSISTANT_NAME, 'make', 'a', 'to', 'on', 'phone', 'call', 'send', 'message', 'whatsapp', 'video']
    query = remove_words(query, words_to_remove)

    try:
        query = query.strip().lower()
        # Create a new SQLite connection and cursor
        conn = sqlite3.connect('jarvis.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT mobile_no FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?", ('%' + query + '%', query + '%'))
        results = cursor.fetchall()
        conn.close()  # Close the connection
        if results:
            mobile_number_str = str(results[0][0])
            if not mobile_number_str.startswith('+91'):
                mobile_number_str = '+91' + mobile_number_str
            print(mobile_number_str, query)
            return mobile_number_str, query
        else:
            raise ValueError("Contact not found")
    except Exception as e:
        print(f"Error finding contact: {e}")
        try:
            speak('not exist in contacts')
        except:
            TextToSpeech('not exist in contacts')
        return None, None

    
def whatsApp(mobile_no, massage, flag, name):
    

    if flag == 'massage':
        target_tab = 13
        jarvis_massage = "massage send successfully to "+name

    elif flag == 'call':
        print("call")# debug
        target_tab = 7
        massage = ''
        jarvis_massage = "calling to "+name

    elif flag == 'video call':
        print("vedio call") # debug
        target_tab = 5
        massage = ''
        jarvis_massage = "staring video call with "+name


    # Encode the massage for URL
    encoded_massage = quote(massage)
    print(encoded_massage)
    # Construct the URL
    whatsapp_url = f"whatsapp://send?phone={mobile_no}&text={encoded_massage}"

    # Construct the full command
    full_command = f'start "" "{whatsapp_url}"'

    # Open WhatsApp with the constructed URL using cmd.exe
    subprocess.run(full_command, shell=True)
    timer.sleep(5)
    subprocess.run(full_command, shell=True)
    
    pyautogui.hotkey('ctrl', 'f')

    for i in range(1, target_tab):
        pyautogui.hotkey('tab')

    pyautogui.hotkey('enter')
    try:
        speak(jarvis_massage)
    except:
        TextToSpeech(jarvis_massage)

# chat bot 
def chatBot(query):
    user_input = query.lower()
    chatbot = hugchat.ChatBot(cookie_path="engine\\cookies.json")
    id = chatbot.new_conversation()
    chatbot.change_conversation(id)
    response =  chatbot.chat(user_input)
    print(response)
    speak(response)
    return response

# android automation

def makeCall(name, mobileNo):
    mobileNo =mobileNo.replace(" ", "")
    try:
        speak("Calling "+name)
    except:
        TextToSpeech("Calling "+name)
    command = 'adb shell am start -a android.intent.action.CALL -d tel:'+mobileNo
    os.system(command)


# to send massage
def sendMassage(massage, mobileNo, name):
    from engine.helper import replace_spaces_with_percent_s, goback, keyEvent, tapEvents, adbInput, check_device_lock_status_batch
    massage = replace_spaces_with_percent_s(massage)
    mobileNo = replace_spaces_with_percent_s(mobileNo)
    
    check_device_lock_status_batch()
    
    speak("sending massage")
    timer.sleep(1)
    keyEvent(3)
    # open sms app
    tapEvents(968, 1665)
    #start chat
    tapEvents(515, 502)
    # search mobile no
    adbInput(mobileNo)
    #tap on name
    tapEvents(541, 475)
    # tap on input
    tapEvents(442, 2196)
    #massage
    adbInput(massage)
    #send
    tapEvents(977, 1168)
    speak("massage send successfully to "+name)
    
    
def openCamVideo(query):
    import os
    from engine.helper import check_device_lock_status_batch, keyEvent, tapEvents, adbInput
    from engine.command import speak, takecommand

    record_start_keywords_front = [ "record us", "record me"]
    record_start_keywords_back = ["record this", "record my back", "record that"]
    record_stop_keywords = ["stop recording", "end recording", "finish recording"]

    # Check if the query is to start recording
    if any(keyword in query for keyword in record_start_keywords_front):
        command = "adb shell am start -a android.media.action.VIDEO_CAMERA --ei android.intent.extras.CAMERA_FACING 1"
    elif any(keyword in query for keyword in record_start_keywords_back):
        command = "adb shell am start -a android.media.action.VIDEO_CAMERA --ei android.intent.extras.CAMERA_FACING 0"
        
    # Keep listening for a stop command
    check_device_lock_status_batch()
    os.system(command)
    speak("Starting the recording, Sir.")    
    tapEvents(548,1998)
    speak("Recording is in progress. Let me know when to stop.")
    while True:
        user_input = takecommand()
        if any(keyword in user_input for keyword in record_stop_keywords):
            speak("Stopping the recording.")
            # Simulate stopping the recording (adjust command as per the recording app)
            tapEvents(548, 1998)
            break
        elif "pause" in user_input:
            tapEvents(243, 2002)
            speak("Pausing the recording.")
            speak("tell me when to unpause")
            while True:
                user_input_pa = takecommand()
                if user_input_pa != "":
                    if "unpause" in user_input_pa:
                        tapEvents(243, 2002)
                        speak("Unpausing the recording.")
                        break
            # Simulate pausing the recording (adjust command as per the recording app)
        elif "take photo" in user_input:
            tapEvents(856, 2029)    
            
        else:
            speak("I didn't understand. Please say 'stop recording' when you're done.")

    else:
        speak("I didn't understand your recording request. Please say 'start recording' or 'stop recording'.")


def openCam(query):
    import os
    from engine.helper import check_device_lock_status_batch, keyEvents
    from engine.command import takecommand,speak
    check_device_lock_status_batch()
    
    back_cam_keywords = ["photo", "shot", "image"]
    front_cam_keywords = ["selfie"]
    
    if any(keyword in query for keyword in back_cam_keywords + front_cam_keywords):
        print(query)
        
        # Determine which camera to open
        if any(keyword in query for keyword in back_cam_keywords):
            command = "adb shell am start -a android.media.action.STILL_IMAGE_CAMERA --ei android.intent.extras.CAMERA_FACING 0"
        elif any(keyword in query for keyword in front_cam_keywords):
            command = "adb shell am start -a android.media.action.STILL_IMAGE_CAMERA --ei android.intent.extras.CAMERA_FACING 1"
        os.system(command)
        
        speak("The camera is ready, Sir. Tell me when to take the shot.")
        
        while True:
            user_input = takecommand()
            if "take" in user_input or "click" in user_input:
                tapEvents(545,11)
                speak("Look at the camera, please! Say cheese.")
                os.system("adb shell input tap 540 2000")  # Tap to take photo
                speak("The shot has been taken.")
                break
            else:
                speak("I did not get that, please say 'take' or 'click'.")
        
        speak("Do you want to see it?")
        
        while True:
            user_input = takecommand().lower()
            if "yes" in user_input:
                os.system("adb shell input tap 231 2018")  # Tap to open gallery
                speak("Here is your photo.")
                timer.sleep(3)
                break
            elif "no" in user_input or "don't" in user_input:
                speak("Okay, Sir.")
                keyEvents(3)  # Simulate home key press
                break
            else:
                speak("I did not get that, please say 'yes' or 'no'.")
    else:
        speak("I did not get that, please say 'take a photo' or 'take a selfie'.")
    
def voiceRecording():
    import sounddevice as sd
    from scipy.io.wavfile import write
    import time
    import os
    import numpy as np
    from pydub import AudioSegment
    from pydub.silence import detect_nonsilent
    # from engine.command import speak, takecommand

    fs = 44100  # Sample rate
    output_path = "recordings"  # Directory to save recordings
    silence_threshold = -40  # Silence threshold in dBFS
    silence_duration = 5  # Duration of silence in seconds to stop recording

    # Ensure the recordings directory exists
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    speak("Sir, please start speaking. I will record until silence is detected.")
    
    recording = []
    try:
        with sd.InputStream(samplerate=fs, channels=1, dtype='int16') as stream:
            print("Recording...")
        silence_counter = 0  # Counter for silent chunks
        max_silence_frames = int(silence_duration * fs / 1024)  # Silence duration in frames

        with sd.InputStream(samplerate=fs, channels=1, dtype='int16') as stream:
#             Opens an audio input stream:
#                 samplerate=fs: Sets the sample rate.
#                 channels=1: Mono recording.
#                 dtype='int16': Audio data format (16-bit signed integers).
            print("Recording...")
            while True:
                data = stream.read(1024)[0]  # Read 1024 frames
                audio_data = np.frombuffer(data, dtype=np.int16)
                recording.append(audio_data)

                # Check if the current chunk is silent
                audio_segment = AudioSegment(
                    audio_data.tobytes(), frame_rate=fs, sample_width=2, channels=1
                )
                if audio_segment.dBFS < silence_threshold:
                    silence_counter += 1
                else:
                    silence_counter = 0  # Reset silence counter if voice is detected

                # Stop recording if silence exceeds the threshold
                if silence_counter > max_silence_frames:
                    speak("Silence detected. Stopping recording.")
                    speak("Wait until the process of saving recording is been done.")
                    break


        # Convert recording to a NumPy array
        if recording:
            recording = np.concatenate(recording)
            audio_segment = AudioSegment(
                recording.tobytes(),
                frame_rate=fs,
                sample_width=recording.dtype.itemsize,
                channels=1,
            )

            # Detect non-silent parts
            nonsilent_ranges = detect_nonsilent(
                audio_segment, min_silence_len=int(silence_duration * 1000), silence_thresh=silence_threshold
            )

            if nonsilent_ranges:
                # Save only the non-silent parts
                output_audio = audio_segment[nonsilent_ranges[0][0] : nonsilent_ranges[-1][1]]
                timestamp = int(time.time())
                filename = os.path.join(output_path, f"recording_{timestamp}.wav")
                output_audio.export(filename, format="wav")
                speak("Recording process complete. It has been saved.")
            else:
                speak("No significant audio was recorded.")

    except Exception as e:
        speak(f"An error occurred while recording: {str(e)}")
        
        
def add_task_to_db(message, time, date, recurrence=None, end_date=None):
    """Add a new reminder task to the database."""
    try:
        conn = sqlite3.connect('jarvis.db')
        cursor = conn.cursor()
        
        # Convert date list to string if it's a list
        if isinstance(date, list):
            date_str = date[0] if date else datetime.now().strftime("%d/%m/%Y")
        else:
            date_str = date
            
        # Convert time to string if needed
        time_str = time[0] if isinstance(time, list) else time
        
        cursor.execute('''
            INSERT INTO reminders (message, time, date, recurrence, end_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (message, time, date, recurrence, end_date))
        conn.commit()
        print(f"✅ Reminder Added: {message} at {time_str}, Date: {date_str}")
        if recurrence:
            print(f"🔄 Recurrence: {recurrence}")
            if end_date:
                print(f"🔚 Until: {end_date}")
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    finally:
        conn.close()
        
def process__reminder(query):
    """Process reminder query and extract date, time, and recurrence information."""
    query_lower = query.lower()
    current_date = datetime.now()
    recurrence = None
    end_date = None
    absolute_dates = []
    formatted_times = []

    # 1. Extract end date first (if specified)
    end_date_match = re.search(r'until\s+(\d{2}/\d{2}/\d{4})', query_lower)
    if end_date_match:
        end_date = end_date_match.group(1)

    # 2. Handle recurrence and day patterns
    # This should be first because it affects date calculation
    if "daily" in query_lower or "everyday" in query_lower or "every day" in query_lower:
        recurrence = "daily"
        absolute_dates.append(current_date.strftime("%d/%m/%Y"))
    
    else:
        # Check for weekly patterns (every Monday, every Saturday, etc.)
        day_pattern = r'(?:every\s+)?(?:on\s+)?(' + '|'.join(calendar.day_name) + r')(?:s(?:\W|$)|\W|$)'
        day_match = re.search(day_pattern, query_lower, re.IGNORECASE)
        
        if day_match:
            print("Matched day:", day_match.group(1))
            day_name = day_match.group(1).lower()
            next_date = get_next_day_date(day_name)
            
            if next_date:  # Ensure it is not None
                if 'every' in query_lower:
                    recurrence = 'weekly'
                absolute_dates.append(next_date.strftime("%d/%m/%Y"))
            else:
                print(f"❌ Error: Could not determine next date for {day_name}")


        else:
            # Handle relative dates if no specific day mentioned
            if "tomorrow" in query_lower:
                absolute_dates.append((current_date + timedelta(days=1)).strftime("%d/%m/%Y"))
            elif "next week" in query_lower:
                absolute_dates.append((current_date + timedelta(weeks=1)).strftime("%d/%m/%Y"))
            elif "next month" in query_lower:
                absolute_dates.append((current_date + timedelta(days=30)).strftime("%d/%m/%Y"))
            elif "today" in query_lower:
                absolute_dates.append(current_date.strftime("%d/%m/%Y"))

    # 3. Handle time specification
    # First check for time words (morning, afternoon, etc.)
    time_words = ['morning', 'afternoon', 'evening', 'night']
    time_match = re.search('|'.join(time_words), query_lower)
    
    if time_match:
        specified_time = get_day_time(time_match.group())
        if specified_time:
            formatted_times = [specified_time]
    else:
        # Check for specific times (2:30 PM, 3 AM, etc.)
        time_extract_pattern = r"(([0-9]|1[0-2])):?([0-5][0-9])?\s*(am|pm|a\.m\.|p\.m\.|AM|PM)"
        time_matches = re.findall(time_extract_pattern, query_lower)
        
        if time_matches:
            for match in time_matches:
                hour = match[1]
                minute = match[2] if match[2] else "00"
                period = match[3].upper().replace(".", "")[:2]
                formatted_times.append(f"{int(hour):02d}:{minute} {period}")

    # 4. Set defaults if nothing specified
    if not absolute_dates:
        absolute_dates.append(current_date.strftime("%d/%m/%Y"))
    if not formatted_times:
        formatted_times.append(current_date.strftime("%I:%M %p"))

    # 5. Process message
    message = query
    # Remove dates and times
    message = re.sub(r'\d{1,2}/\d{1,2}/\d{4}', '', message)
    message = re.sub(r'\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)', '', message, flags=re.IGNORECASE)
    
    # Remove common words
    words_to_remove = [
        'today', 'tomorrow', 'next week', 'next month', 'at', 'on', 'for',
        "I", "I'm", "I am", "me", "my", "need to", "going to",
        "want to", "would like to", "must", "should", "will",
        "have a", "got a", "got", "having", "having a", "go", "add", "reminde", "reminder"
    ]
    for word in words_to_remove:
        message = re.sub(r'\b' + word + r'\b', '', message, flags=re.IGNORECASE)
    
    message = re.sub(r'\s+', ' ', message).strip()

    # 6. Add natural language prefix
    prefixes = [
        "You have ", "You need to ", "Remember, you have ",
        "Don't forget you have ", "There is ", "You should attend ",
        "Make sure to attend ", "You're scheduled for "
    ]
    if not any(message.lower().startswith(prefix.lower()) for prefix in prefixes):
        message = random.choice(prefixes) + message.lower()

    # 7. Add to database
    add_task_to_db(
        message=message,
        time=formatted_times[0],
        date=absolute_dates[0],
        recurrence=recurrence,
        end_date=end_date
    )

    return absolute_dates[0], formatted_times[0], message