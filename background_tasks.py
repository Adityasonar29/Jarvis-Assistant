import threading
import time


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
    print("✅ Background tasks started.")

