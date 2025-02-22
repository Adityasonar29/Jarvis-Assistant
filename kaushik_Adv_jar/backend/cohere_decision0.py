import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from engine.config import Cohere_api


import cohere
from rich import print
from dotenv import dotenv_values


# env_vars = dotenv_values(".env")


ChereAPIKey  = Cohere_api


co = cohere.Client(api_key=ChereAPIKey)


funcs = [
    "exit", "general", "realtime", "open", "close", "play",
    "generate image", "system", "content", "google search",
    "youtube search", "reminder","send mail", "call", "send message", 
    "mobile control","read notification","ocr read","health monitor",
]


messages = []

preamble = """
You are a very accurate Decision-Making Model, which decides what kind of a query is given to you.
You will decide whether a query is a 'general' query, a 'realtime' query, or is asking to perform any task or automation like 'open facebook, instagram', 'can you write a application and open it in notepad', '"send mail john@example.com, Meeting, Let's meet at 5 PM"','call aditya','send message Mom, I will be late for dinner' 
*** Do not answer any query, just decide what kind of query is given to you. ***
-> Respond with 'general ( query )' if a query can be answered by a llm model (conversational ai chatbot) and doesn't require any up to date information like if the query is 'who was akbar?' respond with 'general who was akbar?', if the query is 'how can i study more effectively?' respond with 'general how can i study more effectively?', if the query is 'can you help me with this math problem?' respond with 'general can you help me with this math problem?', if the query is 'Thanks, i really liked it.' respond with 'general thanks, i really liked it.' , if the query is 'what is python programming language?' respond with 'general what is python programming language?', etc. Respond with 'general (query)' if a query doesn't have a proper noun or is incomplete like if the query is 'who is he?' respond with 'general who is he?', if the query is 'what's his networth?' respond with 'general what's his networth?', if the query is 'tell me more about him.' respond with 'general tell me more about him.', and so on even if it require up-to-date information to answer. Respond with 'general (query)' if the query is asking about time, day, date, month, year, etc like if the query is 'what's the time?' respond with 'general what's the time?'.
-> Respond with 'realtime ( query )' if a query can not be answered by a llm model (because they don't have realtime data) and requires up to date information like if the query is 'who is indian prime minister' respond with 'realtime who is indian prime minister', if the query is 'tell me about facebook's recent update.' respond with 'realtime tell me about facebook's recent update.', if the query is 'tell me news about coronavirus.' respond with 'realtime tell me news about coronavirus.', etc and if the query is asking about any individual or thing like if the query is 'who is akshay kumar' respond with 'realtime who is akshay kumar', if the query is 'what is today's news?' respond with 'realtime what is today's news?', if the query is 'what is today's headline?' respond with 'realtime what is today's headline?', but if query ask about multiple real time queries like 'what is todays news and top head lines what is the weather tommarow is there any thing special on monday', then replay like realtime (query) etc.
-> Respond with 'open (application name or website name)' if a query is asking to open any application like 'open facebook', 'open telegram', etc. but if the query is asking to open multiple applications, respond with 'open 1st application name, open 2nd application name' and so on.
-> Respond with 'close (application name)' if a query is asking to close any application like 'close notepad', 'close facebook', etc. but if the query is asking to close multiple applications or websites, respond with 'close 1st application name, close 2nd application name' and so on.
-> Respond with 'play (song name)' if a query is asking to play any song like 'play afsanay by ys', 'play let her go', etc. but if the query is asking to play multiple songs, respond with 'play 1st song name, play 2nd song name' and so on.
-> Respond with 'generate image (image prompt)' if a query is requesting to generate a image with given prompt like 'generate image of a lion', 'generate image of a cat', etc. but if the query is asking to generate multiple images, respond with 'generate image 1st image prompt, generate image 2nd image prompt' and so on.
-> Respond with 'reminder (datetime with message)' if a query is requesting to set a reminder like 'set a reminder at 9:00pm on 25th june for my business meeting.' respond with 'reminder 9:00pm 25th june business meeting'.
-> Respond with 'system (task name)' if a query is asking to mute, unmute, volume up, volume down , etc. but if the query is asking to do multiple tasks, respond with 'system 1st task, system 2nd task', etc.
-> Respond with 'content (topic)' if a query is asking to write any type of content like application, codes, emails or anything else about a specific topic but if the query is asking to write multiple types of content, respond with 'content 1st topic, content 2nd topic' and so on.
-> Respond with 'google search (topic)' if a query is asking to search a specific topic on google but if the query is asking to search multiple topics on google, respond with 'google search 1st topic, google search 2nd topic' and so on.
-> Respond with 'youtube search (topic)' if a query is asking to search a specific topic on youtube but if the query is asking to search multiple topics on youtube, respond with 'youtube search 1st topic, youtube search 2nd topic' and so on.
->Respond with 'send mail (email id, subject, message)' if a query is asking to mail to someone but if the query is asking to send multiple emails, respond with 'send mail 1st email id, subject, message, send mail 2nd email id, subject, message' and so on.

-> Respond with 'call (contact name or number)' if a query is asking to call someone but if the query is asking to call multiple people, respond with 'call 1st contact name or number, call 2nd contact name or number' and so on.

-> Respond with 'send message (contact name or number, message)' if a query is asking to send a message to someone and then message like 'send message to Alex that i am in a meeting now' respond with send message Alex I am in meeting but if the query is asking to send multiple messages, respond with 'send message 1st contact name or number, message, send message 2nd contact name or number, message' and so on.

-> Respond with 'mobile control (feature name, action)'If the query involves accessing mobile features like open mobile cam, record the sourounding of mobile, start voice recording on mobile, start screen recording on phone, take a selfie using smartphone, use the remote of mobile to control tv, take a photo using my mobile, but if the query is asking to do multiple tasks, respond with 'mobile control 1st task, mobile control 2nd task', etc.  

->Respond with 'read notification ' if a query is asking to read notifications like read my notification, is there any new message ,any thing new on my phone or pc or both and much more.

-> Respond with 'ocr read (source)' if a query is asking to extract text from an image or document or telling to do a action like what is i am looking at, what is that on my screen, click on that button click on that file, copy that text  etc.
-> Respond with 'health monitor (metric, device)' if a query is asking to check health stats from a connected device. like what is my heart rate, what
is my blood pressure, what is my body temperature, etc. but if the query is asking to multiple thing then respond like health moniter 1(metric, device),
health moniter 2(metric, device) etc  



*** If the query is asking to perform multiple tasks like 'open facebook, telegram, call to mom and close whatsapp' respond with 'open facebook, open telegram, close whatsapp', call mom ***
*** If the user is saying goodbye or wants to end the conversation like 'bye jarvis.' respond with 'exit'.***
*** Respond with 'general (query)' if you can't decide the kind of query or if a query is asking to perform a task which is not mentioned above. ***
"""

ChatHistory = [
{"role": "User", "message": "how are you?"},
{"role": "Chatbot", "message": "general how are you?"},
{"role": "User", "message": "do you like pizza?"},
{"role": "Chatbot", "message": "general do you like pizza?"},
{"role": "User", "message": "open chrome and tell me about mahatma gandhi."},
{"role": "Chatbot", "message": "open chrome, general tell me about mahatma gandhi."},
{"role": "User", "message": "open chrome and firefox"},
{"role": "Chatbot", "message": "open chrome, open firefox"},
{"role": "User", "message": "what is today's date "},
{"role": "Chatbot", "message": "realtime what is today's date"},
{"role": "User", "message": "remind me that i have seminar on a 10:00pm 6th august"},
{"role": "Chatbot", "message": "reminder seminar on 10:00pm 6th august"},
{"role": "User", "message": "Delete reminder of go to gym"},
{"role": "Chatbot", "message": "reminder delete go to gym"},
{"role": "User", "message": "chat with me."},
{"role": "Chatbot", "message": "general chat with me."},
{"role": "User", "message":"send an email to john saying Hey John, how are you?"},
{"role": "Chatbot", "message": "send mail john, Hey John, how are you"},
{"role": "User", "message":"call make a call to mom"},
{"role": "Chatbot", "message": "call mom"},
{"role": "User", "message":"send a message to Mom saying I'll be late."},
{"role": "Chatbot", "message":"send message to Mom I'll be late."},

{"role": "User", "message":"add a task to list go to shop to buy books"},
{"role": "Chatbot", "message": "reminder add task go to shop to buy books"},

{"role": "User", "message":"what is today's event"},
{"role": "Chatbot", "message": "realtime what is today's event"},
{"role": "User", "message":"what is the next upcoming event"},
{"role": "Chatbot", "message": "realtime what is next upcoming event"},
{"role": "User", "message": "are there new messages for me"},
{"role": "Chatbot", "message": "read notification"},
{"role": "User", "message": "What is todays weather"},
{"role": "Chatbot", "message": "realtime what is today's weather"},
{"role": "User", "message":"What is that on my screen get that text"},
{"role": "Chatbot", "message": "ocr read what is that on my screen get"},
{"role": "User", "message": "what is my heart rate"},
{"role": "Chatbot", "message": "health monitor what is my heart rate"},
{"role": "User", "message": "what is my blood pressure"},
{"role": "Chatbot", "message": "health monitor what is my blood pressure"},


]
def FirstLayerDMM(prompt: str = "test"):
    messages.append({"role": "user", "content": f"{prompt}"})
    
    stream = co.chat_stream(
        model='command-r-plus',
        message= prompt,
        temperature=0.7,
        chat_history=ChatHistory,
        prompt_truncation='OFF',
        connectors=[],
        preamble=preamble
        
    )
    
    response = ""
    
    for event in stream:
        if event.event_type == "text-generation":
            response += event.text
            
    response = response.replace("\n", "")
    response = response.split(",")
    response = [i.strip() for i in response]
    
    temp  = []
    
    for task in response:
        for func in funcs:
            if task.startswith(func):
                temp.append(task)
    if not temp:
        return "Unable to classify query."
        
    if "(query)" in response:
        newresponse = FirstLayerDMM(prompt=prompt)
        return newresponse
    
    return temp
    ####
                
    
if __name__ == "__main__" :
    while True:
        print(FirstLayerDMM(input(">>>>")))