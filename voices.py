import pyttsx3

# Initialize the text-to-speech engine
engine = pyttsx3.init()

# Get available voices
voices = engine.getProperty('voices')

# Change the voice (0 for default male, 1 for female in most systems)
engine.setProperty('voice', voices[1].id)  # Change index based on available voices

# Speak a test sentence
engine.say("Hello, I am using a different voice now!")

# Run and close the engine
engine.runAndWait()