import sys
import os
import json
import re
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from groq import Groq
from json import load, dump
from datetime import datetime
from functools import wraps

from dotenv import dotenv_values

from New_Features.sentimental_analysis.snetiment import process_user_emotion

# Add a run_once decorator function
def run_once(func):
    """
    A decorator that ensures a function is executed only once.
    
    Usage:
    @run_once
    def my_function():
        # This code will run only once
        print("This will only print once")
    """
    has_run = False
    result = None
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        nonlocal has_run, result
        if not has_run:
            result = func(*args, **kwargs)
            has_run = True
            return result
        else:
            return result
    
    return wrapper

# Global variable to store the session's chat file path
SESSION_CHAT_FILE = None
SESSION_CHAT_TITLE = None

# Function to initialize the session chat file (runs only once per session)
@run_once
def initialize_session_chat_file(first_message):
    """
    Creates a new chat file for the current session.
    This function will run only once per session.
    """
    global SESSION_CHAT_FILE, SESSION_CHAT_TITLE
    print("Creating new conversation file...")
    SESSION_CHAT_FILE, SESSION_CHAT_TITLE = create_chat_log(first_message, "Data\\Chat_history")
    print(f"New chat created: {SESSION_CHAT_TITLE}")
    print(f"Chat file: {SESSION_CHAT_FILE}")
    return SESSION_CHAT_FILE

env_vars = dotenv_values(".env")
# chat_histor_page_dir =  
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

Client = Groq(api_key=GroqAPIKey)

messages = []

System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Rely strictly on the provided data to answer the query, but adjust your tone appropriately based on the detected emotion. ***
*** Provide concise, professional answers without unnecessary elaboration. ***
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
    current_date_time = datetime.now()
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

def ChatBot(query, chat_file=None):
    """
    Main chatbot function that processes user queries and returns responses.
    
    Parameters:
    - query: The user's input message
    - chat_file: Optional path to a specific chat log file. If provided, uses that file instead of the session file.
    """
    global SESSION_CHAT_FILE
    
    try:
        # Initialize the session chat file if it hasn't been done yet
        if SESSION_CHAT_FILE is None:
            initialize_session_chat_file(query)
        
        # Always use the session chat file unless a specific file is provided
        chat_history_path = chat_file if chat_file else SESSION_CHAT_FILE
            
        # Load existing messages from the file
        try:
            with open(chat_history_path, "r") as f:
                messages = load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # If file doesn't exist or is empty/invalid, start with empty history
            messages = []
            
        messages.append({"role": "user","content": f"{query}"})
        
        completion = Client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + [{"role": "system","content":RealtimeInformation()}] + messages + [{"role": "system","content":process_user_emotion(query)}],
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
        Answer = AnswerModifier(Answer)
        
        messages.append({"role": "assistant","content": f"{Answer}"})
        
        # Save the updated conversation history
        with open(chat_history_path, "w") as f:
            dump(messages, f, indent=4)
            
        return Answer
    
    except Exception as e:
        print(f"Error in ChatBot: {e}")
        return f"I apologize, but I encountered an error: {str(e)}"

# Function to start a new conversation
def start_new_conversation(first_message, log_dir="Data\\Chat_history"):
    """
    Starts a new conversation by creating a new chat log file and processing the first message.
    
    Returns:
    - chat_file: Path to the new chat log file
    - chat_title: Title of the chat
    - response: The assistant's response to the first message
    """
    # Create a new chat log file
    chat_file, chat_title = create_chat_log(first_message, log_dir)
    
    # Process the first message directly without recursion
    try:
        with open(chat_file, "r") as f:
            messages = load(f)
            
        completion = Client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + [{"role": "system","content":RealtimeInformation()}] + messages + [{"role": "system","content":process_user_emotion(first_message)}],
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )
        
        response = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                response += chunk.choices[0].delta.content
                
        response = response.replace("</s>", "")
        response = AnswerModifier(response)
        
        # Update the chat log with the assistant's response
        append_to_chat_log(chat_file, response, role="assistant")
    except Exception as e:
        response = f"Error starting conversation: {str(e)}"
    
    return chat_file, chat_title, response

# Function to continue an existing conversation
def continue_conversation(chat_file, message):
    """
    Continues an existing conversation by processing a new message.
    
    Returns:
    - response: The assistant's response to the message
    """
    # Process the message
    response = ChatBot(message, chat_file)
    
    # Update the chat log with both messages
    append_to_chat_log(chat_file, message, role="user")
    append_to_chat_log(chat_file, response, role="assistant")
    
    return response

# Function to list all available chat logs
def list_chat_logs(log_dir="Data\\Chat_history"):
    """
    Lists all available chat logs in the specified directory.
    
    Returns:
    - A list of tuples containing (file_path, chat_title, timestamp)
    """
    if not os.path.exists(log_dir):
        return []
        
    chat_logs = []
    for file in os.listdir(log_dir):
        if file.endswith(".json") and file.startswith("chat_"):
            file_path = os.path.join(log_dir, file)
            
            # Extract title and timestamp from filename
            match = re.match(r"chat_(.+)_(\d{8}_\d{6})\.json", file)
            if match:
                title = match.group(1).replace("_", " ")
                timestamp = match.group(2)
                
                chat_logs.append((file_path, title, timestamp))
                
    # Sort by timestamp (newest first)
    chat_logs.sort(key=lambda x: x[2], reverse=True)
    return chat_logs

def create_chat_log(first_input, log_dir="Data\\Chat_history"):
    """
    Creates a new chat log file with a meaningful title based on the first message.
    Returns the filepath and title.
    """
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    title = generate_chat_title(first_input)

    filename = f"chat_{title}_{timestamp}.json"
    filepath = os.path.join(log_dir, filename)

    # Initialize with the first message in the format expected by ChatBot
    # initial_data = [
    #     {
    #         "role": "user",
    #         "content": first_input
    #     }
    # ]
    
    # with open(filepath, "w", encoding="utf-8") as f:
    #     json.dump(initial_data, f, indent=2)

    return filepath, title


def append_to_chat_log(filepath, message, role="user"):
    """
    Appends a message to an existing chat log file.
    """
    # Read the current conversation history
    with open(filepath, "r", encoding="utf-8") as f:
        history = json.load(f)
    
    # Append the new message in the format expected by ChatBot
    history.append({
        "role": role,
        "content": message
    })
    
    # Write the updated conversation back to the file
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

def generate_chat_title(text, max_length=80):
    """
    Generates a concise, meaningful title for a chat based on the first message.
    Uses a direct call to the LLM to create a natural title.
    """
    try:
        # Create a direct call to the LLM to avoid recursion with ChatBot function
        # Prompt the LLM to generate a concise, meaningful title
        prompt = f"Generate a very short title (3-5 words max) for a conversation that starts with this message: '{text}'. Just return the title, nothing else."
        
        # Create a temporary message list for this specific request
        temp_messages = [
            {"role": "system", "content": "You are a helpful assistant that generates short, concise titles."},
            {"role": "user", "content": prompt}
        ]
        
        # Direct call to the LLM
        try:
            completion = Client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=temp_messages,
                max_tokens=200,
                temperature=0.3,  # Lower temperature for more focused responses
                top_p=1,
                stream=False,  # No streaming for this simple request
                stop=None
            )
            
            # Extract the title from the response
            title = completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error in direct LLM call: {e}")
            # Fall back to simple approach if LLM call fails
            # return simple_title_fallback(text)
        
        # Clean up the response
        title = title.strip().strip('"\'').replace('\n', ' ')
        
        # If the title is too long, truncate it
        if len(title) > max_length:
            title = title[:max_length]
            
        return sanitize_filename(title)
    except Exception as e:
        print(f"Error generating title: {e}")
        # Fall back to simple approach
        # return simple_title_fallback(text, max_length)

def sanitize_filename(text, max_length=80):
    """
    Sanitizes a string to be used as a filename by replacing non-alphanumeric characters.
    """
    text = re.sub(r'\W+', '_', text)  # Replace non-alphanumeric characters
    return text[:max_length].strip("_")


# def simple_title_fallback(text, max_length=30):
#     """
#     A simple fallback for title generation when the main method fails.
#     Just extracts the first few meaningful words.
#     """
#     # Remove common question starters
#     cleaned_text = re.sub(r'^(can you |what |how |why |tell me |explain )', '', text.lower())
    
#     # Get the first few words (up to 5)
#     words = cleaned_text.split()[:5]
#     title = '_'.join(words)
    
#     return sanitize_filename(title, max_length)

# Example of using the run_once decorator
@run_once
def initialize_application():
    """
    This function will only run once no matter how many times it's called.
    Use this for one-time initialization tasks like:
    - Setting up database connections
    - Loading large models into memory
    - Initializing configuration
    - Creating necessary directories
    """
    print("Initializing application...")
    # Example: Create necessary directories if they don't exist
    if not os.path.exists("Data\\Chat_history"):
        os.makedirs("Data\\Chat_history")
    if not os.path.exists("Data"):
        os.makedirs("Data")
    print("Application initialized successfully!")
    return True

if __name__ == "__main__" :
    # Initialize the application once
    initialize_application()
    
    # Reset session variables to ensure a fresh start
    SESSION_CHAT_FILE = None
    SESSION_CHAT_TITLE = None
    
    while True:
        user_input = input("Enter Your Question : ")
        if user_input.lower() == "exit":
            break
        print(ChatBot(user_input))