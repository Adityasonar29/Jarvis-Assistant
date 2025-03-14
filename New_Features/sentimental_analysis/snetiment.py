import random
from transformers import pipeline
import pyttsx3

# Initialize the emotion classification pipeline with a pre-trained model
emotion_classifier = pipeline("text-classification", 
                            model="bhadresh-savani/bert-base-uncased-emotion",
                            device=-1)

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Initialize global variables
conversation_history = []  # Default emotional state

# Define emotion responses dictionary
emotion_responses = {
    "joy": [
        "I'm thrilled you're feeling joyful!",
        "It's great to hear that you're happy!",
        "Your positivity is contagious!",
        "That's wonderful news—keep up the great mood!",
        "Happiness is a beautiful thing; enjoy it!",
        "I'm delighted you're in such high spirits!",
        "Your joyful energy really shines through!",
        "Keep smiling—your joy is inspiring!",
        "It's fantastic to see you so upbeat!",
        "Your happiness lights up the conversation!"
    ],
    "sadness": [
        "I'm sorry to hear you're feeling down.",
        "It sounds like you're a bit low—I'm here for you.",
        "I understand that sadness can be heavy; let me know if I can help.",
        "I'm here to listen if you'd like to talk.",
        "It's okay to feel sad sometimes; I'm with you.",
        "I care about your feelings—let's see how we can improve things.",
        "I know it's tough right now; you're not alone.",
        "I'm here to support you through these moments.",
        "Your feelings matter; I hope things get better soon.",
        "I appreciate you sharing your sadness—let's work through it together."
    ],
    "anger": [
        "It sounds like you're really upset right now.",
        "I'm sorry you're feeling angry.",
        "I understand your frustration—let's try to find a solution.",
        "Take a deep breath; I'm here to help.",
        "Your anger is valid—let's work through it together.",
        "I can sense your irritation; let's calm down and think this through.",
        "I appreciate your passion, even if it comes out as anger.",
        "Let's take a moment to relax and then address the issue.",
        "I understand that this is upsetting; how can I assist?",
        "Your feelings are important—let's channel that energy constructively.",
        "I hear your anger—let's find a way forward together."
    ],
    "fear": [
        "I sense that you're feeling anxious.",
        "It's understandable to feel scared sometimes.",
        "I'm here to support you through your fear.",
        "Take a deep breath—we'll face this together.",
        "I know this situation might be intimidating; you're not alone.",
        "Your fear is completely valid—let's work on easing it.",
        "Let's take a moment to find some calm.",
        "I understand that this can be frightening; I'm here for you.",
        "Remember, courage is about facing fear—even a little bit at a time.",
        "I'm here to help you navigate through this uncertainty."
    ],
    "surprise": [
        "That sounds unexpected!",
        "I'm intrigued by what just happened.",
        "Wow, that must have been quite a shock!",
        "It seems like you're surprised; care to share more?",
        "I'm curious—what caught you off guard?",
        "Surprises can be exciting; tell me more about it.",
        "I can sense your astonishment; what's the story?",
        "Unexpected events make life interesting!",
        "That's quite a twist—I'm all ears.",
        "It sounds like something remarkable just occurred!"
    ],
    "disgust": [
        "It seems something is really bothering you.",
        "I understand that this situation is off-putting.",
        "I can sense your displeasure.",
        "It sounds like you're experiencing disgust—how can I help?",
        "I'm here to listen if something upset you.",
        "Let's try to address what made you feel this way.",
        "I'm sorry if something has disturbed you.",
        "I appreciate your honesty—let's see what we can do about it.",
        "Your discomfort is important; let's work to resolve it.",
        "I understand this is unpleasant—let's find a solution."
    ],
    "neutral": [
        "Thank you for sharing your thoughts.",
        "I'm here whenever you're ready to talk more.",
        "I appreciate your input.",
        "Let me know how I can assist you further.",
        "Thanks for keeping me updated.",
        "I'm here to help with whatever you need.",
        "I value your perspective.",
        "Feel free to share more details if you'd like.",
        "Let's work together on your request.",
        "How can I be of service today?"
    ],
    "annoyed": [
        "Ugh… do I have to? 😒",
        "Can we not do this right now? 😑",
        "Fine… but I won't enjoy it. 🙄"
    ],
    "sympathetic": [
        "I understand... It's okay to feel down sometimes. 😔",
        "I'm here if you need me. Just say the word.",
        "I wish I could give you a hug."
    ],
    "supportive": [
        "I'm here to support you through this.",
        "Let's work together to overcome this challenge.",
        "You can count on me for help."
    ],
    "polite": [
        "Thank you for your patience.",
        "I appreciate your understanding.",
        "Let's proceed with respect and courtesy."
    ]
}

## not for suppriesing and for disgust not giveing the neutral

def detect_user_emotion(text):
    """
    Detects the emotion in the user's text using the emotion classifier.
    Returns the detected emotion as a lowercase string.
    """
    result = emotion_classifier(text)
    return result[0]['label'].lower()

def update_jarvis_emotion(user_emotion):
    """
    Updates Jarvis's emotional state based on the user's emotion.
    """
    global jarvis_emotion
    
    emotion_mapping = {
        "joy": "joy",
        "anger": "annoyed",
        "sadness": "sympathetic",
        "fear": "supportive",
        "neutral": "neutral",
        "excited": "excited",
        "surprise": "surprised"
    }
    
    jarvis_emotion = emotion_mapping.get(user_emotion, "neutral")
    return jarvis_emotion

def analyze_conversation(user_message):
    """
    Analyzes the conversation context and history to determine appropriate emotional response.
    """
    global conversation_history

    # Default emotional state
    detected_emotion = "neutral"

    # Check for repeated questions
    if conversation_history.count(user_message) > 2:
        detected_emotion = "annoyed"
    # Check for complex sentences
    elif len(user_message.split()) > 20:
        detected_emotion = "surprised"
    # Check for praise
    elif any(word in user_message.lower() for word in ["good job", "amazing", "well done", "smart"]):
        detected_emotion = "happy"
    # Check for negative feedback
    elif any(word in user_message.lower() for word in ["stupid", "useless", "idiot"]):
        detected_emotion = "sad"

    # Update conversation history
    conversation_history.append(user_message)
    if len(conversation_history) > 10:
        conversation_history.pop(0)

    return detected_emotion

def speak(text, emotion="neutral"):
    """
    Speaks the given text with emotion-appropriate voice modulation.
    """
    # Define emotion-based voice properties
    voice_properties = {
        "happy": {"rate": 250},
        "sad": {"rate": 150},
        "angry": {"rate": 220},
        "excited": {"rate": 270},
        "neutral": {"rate": 200}
    }
    
    # Get voice properties for the emotion
    properties = voice_properties.get(emotion, voice_properties["neutral"])
    
    # Apply voice properties
    engine.setProperty('rate', properties["rate"])
    
    # Speak the text
    engine.say(text)
    engine.runAndWait()

def process_user_emotion(user_message):
    """
    Main function to process user input and generate appropriate response.
    Returns a tuple of (response_text, emotion)
    """
    # Detect user's emotion
    user_emotion = detect_user_emotion(user_message)
    # print("user_emotion = " + user_emotion)
    
    # Update Jarvis's emotional state
    current_emotion = update_jarvis_emotion(user_emotion)
    # print("jarvis_emotion = " + current_emotion)
    
    # Analyze conversation context
    context_emotion = analyze_conversation(user_message)
    # print("context_emotion = " + context_emotion)
    
    # Get appropriate response
    response = random.choice(emotion_responses.get(current_emotion, emotion_responses["neutral"]))

    # print("response = " + response)
    
    # Format full response with emotional context
    full_response = f"[SYSTEM] Emotional Context:\nUser Emotion: {user_emotion}\nAI Emotion: {current_emotion}\nContext: {context_emotion}\nSuggested Response: {response}"
    
    return full_response

def main():
    """
    Main function for testing the sentiment analysis system with a single prompt.
    """
    # Choose one example prompt for testing (e.g., for 'joy')
    test_input = "what to do i my wallet is stolen"
    # Process the user input to get a response and the detected emotion
    response = process_user_emotion(test_input)
    
    print(f"User input: {test_input}")
    print(f"Response: {response}")
    
    # Speak the response with an emotional tone (assuming speak() modulates tone based on detected_emotion)
    speak(response)

if __name__ == "__main__":
    main()