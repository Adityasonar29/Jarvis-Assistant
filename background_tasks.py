import threading
import time
import datetime
from monitoring_file.monitoring_all import monitor_system
import os
import json
from New_Features.alarm import set_alarm, convert_to_24hr_format

# Path for storing alarms
ALARMS_FILE = os.path.join(os.path.dirname(__file__), "alarms.json")

# Global list to store active alarms
active_alarms = []

def load_alarms():
    """Load saved alarms from file"""
    if os.path.exists(ALARMS_FILE):
        try:
            with open(ALARMS_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading alarms: {e}")
    return []

def save_alarms():
    """Save active alarms to file"""
    try:
        with open(ALARMS_FILE, 'w') as f:
            json.dump(active_alarms, f)
    except Exception as e:
        print(f"Error saving alarms: {e}")

def add_alarm(time_str):
    """
    Add a new alarm
    time_str should be in 24-hour format as string, e.g., "14:30"
    """
    # Create alarm object
    alarm = {
        "time": time_str,
        "active": True,
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Add to active alarms
    active_alarms.append(alarm)
    
    # Save to file
    save_alarms()
    
    return f"Alarm set for {time_str}"

def start_alarm_checker():
    """Function to continuously check for alarms."""
    print("⏰ Alarm system started...")
    
    # Load saved alarms
    global active_alarms
    active_alarms = load_alarms()
    
    while True:
        current_time = datetime.datetime.now().strftime("%H:%M")
        
        # Check each alarm
        for alarm in active_alarms[:]:  # Create a copy to safely modify during iteration
            if alarm["active"] and alarm["time"] == current_time:
                print(f"⏰ ALARM: {current_time}!")
                
                # Use the set_alarm function from New_Features/alarm.py to play the sound
                set_alarm(alarm["time"])
                
                # Mark alarm as inactive
                alarm["active"] = False
                save_alarms()
                
                # Remove inactive alarms
                active_alarms = [a for a in active_alarms if a["active"]]
                save_alarms()
        
        time.sleep(30)  # Check alarms every 30 seconds

def start_reminder_checker():
    """Function to continuously check for reminders."""
    print("📌 Reminder system started...")
    from engine.features import check_reminders
    while True:
        check_reminders()
        time.sleep(10)  # Check reminders every 10 seconds

def start_background_tasks():
    """Start all background tasks as threads."""
    # Creating a daemon thread for reminders
    reminder_thread = threading.Thread(target=start_reminder_checker, daemon=True)
    reminder_thread.start()
    
    # Creating a daemon thread for alarms
    alarm_thread = threading.Thread(target=start_alarm_checker, daemon=True)
    alarm_thread.start()
    
    
    #monitoring the system performance
    monitor_sys = threading.Thread(target=monitor_system, daemon=True)
    monitor_sys.start()
    
    print("✅ Background tasks started.")

# If this file is run directly, start the background tasks
if __name__ == "__main__":
    start_background_tasks()

