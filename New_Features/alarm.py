import datetime
import re
import time
import winsound  # For Windows users

def convert_to_24hr_format(time_str):
    """
    Convert various time formats to 24-hour format (HH:MM)
    Handles inputs like "7:30 AM", "6 PM", "14:30", etc.
    """
    # If already in 24-hour format
    if re.match(r'^\d{1,2}:\d{2}$', time_str):
        return time_str
    
    # Try to extract hours, minutes, and AM/PM
    am_pm_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm|AM|PM)?', time_str)
    
    if am_pm_match:
        hours = int(am_pm_match.group(1))
        minutes = int(am_pm_match.group(2)) if am_pm_match.group(2) else 0
        am_pm = am_pm_match.group(3).lower() if am_pm_match.group(3) else None
        
        # Convert to 24-hour format
        if am_pm == 'pm' and hours < 12:
            hours += 12
        elif am_pm == 'am' and hours == 12:
            hours = 0
            
        return f"{hours:02d}:{minutes:02d}"
    
    # If no match found, return original string
    return time_str

def set_alarm(alarm_time):
    """
    Play alarm sound when called
    This function is called by the background_tasks.py when an alarm time is reached
    """
    print(f"⏰ ALARM: {alarm_time}!")
    
    # Play a more noticeable alarm sound
    for _ in range(5):  # Play sound 5 times
        winsound.Beep(1000, 500)  # frequency = 1000Hz, duration = 500ms
        time.sleep(0.5)
        winsound.Beep(1500, 500)  # frequency = 1500Hz, duration = 500ms
        time.sleep(0.5)
    
    return True

# Example usage
if __name__ == "__main__":
    test_times = ["7:30 AM", "6 PM", "14:30", "12:00 AM", "12:00 PM"]
    for time_str in test_times:
        print(f"{time_str} -> {convert_to_24hr_format(time_str)}")
        
    # Test alarm sound
    set_alarm("14:30") 