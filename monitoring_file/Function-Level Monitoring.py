import time
import psutil
import os

def monitor_function(func):
    """Decorator to monitor CPU, RAM, and execution time for a function"""
    def wrapper(*args, **kwargs):
        process = psutil.Process(os.getpid())  # Get current process
        start_time = time.time()
        start_memory = process.memory_info().rss / (1024 * 1024)  # Convert to MB
        start_cpu = process.cpu_percent(interval=None)  # Get CPU %
        start_gpu = process.gpu_percent(interval=None)  # Get GPU %

        result = func(*args, **kwargs)  # Run the function

        end_time = time.time()
        end_memory = process.memory_info().rss / (1024 * 1024)
        end_cpu = process.cpu_percent(interval=None)
        end_gpu = process.gpu_percent(interval=None)

        print(f"📌 Function: {func.__name__}")
        print(f"⏳ Execution Time: {end_time - start_time:.2f} sec")
        print(f"💾 Memory Usage: {end_memory - start_memory:.2f} MB")
        print(f"GPU Usage: {end_gpu - start_gpu:.2f}")
        print(f"⚡ CPU Usage: {end_cpu:.2f}%\n")

        return result

    return wrapper

# Example Usage: Track Speech-to-Text Function
@monitor_function
def transcribe_audio():
    time.sleep(2)  # Simulating function execution
    return "Transcribed Text"

print(transcribe_audio())
