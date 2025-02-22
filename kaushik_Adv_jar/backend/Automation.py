import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from kaushik_Adv_jar.backend.Text_To_Speech import TextToSpeech
from kaushik_Adv_jar.backend.speech_to_text import SpeechRecognition
from engine.websiteauto import open_web
from AppOpener import close, open as appopen 
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
# from requests_html import HTMLSession
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import pyautogui
import keyboard 
import asyncio
import os
import time
import wikipedia

env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")



# Define CSS classes for parsing specific elements in HTML content.


useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4986 Safari/537.36'

client = Groq(api_key=GroqAPIKey)

professional_responses = [
    "I have found the following information for you, sir.",
    "Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
    "I'm at your service for any additional questions or support you may need-don't hesitate to ask.",
]

messages = []

SystemChatBot = [{"role": "system", "content": f"Hello, I am {os. environ['Username']}, You're a content writer. You have to write content like letters, codes, applications, essays, notes, songs,poems,emails etc."}]

def GoogleSearch(Topic):
    search(Topic)
    return True


# Function to generate content using AI and save it to a file.
def Content(Topic):

# Nested function to open a file in Notepad.
    def OpenNotepad(File):
        default_text_editor = 'notepad.exe'
        subprocess.Popen([default_text_editor, File])
                  
    def ContentWriter(prompt):
            messages.append({"role": "user", "content": f"{prompt}"})
            completions = client.chat.completions.create(
                model = "mixtral-8x7b-32768",
                messages= SystemChatBot + messages,
                max_tokens=2048,
                temperature=0.7,
                top_p=1,
                stream=True,
                stop=None
            )
    
            Answer = ""

            for chunk in completions:
                if chunk.choices[0].delta.content:
                    Answer += chunk.choices[0].delta.content
                
            Answer = Answer.replace("</s>", "")
            messages.append({"role": "assistant", "content": f"{Answer}"})
            return Answer

    Topic: str = Topic.replace("Content", "")
    ContentByAI = ContentWriter(Topic)

    with open(rf"Data\content\{Topic.lower().replace(' ','')}.txt", "w", encoding="utf-8") as file:
        file.write(ContentByAI)
        file.close()
    
    OpenNotepad(rf"Data\content\{Topic.lower().replace(' ','')}.txt")
    return True



def YoutubeSearch(Topic):
    Url4Search = f"https://www.youtube.com/results?search_query={Topic}"
    webbrowser.open(Url4Search)
    return True


# YoutubeSearch("How to make a website")

def PlayYoutube(query):
    playonyt(query)
    return True

# wikipedia summary
def WikipediaSearch(Topic):
    try:
        summary = wikipedia.summary(Topic, sentences=5)
        print(summary)
        TextToSpeech(summary)
        return summary
    except Exception as e:
        print(f"[Error] Error in searching Wikipedia for {Topic}: {e}")
        return False

# PlayYoutube("Never gonna give you up")

def OpenApp(app):
    try:
        appopen(app, match_closest=True, output=True, throw_error=True)
        return True
    except Exception as e:
        print(f"[WARNING] App not found. Error: {e}. Falling back to web search.")

        open_web(app)

def CloseApp(app):
    app = app.lower()
    if "chrome" in app:
        pass
    else:
        try:
            close(app, match_closest=True, output=True, throw_error=True)
            print("App Closed")
            return True
        except Exception as e:
            print(f"[Error] Error in Openning the {app}: {e}")
            return False
        
# Send mail using 
def Send_mail_h(query):
    
    from engine.features import sendMail, findMail
    email_reciver, name  =findMail(query)
    query = query.replace(f"{email_reciver or name}", "")
    message = query
    TextToSpeech("do you what to include any specific subject")
    userinput = SpeechRecognition()
    if userinput.startswith("yes"):
        subject = SpeechRecognition()
    else:
        subject = ("Nothing")
    sendMail(email_reciver,subject=subject,body=message)

def call(nameorcontact):
    from engine.features import findContact,makeCall
    contact_no, name = findContact(nameorcontact)
    print(f"Found Contact: {name}, Number: {contact_no}")  # Debugging output

    if contact_no and contact_no != 0:
        print(f"Calling {name} at {contact_no}")
        makeCall(name, contact_no)
    else:
        print("[ERROR] Contact not found!")

def Reminder(query):
    from engine.features import process__reminder
    process__reminder(query)
        
    
def WhatsApp(query):
    from engine.features import  whatsApp, findContact
    print("Whatsapp fuc activeted")
    
    contact_no, name = findContact(query)
    if(contact_no != 0):
        massage = ""
        if "send message" in query:
            query = query.replace("send message", "")
            print(contact_no, name)
            query = query.replace(f"{contact_no or name}", "")
            massage = 'message'
                        
        elif "video call" in query:
            massage = 'video call'
                    
        else:
            TextToSpeech("plese say phone call")                
        whatsApp(contact_no, query, massage, name)



def System(command):
    def mute():
        keyboard.press_and_release("volume mute")

    def unmute():
        keyboard.press_and_release("volume mute")

    def volumeup():
        keyboard.press_and_release("volume up")
    
    def volumedown():
        keyboard.press_and_release("volume down")

    def shutdown():
        os.system("shutdown /s /t 1")
    
    def restart():
        os.system("shutdown /r /t 1")

    def lock():
        os.system("rundll32.exe user32.dll,LockWorkStation")

    def sleep():
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

    if command =="mute":
        mute()
    elif command =="unmute":
        unmute()
    elif command =="volume up":
        volumeup()
    elif command =="volume down":
        volumedown()
    elif command =="shutdown":
        shutdown()
    elif command =="restart":
        restart()
    elif command =="lock":
        lock()
    elif command =="sleep":
        sleep()
    return True


async def TranslateAndExecute(commands:list[str]):

    funcs = []

    for command in commands:
        if command.startswith("open "):
            if "open it" in command:
                pass
            if "open file" == command:
                pass
            else: 
                fun = asyncio.to_thread(OpenApp, command.removeprefix("open "))
                funcs.append(fun)
        elif command.startswith("general "):
            pass
        
        elif command.startswith("realtime "):
            pass
        
        elif command.startswith("close "):
            fun = asyncio.to_thread(CloseApp, command.removeprefix("close "))
            funcs.append(fun)
            
        elif command.startswith("play "):
            fun = asyncio.to_thread(PlayYoutube, command.removeprefix("play "))
            funcs.append(fun)
            
        elif command.startswith("content "):
            fun = asyncio.to_thread(Content, command.removeprefix("content "))
            funcs.append(fun)
            
        elif command.startswith("google search "):
            fun = asyncio.to_thread(GoogleSearch, command.removeprefix("google search "))
            funcs.append(fun)
        
        elif command.startswith("youtube search "):
            fun = asyncio.to_thread(YoutubeSearch, command.removeprefix("youtube search "))
            funcs.append(fun)
            
        elif command.startswith("system "):
            fun = asyncio.to_thread(System, command.removeprefix("system "))
            funcs.append(fun)
            
        elif command.startswith("send mail"):
            fun = asyncio.to_thread(Send_mail_h, command.removeprefix("send mail "))
            funcs.append(fun)
        
        elif command.startswith("send mail"):
            print("Calling Send_mail_h")  # Debugging output
            fun = asyncio.to_thread(Send_mail_h, command.removeprefix("send mail "))
            funcs.append(fun)
            
        elif command.startswith("call"):
            print("Calling call")  # Debugging output
            fun = asyncio.to_thread(call, command.removeprefix("call "))
            funcs.append(fun)
        elif command.startswith("wikipedia search "):
            fun = asyncio.to_thread(WikipediaSearch, command.removeprefix("wikipedia search "))
            funcs.append(fun)
        elif command.startswith("whatsapp"):
            # print("Calling WhatsApp")  # Debugging output
            fun = asyncio.to_thread(WhatsApp, command.removeprefix("whatsapp "))
            funcs.append(fun)
        elif command.startswith("reminder"):
            
            fun = asyncio.to_thread(Reminder, command.removeprefix("reminder "))
            funcs.append(fun)
            
        else:
            print(f"No function Found for {command}")
            
    results = await asyncio.gather(*funcs)
    
    for result in results:
        if isinstance (result, str):
            yield result
        else:
            yield result
            
async def Automation(commands: list[str]):
    async for result in TranslateAndExecute(commands):
        pass
    
    return True
        
if __name__ == "__main__":
    asyncio.run(Automation([
        "reminder 6:00 PM call mom"
    ]))