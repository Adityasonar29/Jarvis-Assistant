# Jarvis - Your Personal AI Assistant

Jarvis is a modern, web-based AI assistant that combines voice interaction, sentiment analysis, and text-based communication with a beautiful UI inspired by Siri's wave animation.

## Features

### 1. Multiple Interaction Methods
- **Voice Commands**: Activate with the microphone button
- **Keyboard Shortcut**: Quick activation using `Ctrl + J` (Windows) or `Command + J` (Mac)
- **Text Input**: Type your commands in the chatbox

### 2. Smart Interactions
- **Sentiment Analysis**: Understands your emotional state and responds appropriately
- **Dynamic UI**: Beautiful Siri-like wave animation during active listening
- **Sound Feedback**: Audio cues when the assistant is activated

### 3. UI Elements
- **Animated Text**: Smooth text animations using textillate.js
- **Wave Visualization**: iOS-style wave animation during voice interaction
- **Adaptive Interface**: Dynamic button visibility based on input state

## Setup

1. **Create Virtual Environment**
```bash
python -m venv venv
```

2. **Activate Virtual Environment**
- Windows (PowerShell):
```powershell
.\venv\Scripts\Activate.ps1
```
- Mac/Linux:
```bash
source venv/bin/activate
```

3. **Install Dependencies**
```bash
pip install transformers torch eel
```

## Usage

### Starting the Application
1. Activate your virtual environment
2. Run the main application file
3. The web interface will automatically open in your default browser

### Ways to Interact

1. **Voice Commands**
   - Click the microphone button
   - Wait for the wave animation to start
   - Speak your command

2. **Keyboard Shortcut**
   - Press `Ctrl + J` (Windows) or `Command + J` (Mac)
   - The wave animation will appear
   - Speak your command

3. **Text Input**
   - Type in the chatbox
   - Press Enter or click the Send button
   - The assistant will process your text input

### Closing the Assistant
- Click the close button to hide the wave animation
- The assistant remains ready for your next command

## Technical Details

### Key Components
- **Frontend**: HTML, CSS, JavaScript with jQuery
- **Backend**: Python with Eel framework
- **AI Features**: 
  - Sentiment analysis using BERT model
  - Emotion detection and appropriate response generation

### Libraries Used
- `transformers`: For sentiment analysis
- `eel`: For Python-JavaScript integration
- `textillate.js`: For text animations
- `SiriWave`: For iOS-style wave animation

## Troubleshooting

If the keyboard shortcut doesn't work:
1. Make sure you're using the correct key combination for your OS
2. Check if any other application is using the same shortcut
3. Try clicking anywhere on the window first to ensure it has focus

## Contributing

Feel free to submit issues and enhancement requests! 