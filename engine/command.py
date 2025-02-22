import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import subprocess
from dotenv import dotenv_values
import speech_recognition as sr
from asyncio import run
import pyttsx3
import time
from kaushik_Adv_jar.backend.Text_To_Speech import TextToSpeech
import eel

from kaushik_Adv_jar.backend.Automation import Automation

from kaushik_Adv_jar.backend.REal_time_q_chatbot import RealtimeSearchEngine
from kaushik_Adv_jar.backend.speech_to_text import SpeechRecognition
from kaushik_Adv_jar.backend.chatbot_gorg import Assistantname, ChatBot
from kaushik_Adv_jar.backend.cohere_decision0 import FirstLayerDMM
from kaushik_Adv_jar.Frontend.GUI import MicButtonInitialed, MicButtonClosed, ShowTextToScreen
from kaushik_Adv_jar.backend.speech_to_text import QueryModifier, SetAssistantStatus

env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
DefaultMessage = f'''{Username} : Hello {Assistantname}, How are you?
{Assistantname} : Welcome {Username}, I am fine, How can I help you?'''
subprocesses = []
Function = ["open","close", "play", "system", "content", "google search", "youtube search", "reminder"]

@eel.expose
def speak(text):
    text = str(text)
    query = text
    TextToSpeech(Text=text)
    eel.DisplayMassage(query)
    eel.receiverText(query)


@eel.expose
def takecommand():

    print('listening...')
    eel.DisplayMassage('listening....')
    MicButtonInitialed()

    try:
        query = SpeechRecognition()
        eel.DisplayMassage('recognizing....')
        print('recognizing...')
        query = query.lower()
        eel.DisplayMassage(query)
        MicButtonClosed()
        print("Thinking...")
        time.sleep(2)
       
    except Exception as e:
        print(f"[Error] in speech recognition: {e}")
    
    return query


@eel.expose
def allCommands(massage=1):

    if massage == 1:
        query = takecommand()
        print(query)
        eel.senderText(query)

    else:
        query = massage
        eel.senderText(query)

    try:
        TaskExecution = False
        ImageExecution = False
        
        Decision = FirstLayerDMM(query)
        print(" ")
        print(f"Decision: {Decision}")
        print(" ")
        
        G = any([i for i in Decision if i.startswith("general")])
        R = any([i for i in Decision if i.startswith("realtime")])
        
        Mearged_query = " and ".join(
             [" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")]
         )
        
        for quries in Decision:
            if "generate " in quries:
                ImageGenerationQuery = str(quries)
                ImageExecution = True
                
        for queries in Decision:
            if TaskExecution == False:
                if any(queries.startswith(func) for func in Function):
                    run(Automation(list(Decision)))
                    TaskExecution = True
        
        if ImageExecution == True:
            with open("kaushik_Adv_jar/Frontend/Files/ImageGeneration.data", "w") as file:
                file.write(f"{ImageGenerationQuery},True")
                
            try:
                p1 = subprocess.Popen(['python', r'kaushik_Adv_jar\\BackEnd\\ImageGeneration.py'],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    stdin=subprocess.PIPE, shell=False)
                subprocess.append(p1)
                
            except Exception as e:
                print(f"[Error] In Starting Image generation.py:{e}")
        
        
            
                
        if G and R or R:
            SetAssistantStatus("Searching....")
            Answer = RealtimeSearchEngine(QueryModifier(Mearged_query))
            ShowTextToScreen(f"{Assistantname} : {Answer}")
            SetAssistantStatus("Answering...")
            TextToSpeech(Answer)
            return True
        else:
            for Queries in Decision:
                if "general" in Queries:
                    SetAssistantStatus("Thinking....")
                    QueryFinal = Queries.replace("general ", "")
                    Answer = ChatBot(QueryModifier(QueryFinal))
                    ShowTextToScreen(f"{Assistantname} : {Answer}")
                    SetAssistantStatus("Answering...")
                    TextToSpeech(Answer)
                    return True
                
                elif "realtime" in Queries:
                    SetAssistantStatus("Searching....")
                    QueryFinal = Queries.replace("realtime ", "")
                    Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
                    ShowTextToScreen(f"{Assistantname} : {Answer}")
                    SetAssistantStatus("Answering...")
                    TextToSpeech(Answer)
                    return True
            
                elif "exit" in Queries:
                    QueryFinal = "Okay, Bye!"
                    Answer = ChatBot(QueryModifier(QueryFinal))
                    ShowTextToScreen(f"{Assistantname} : {Answer}")
                    SetAssistantStatus("Answering...")
                    TextToSpeech(Answer)
                    SetAssistantStatus("Answering...")
                    os._exit(1) 
    except Exception as e:
        error_massage  =f"An Error Occurred: {str(e)}"
        print(error_massage)
        eel.DisplayMassage(error_massage)
    eel.ShowHood()
if __name__ == "__main__":
    while True:
        allCommands(input("Enter the command: "))