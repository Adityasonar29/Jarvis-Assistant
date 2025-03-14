import multiprocessing
import time
import subprocess
from background_tasks import start_background_tasks

#this is multithredding file

#to run jarvis
def startJarvis():
    #code for process one 
    print("Process 1 is Running.")
    from main import start
    start()

#to run hot word detection
def listenHotword():
    #code for process two
    print("Process 2 is Running.")
    from engine.features import hotword
    hotword()

    # Start both processes
if __name__ == '__main__':
        # Start background tasks (reminders)
        start_background_tasks()  
        
        p1 = multiprocessing.Process(target=startJarvis)
        p2 = multiprocessing.Process(target=listenHotword)

        p1.start()
        
        
        subprocess.call([r"device.bat"])
        
        
        p2.start()
        p1.join()
        

        if p2.is_alive():
            p2.terminate()
            p2.join()

        print("system stop")
        
        