import random
from transformers import pipeline

# Initialize the emotion classification pipeline with a pre-trained model
emotion_classifier = pipeline("text-classification", model="bhadresh-savani/bert-base-uncased-emotion",device = -1)
# Define a dictionary mapping each emotion to a list of 10 responses
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
        "Your feelings are important—let's channel that energy constructively."
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
        "I'm sorry that you're feeling this way.",
        "I can sense your displeasure.",
        "It sounds like you're experiencing disgust—how can I help?",
        "I'm here to listen if something upset you.",
        "I understand that this situation is off-putting.",
        "Let's try to address what made you feel this way.",
        "I'm sorry if something has disturbed you.",
        "I appreciate your honesty—let's see what we can do about it.",
        "Your discomfort is important; let's work to resolve it."
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
    ]
}

def jarvis_emotion_handler(user_text):
    """
    Analyzes the user's text to detect their emotion and returns a Jarvis response
    tailored to that emotion. Jarvis is informed about the detected emotion and
    acts accordingly.
    """
    
    result = emotion_classifier(user_text)
    emotion = result[0]['label'].lower()
    
    jarvis_response = random.choice(emotion_responses.get(emotion, emotion_responses["neutral"]))

    full_response = f"(Detected emotion: {emotion.capitalize()}) (Response need to add in Answer: {jarvis_response})"
    

    return full_response

if __name__ == "__main__":
    user_input = "I'm so frustrated with everything right now!"
    emotional_text = jarvis_emotion_handler(user_input)
    print(emotional_text)