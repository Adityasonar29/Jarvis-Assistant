import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import eel
import pyttsx3
from asyncio import run
import speech_recognition as sr
import time
from kaushik_Adv_jar.backend.cohere_decision0 import FirstLayerDMM
from kaushik_Adv_jar.Frontend.GUI import MicButtonInitialed, MicButtonClosed
from kaushik_Adv_jar.backend.Text_To_Speech import TextToSpeech
from kaushik_Adv_jar.backend.speech_to_text import SpeechRecognition

@eel.expose
def speak(text):
    text = str(text)
    TextToSpeech(Text=text)
    eel.DisplayMassage(text)
    eel.receiverText(text)


@eel.expose
def takecommand():

    print('listening....')
    eel.DisplayMassage('listening....')
    MicButtonInitialed()

    try:
        query = SpeechRecognition()
        eel.DisplayMassage('recognizing....')
        print('recognizing')
        query = query.lower()
        eel.DisplayMassage(query)
        MicButtonClosed()
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
        Decision = FirstLayerDMM(query)
        print(" ")
        print(f"Decision: {Decision}")
        print(" ")
        
        # G = any([i for i in Decision if i.startswith("general")])
        # R = any([i for i in Decision if i.startswith("realtime")])
        
        # Mearged_query = " and ".join(
        #     [" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")]
        # )
        
        # for quries in Decision:
        #     if "generate " in quries:
        #         ImageGenerationQuery = str(quries)
        #         ImageExecution = True
                
        # for queries in Decision:
        #     if TaskExecution == False:
        #         if any(queries.startswith(func) for func in Function):
        #             run(Automation(list(Decision)))
        #             TaskExecution = True
        
        # if ImageExecution == True:
        #     with open("kaushik_Adv_jar/Frontend/Files/ImageGeneration.data", "w") as file:
        #         file.write(f"{ImageGenerationQuery},True")
                
        #     try:
        #         p1 = subprocess.Popen(['python', r'kaushik_Adv_jar\\BackEnd\\ImageGeneration.py'],
        #                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        #                             stdin=subprocess.PIPE, shell=False)
        #         subprocesses.append(p1)
                
        #     except Exception as e:
        #         print(f"[Error] In Starting Image generation.py:{e}")
        
        
            
                
        # if G and R or R:
        #     SetAssistantStatus("Searching....")
        #     Answer = RealtimeSearchEngine(QueryModifier(Mearged_query))
        #     ShowTextToScreen(f"{Assistantname} : {Answer}")
        #     SetAssistantStatus("Answering...")
        #     TextToSpeech(Answer)
        #     return True
        # else:
        #     for Queries in Decision:
        #         if "general" in Queries:
        #             SetAssistantStatus("Thinking....")
        #             QueryFinal = Queries.replace("general ", "")
        #             Answer = ChatBot(QueryModifier(QueryFinal))
        #             ShowTextToScreen(f"{Assistantname} : {Answer}")
        #             SetAssistantStatus("Answering...")
        #             TextToSpeech(Answer)
        #             return True
                
        #         elif "realtime" in Queries:
        #             SetAssistantStatus("Searching....")
        #             QueryFinal = Queries.replace("realtime ", "")
        #             Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
        #             ShowTextToScreen(f"{Assistantname} : {Answer}")
        #             SetAssistantStatus("Answering...")
        #             TextToSpeech(Answer)
        #             return True
            
                # elif "exit" in Queries:
                #     QueryFinal = "Okay, Bye!"
                #     Answer = ChatBot(QueryModifier(QueryFinal))
                #     ShowTextToScreen(f"{Assistantname} : {Answer}")
                #     SetAssistantStatus("Answering...")
                #     TextToSpeech(Answer)
                #     SetAssistantStatus("Answering...")
                #     os._exit(1) 
        
        # if "open" in query:
        #     from engine.features import openCommand
        #     openCommand(query)
        # elif "on youtube" in query:
        #     from engine.features import PlayYoutube
        #     PlayYoutube(query)
        
        # elif "send message" in query or "call" in query or "video call" in query:
        #     from engine.features import findContact, whatsApp, makeCall, sendMassage
        #     contact_no, name = findContact(query)
        #     if(contact_no != 0):
        #         speak("Which mode you want to use whatsapp or mobile")
        #         preferance = takecommand()
        #         print(preferance)

        #         if "mobile" in preferance:
        #             from engine.helper import check_device_lock_status_batch
        #             check_device_lock_status_batch()
        #             if "send message" in query or "send sms" in query: 
        #                 speak("what message to send")
        #                 massage = takecommand()
        #                 sendMassage(massage, contact_no, name)
        #             elif "call" in query:
        #                 makeCall(name, contact_no)
        #             else:
        #                 speak("please try again")
        #         elif "whatsapp" in preferance:
        #             massage = ""
        #             if "send message" in query:
        #                 massage = 'message'
        #                 speak("what message to send")
        #                 query = takecommand()
                                        
        #             elif "call" in query:
        #                 massage = 'call'
                        
        #             elif "video call" in query:
        #                 massage = 'video call'
                        
        #             else:
        #                 speak("plese say phone call")                
        #             whatsApp(contact_no, query, massage, name)
        # elif "send mail" in query:
        #     from engine.features import sendMail,findMail
        #     email_reciver, name =findMail(query)
        #     speak("what is the subject")
        #     subject = takecommand()
        #     speak("what is the message")
        #     message = takecommand()
        #     sendMail(email_reciver,subject=subject,body=message)
            
        # elif "photo" in query or "selfie" in query:
        #     from engine.features import openCam
        #     openCam(query)
            
        # elif "video" in query or "record" in query:
        #     from engine.features import openCamVideo
        #     openCamVideo(query)
            
        # elif "record the voice" in query or "voice recording" in query:
        #     from engine.features import voiceRecording
        #     voiceRecording()
            
        # else:
        #     from engine.features import chatBot
        #     chatBot(query)
    except Exception as e:
        error_massage  =f"An Error Occurred: {str(e)}"
        print(error_massage)
        eel.DisplayMassage(error_massage)
    eel.ShowHood()
