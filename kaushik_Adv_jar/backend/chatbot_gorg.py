import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from groq import Groq
from json import load, dump
import datetime 
from dotenv import dotenv_values

from New_Features.sentimental_analysis.snetiment import jarvis_emotion_handler

env_vars = dotenv_values(".env")

Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

Client = Groq(api_key=GroqAPIKey)

messages = []

System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

SystemChatBot  = [
    {"role":"system", "content":System} 
]

try:
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)
except FileNotFoundError:
    with open(r"Data\ChatLog.json", "w") as f:
        dump([], f)
        
def RealtimeInformation():
    current_date_time = datetime.datetime.now()
    day  = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month =  current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    seconds = current_date_time.strftime("%S")
    
    
    data = f"Please use this real information if needed, \n"
    data += f"Day: {day}\nDate: {date}\nMonth: {month}\nYear: {year}\n"
    data += f"Time: {hour} hours :{minute} minutes :{seconds} seconds.\n"
    return data

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modfied_answer = '\n'.join(non_empty_lines)
    return modfied_answer

def ChatBot(query):

    try:
        with open(r"Data\ChatLog.json", "r") as f:
            messages = load(f)
            
        messages.append({"role": "user","content": f"{query}"})
        
        completion = Client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot+[{"role": "system","content":RealtimeInformation()}] + messages + [{"role": "system","content":jarvis_emotion_handler(query)}],
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )
        
        Answer = ""
        
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content
                
        Answer = Answer.replace("</s>", "")
        
        messages.append({"role": "assistant", "content": Answer})
        
        with open(r"Data\ChatLog.json", "w") as f:
            dump(messages, f, indent=4)
            
        return AnswerModifier(Answer=Answer)
    
    except Exception as e:
        print(f"Error: {e}")
        with open(r"Data\ChatLog.json", "w") as f:
            dump([], f, indent=4)
        return ChatBot(query)
    
if __name__ == "__main__" :
    while True:
        user_input = input("Enter Your Question :")
        print(ChatBot(user_input))