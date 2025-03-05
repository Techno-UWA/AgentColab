import os
import subprocess
import tkinter as tk
import datetime 
from tkinter import scrolledtext
import speech_recognition as sr
from groq import Groq


client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def take_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("listening...")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print("Recognising...")
        query = r.recognize_google(audio, language='en-us')
        
    except Exception as e:
        print(e)
        return ""
    return query.lower()  # Convert the query to lowercase for easier comparison

def speak(text):
    """Convert text to speech and play it."""
    voice = "en-US-AriaNeural"
    command = f'edge-tts --voice "{voice}" --text "{text}" --write-media "audio/output.mp3"'
    os.system(command)
    subprocess.run(["afplay", "audio/output.mp3"])  # Use afplay on macOS

def send_message():
    while True:
        """Handle user input and get AI response."""
        query = take_command()
        # Call AI API
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": query}],
            model="llama3-8b-8192",
        )
        response = chat_completion.choices[0].message.content
                
        speak(response)
            
        
def basic_message(self):
    query = take_command()
    if "what is the time" or "tell me the time" in query:
        print(self.timezone)


if __name__ == "__main__":
    send_message()
