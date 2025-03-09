# # Function to start a new conversation
# def start_new_conversation(first_message, log_dir="Data\\Chat_history"):
#     """
#     Starts a new conversation by creating a new chat log file and processing the first message.
    
#     Returns:
#     - chat_file: Path to the new chat log file
#     - chat_title: Title of the chat
#     - response: The assistant's response to the first message
#     """
#     # Create a new chat log file
#     chat_file, chat_title = create_chat_log(first_message, log_dir)
    
#     # Process the first message directly without recursion
#     try:
#         with open(chat_file, "r") as f:
#             messages = load(f)
            
#         completion = Client.chat.completions.create(
#             model="llama3-70b-8192",
#             messages=SystemChatBot + [{"role": "system","content":RealtimeInformation()}] + messages + [{"role": "system","content":process_user_emotion(first_message)}],
#             max_tokens=1024,
#             temperature=0.7,
#             top_p=1,
#             stream=True,
#             stop=None
#         )
        
#         response = ""
#         for chunk in completion:
#             if chunk.choices[0].delta.content:
#                 response += chunk.choices[0].delta.content
                
#         response = response.replace("</s>", "")
#         response = AnswerModifier(response)
        
#         # Update the chat log with the assistant's response
#         append_to_chat_log(chat_file, response, role="assistant")
#     except Exception as e:
#         response = f"Error starting conversation: {str(e)}"
    
#     return chat_file, chat_title, response

# Function to continue an existing conversation
# def continue_conversation(chat_file, message):
#     """
#     Continues an existing conversation by processing a new message.
    
#     Returns:
#     - response: The assistant's response to the message
#     """
#     # Process the message
#     response = ChatBot(message, chat_file)
    
#     # Update the chat log with both messages
#     append_to_chat_log(chat_file, message, role="user")
#     append_to_chat_log(chat_file, response, role="assistant")
    
#     return response

# Function to list all available chat logs
import datetime
import json
import os
import re

from kaushik_Adv_jar.backend.chatbot_gorg_copy import Client


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
                model="llama3-70b-8192",
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