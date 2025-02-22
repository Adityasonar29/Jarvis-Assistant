import sys
import os
import re
from rich import print
from dotenv import dotenv_values

# Adjust your import if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from engine.config import Cohere_api
import cohere

# Use your API key
ChereAPIKey = Cohere_api
co = cohere.Client(api_key=ChereAPIKey)

# List of allowed functions/commands.
funcs = [
    "exit", "general", "realtime", "open", "close", "play",
    "generate image", "system", "content", "google search",
    "youtube search", "reminder", "send mail", "call", "send message", 
    "mobile control", "todo", "read notification", "ocr read", "health monitor",
]

# Updated preamble instructing plain text, comma-separated output.
preamble = """
You are a decision-making model. Decide what type of query is being requested.
For each query, output a comma-separated list of commands. Each command should start with one of the following keywords:
exit, general, realtime, open, close, play, generate image, system, content, google search, youtube search, reminder, send mail, call, send message, mobile control, todo, read notification, ocr read, health monitor.
Follow these examples exactly and output only the commands with no additional text.
Example:
For the input "open chrome and tell me about mahatma gandhi.", output:
open chrome, general tell me about mahatma gandhi
"""

# Updated chat history using plain text examples.
ChatHistory = [
    {"role": "User", "message": "how are you?"},
    {"role": "Chatbot", "message": "general how are you?"},
    {"role": "User", "message": "do you like pizza?"},
    {"role": "Chatbot", "message": "general do you like pizza?"},
    {"role": "User", "message": "open chrome and tell me about mahatma gandhi."},
    {"role": "Chatbot", "message": "open chrome, general tell me about mahatma gandhi"},
    {"role": "User", "message": "open chrome and firefox"},
    {"role": "Chatbot", "message": "open chrome, open firefox"},
    {"role": "User", "message": "what is today's date"},
    {"role": "Chatbot", "message": "realtime what is today's date"},
    {"role": "User", "message": "remind me that I have a seminar at 10:00pm on 6th August"},
    {"role": "Chatbot", "message": "reminder 10:00pm 6th August seminar"},
    {"role": "User", "message": "chat with me."},
    {"role": "Chatbot", "message": "general chat with me."},
    {"role": "User", "message": "send an email to john saying Hey John, how are you?"},
    {"role": "Chatbot", "message": "send mail john, Hey John, how are you"},
    {"role": "User", "message": "call mom"},
    {"role": "Chatbot", "message": "call mom"},
    {"role": "User", "message": "send a message to Mom saying I'll be late."},
    {"role": "Chatbot", "message": "send message Mom, I'll be late"},
    {"role": "User", "message": "add a task to list go to shop to buy books"},
    {"role": "Chatbot", "message": "todo add task go to shop to buy books"},
    {"role": "User", "message": "what is today's event"},
    {"role": "Chatbot", "message": "realtime what is today's event"},
    {"role": "User", "message": "what is the next upcoming event"},
    {"role": "Chatbot", "message": "realtime what is next upcoming event"},
    {"role": "User", "message": "are there new messages for me"},
    {"role": "Chatbot", "message": "read notification are there new messages for me"},
    {"role": "User", "message": "What is today's weather"},
    {"role": "Chatbot", "message": "realtime what is today's weather"},
    {"role": "User", "message": "What is that on my screen get that text"},
    {"role": "Chatbot", "message": "ocr read what is that on my screen get that text"},
    {"role": "User", "message": "what is my heart rate"},
    {"role": "Chatbot", "message": "health monitor what is my heart rate"},
    {"role": "User", "message": "what is my blood pressure"},
    {"role": "Chatbot", "message": "health monitor what is my blood pressure"},
]

def parse_response(response_text):
    """
    Parses the plain text response by splitting on commas and matching against allowed functions.
    """
    # Remove newlines and extra whitespace.
    response_text = response_text.replace("\n", " ").strip()
    # Split on commas.
    commands_raw = [item.strip() for item in response_text.split(",")]
    
    commands = []
    for cmd in commands_raw:
        # Check case-insensitively if the command starts with one of the allowed keywords.
        for func in funcs:
            if cmd.lower().startswith(func):
                commands.append(cmd)
                break
    return commands

def FirstLayerDMM(prompt: str = "test"):
    # Append the user's prompt to the chat history.
    ChatHistory.append({"role": "User", "message": prompt})
    
    # Call the Cohere API with the complete conversation context.
    stream = co.chat_stream(
        model='command-r-plus',
        message=prompt,
        temperature=0.7,
        chat_history=ChatHistory,
        prompt_truncation='AUTO',
        connectors=[],
        preamble=preamble
    )
    
    response_text = ""
    for event in stream:
        if event.event_type == "text-generation":
            response_text += event.text
    response_text = response_text.strip()
    
    # Parse the plain text output to extract commands.
    commands = parse_response(response_text)
    
    # Debug: Show raw and parsed responses.
    # print(f"[bold blue]Raw response:[/bold blue] {response_text[0]}")
    # print(f"[bold green]Parsed commands:[/bold green] {commands[0]}")
    
    # Append the chatbot's response to the chat history.
    ChatHistory.append({"role": "Chatbot", "message": response_text})
    
    if not commands:
        return "Unable to classify query."
    
    # If any command remains ambiguous (contains "(query)"), you could re-prompt here.
    if any("(query)" in cmd for cmd in commands):
        return "Ambiguous command received, please rephrase."
    
    return commands

if __name__ == "__main__":
    while True:
        user_input = input(">>>> ")
        result = FirstLayerDMM(prompt=user_input)
        print(result)
