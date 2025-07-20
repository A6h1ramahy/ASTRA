import sounddevice as sd 
import numpy as np
from plyer import notification
from pydub import AudioSegment
import threading
import time
import datetime
import speech_recognition as sr
import pyttsx3
import requests 
import pywhatkit
import wikipedia
import pyautogui
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("API_KEY")

# Initialize DeepSeek API
DEEPSEEK_API_KEY = api_key
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"  

# Initialize text-to-speech engine
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

# Function to speak text
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to listen to user input
def listen():
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
        print("Recognizing...")
        query = recognizer.recognize_google(audio, language="en-US")
        print(f"\n{query}")
        return query.lower()
    except sr.UnknownValueError:
        print("Sorry, I didn't catch that.\n\n")
        return ""
    except sr.RequestError as e:
        speak("Speech recognition service is not available.")
        return ""
    except Exception as e:
        print("An unexpected error occurred while listening.")
        return ""

# Function to get AI response using DeepSeek API
def get_ai_response(prompt):
    if not DEEPSEEK_API_KEY:
        return "Error: DeepSeek API key is missing."
    
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=10)
        response.raise_for_status()  # Raises an error for HTTP errors

        data = response.json()
        return data.get('choices', [{}])[0].get('message', {}).get('content', "Error: No valid response.")
    
    except requests.exceptions.Timeout:
        return "Error: DeepSeek API request timed out."
    except requests.exceptions.RequestException as e:
        return f"Error: Unable to connect to DeepSeek API. {e}"

# Function to handle commands
def handle_command(query):
    if "open" in query and "website" in query:
        website = query.replace("open website", "").strip()
        speak(f"Opening {website}")
        pywhatkit.search(website)
    elif "open file" in query:
        file_path = query.replace("open file", "").strip()
        try:
            os.startfile(file_path)
            speak(f"Opening {file_path}")
        except FileNotFoundError:
            speak(f"Sorry, I couldn't find the file at {file_path}")
        except Exception as e:
            speak(f"An error occurred while trying to open the file: {e}")
    elif "alarm" in query and "set" in query.lower():
        alarm_time = query.replace("set alarm for", "").strip()
        try:
            datetime.datetime.strptime(alarm_time, "%H:%M")
            speak(f"Alarm set for {alarm_time}")
            set_alarm(alarm_time)
        except ValueError:
            speak("Please provide the alarm time in the correct format (HH:MM).")
    elif "cancel alarm" in query:
        cancel_alarm()
    elif "wikipedia" in query:
        search_query = query.replace("wikipedia", "").strip()
        try:
            info = wikipedia.summary(search_query, sentences=2)
            speak(f"According to Wikipedia: {info}")
        except wikipedia.exceptions.DisambiguationError as e:
            speak(f"Multiple results found. Please be more specific.")
        except wikipedia.exceptions.PageError:
            speak(f"Sorry, I couldn't find any information on {search_query}.")
        except Exception as e:
            speak("An unexpected error occurred while searching Wikipedia.")
    elif "search" in query:
        search_query = query.replace("search", "").strip()
        speak(f"Searching for {search_query}")
        pywhatkit.search(search_query)
    elif "time" in query or "date" in query:
        get_time_and_date()  
    else:
        ai_response = get_ai_response(query)
        speak(ai_response)

def get_time_and_date():
    now = datetime.datetime.now()
    current_time = now.strftime("%I:%M %p")  # Format: HH:MM AM/PM
    current_date = now.strftime("%A, %B %d, %Y")  # Format: Day, Month Date, Year
    speak(f"The current time is {current_time} and the date is {current_date}")

def play_sound():
    # Load an audio file
    sound = AudioSegment.from_file("alarm.mp3")  # Replace with your actual sound file
    samples = np.array(sound.get_array_of_samples(), dtype=np.float32)

    # Normalize samples
    samples /= np.max(np.abs(samples))

    # Play the sound
    sd.play(samples, samplerate=sound.frame_rate)
    sd.wait()  # Wait for the sound to finish playing

# Global flag to stop the alarm
alarm_running = True

def alarm_task(alarm_time):
    global alarm_running
    while alarm_running:  # Check if the alarm is still running
        current_time = datetime.datetime.now().strftime("%H:%M")
        if current_time == alarm_time:
            notification.notify(
                title="Alarm Notification",
                message="It's your alarm time... Press 'q' to stop.",
                timeout=10  
            )
            play_sound()  # Play notification sound
        time.sleep(10)  # Reduced sleep interval for better accuracy

        # Run the alarm in a separate thread so the user can stop it
        alarm_thread = threading.Thread(target=alarm_task, args=(alarm_time))
        alarm_thread.start()
        stop_alarm()  # Allows user to stop the alarm
        alarm_thread.join()

def stop_alarm():
    global alarm_running
    input("Press 'q' and Enter to stop the alarm: ")
    alarm_running = False

def set_alarm(alarm_time):
    try:
        datetime.datetime.strptime(alarm_time, "%H:%M")
        speak(f"Alarm set for {alarm_time}")
        alarm_thread = threading.Thread(target=alarm_task, args=(alarm_time,))
        alarm_thread.daemon = True  # Ensures the thread exits when the program closes
        alarm_thread.start()
    except ValueError:
        speak("Please provide the alarm time in the correct format (HH:MM).")

def cancel_alarm():
    global alarm_thread
    if alarm_thread and alarm_thread.is_alive():
        alarm_thread.join(timeout=0) #try to stop thread.
        alarm_thread = None
        speak("Alarm cancelled.")
    else:
        speak("No alarm is currently set.")

# Main function
def main():
    speak("Hi Hello There, I am Astra. Feel free to call my name if you need any assistance!!")
    while True:
        start = listen()
        if start:
            if start.lower() in ["hey astra","astra","hello astra","hi astra"]:
                speak("Yeah, I am here for you")
                query = listen()
                if query:
                    if query.lower() in ["exit", "stop", "quit", "bye"]:
                        speak("Goodbye! Have a nice day...")
                        break 
                    handle_command(query)

if __name__ == "__main__":
    main()