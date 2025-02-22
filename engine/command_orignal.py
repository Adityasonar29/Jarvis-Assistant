import pyttsx3
import speech_recognition as sr
import eel
import time

@eel.expose
def speak(text):
    text = str(text)
    engine = pyttsx3.init('sapi5')
    voices = engine.getProperty('voices') 
    engine.setProperty('voice', voices[0].id)
    engine.setProperty('rate', 174)
    eel.DisplayMassage(text)
    engine.say(text)
    eel.receiverText(text)
    engine.runAndWait()

@eel.expose
def takecommand():

    r = sr.Recognizer()

    with sr.Microphone() as source:
        print('listening....')
        eel.DisplayMassage('listening....')
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source)
        #add something for time out
        audio = r.listen(source, 10, 6)

    try:
        print('recognizing')
        eel.DisplayMassage('recognizing....')
        query = r.recognize_google(audio, language='en-in')
        print(f"user said: {query}")
        eel.DisplayMassage(query)
        time.sleep(2)
       
    except Exception as e:
        return ""
    
    return query.lower()

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

        if "open" in query:
            from engine.features import openCommand
            openCommand(query)
        elif "on youtube" in query:
            from engine.features import PlayYoutube
            PlayYoutube(query)
        
        elif "send message" in query or "call" in query or "video call" in query:
            from engine.features import findContact, whatsApp, makeCall, sendMassage
            contact_no, name = findContact(query)
            if(contact_no != 0):
                speak("Which mode you want to use whatsapp or mobile")
                preferance = takecommand()
                print(preferance)

                if "mobile" in preferance:
                    from engine.helper import check_device_lock_status_batch
                    check_device_lock_status_batch()
                    if "send message" in query or "send sms" in query: 
                        speak("what message to send")
                        massage = takecommand()
                        sendMassage(massage, contact_no, name)
                    elif "call" in query:
                        makeCall(name, contact_no)
                    else:
                        speak("please try again")
                elif "whatsapp" in preferance:
                    massage = ""
                    if "send message" in query:
                        massage = 'message'
                        speak("what message to send")
                        query = takecommand()
                                        
                    elif "call" in query:
                        massage = 'call'
                        
                    elif "video call" in query:
                        massage = 'video call'
                        
                    else:
                        speak("plese say phone call")                
                    whatsApp(contact_no, query, massage, name)
        elif "send mail" in query:
            from engine.features import sendMail,findMail
            email_reciver, name =findMail(query)
            speak("what is the subject")
            subject = takecommand()
            speak("what is the message")
            message = takecommand()
            sendMail(email_reciver,subject=subject,body=message)
            
        elif "photo" in query or "selfie" in query:
            from engine.features import openCam
            openCam(query)
            
        elif "video" in query or "record" in query:
            from engine.features import openCamVideo
            openCamVideo(query)
            
        elif "record the voice" in query or "voice recording" in query:
            from engine.features import voiceRecording
            voiceRecording()
            
        else:
            from engine.features import chatBot
            chatBot(query)
    except Exception as e:
        error_massage  =f"An Error Occurred: {str(e)}"
        print(error_massage)
        eel.DisplayMassage(error_massage)
    eel.ShowHood()