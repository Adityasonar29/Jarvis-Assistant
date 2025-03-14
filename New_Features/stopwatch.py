import time
import threading
import speech_recognition as sr
import pyttsx3

class Stopwatch:
    def __init__(self):
        self.running = False
        self.start_time = None
        self.elapsed_time = 0
        self.thread = None  # Keep track of the stopwatch thread

    def start(self):
        if not self.running:
            self.running = True
            self.start_time = time.time() - self.elapsed_time
            self.thread = threading.Thread(target=self.run, daemon=True)
            self.thread.start()

    def run(self):
        while self.running:
            self.elapsed_time = time.time() - self.start_time
            time.sleep(0.1)

    def stop(self):
        if self.running:
            self.running = False

    def reset(self):
        self.stop()
        self.elapsed_time = 0
        self.start_time = None

    def get_time(self):
        return round(self.elapsed_time, 2)


class VoiceAssistant:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 170)
        self.engine.setProperty('volume', 1.0)
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[0].id)

    def speak(self, text):
        self.engine.say(text)
        print(text)
        self.engine.runAndWait()


def listen_for_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for command...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=5)
            command = recognizer.recognize_google(audio).lower()
            return command
        except sr.UnknownValueError:
            return None
        except sr.RequestError:
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None


def main():
    stopwatch = Stopwatch()
    assistant = VoiceAssistant()

    assistant.speak("Stopwatch is ready. Say start, stop, reset, or exit.")
    print("Say 'start', 'stop', 'reset', or 'exit'.")

    while True:
        command = listen_for_command()
        if command:
            if "start" in command:
                if not stopwatch.running:
                    stopwatch.start()
                    assistant.speak("Stopwatch started.")
                else:
                    assistant.speak("Stopwatch is already running.")

            elif "stop" in command:
                if stopwatch.running:
                    stopwatch.stop()
                    assistant.speak(f"Stopped at {stopwatch.get_time()} seconds.")
                    
                    break
                else:
                    assistant.speak("Stopwatch is not running.")
                    break

            elif "reset" in command:
                stopwatch.reset()
                assistant.speak("Stopwatch reset.")

            elif "exit" in command:
                assistant.speak("Exiting stopwatch.")
                break


if __name__ == "__main__":
    main()
