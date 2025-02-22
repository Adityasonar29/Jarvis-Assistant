# At the top of the file, update imports
import random
import sqlite3
import threading
from datetime import datetime, timedelta
import re
from plyer import notification
import time as timer

from kaushik_Adv_jar.backend.Text_To_Speech import TextToSpeech
from kaushik_Adv_jar.backend.speech_to_text import SpeechRecognition

import calendar


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
        TextToSpeech(f"✅ Reminder Added: {message} at {time_str}, Date: {date_str}")
        if recurrence:
            TextToSpeech(f"🔄 Recurrence: {recurrence}")
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

def start_reminder_checker():
    """Start the reminder checking scheduler."""
    print("🚀 Starting reminder checker...")
    
    while True:
        check_reminders()
        timer.sleep(60)  # Check every 59 seconds

if __name__ == "__main__":
    # Initialize database
    
    # Start the reminder checker in a separate thread
    print("📌 Starting reminder system...")
    checker_thread = threading.Thread(target=start_reminder_checker, daemon=True)
    checker_thread.start()
    
    # Keep the main thread running
    try:
        while True:
            command = SpeechRecognition()
            if command.lower() == 'exit':
                break
            date, time, msg = process__reminder(command)
            TextToSpeech(f"Added reminder: {msg} at {time} on {date}")
            
    except KeyboardInterrupt:
        print("\n👋 Shutting down reminder system...")