import os
import subprocess
import random
import speech_recognition as sr
import webbrowser
import pyautogui
import pygame
import requests
import threading
import cv2
import numpy as np 
import pyjokes

from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from pynput.keyboard import Key, Controller as KeyboardController
from gui_scripts.buttons import Button
from gui_scripts.gui_settings import *

def speak(text):
    voice = "en-US-AvaNeural"
    command = f'edge-tts --voice "{voice}" --text "{text}" --write-media "audio/output.mp3"'
    os.system(command)
    subprocess.run(["afplay", "audio/output.mp3"])  # Use afplay to play the audio on macOS
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

def get_web_content(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.get_text()


def capture_and_display():
    cap = cv2.VideoCapture(0)  # Open the built-in camera (index 0)
    
    # Continuously capture and display frames from the camera
    while True:
        ret, frame = cap.read()  # Read a frame from the camera
        
        # Perform basic image analysis (in this case, just display the shape of the scanned object)
        shape = frame.shape  # Get the shape of the image (height, width, channels)
        shape_str = f"Shape: {shape}"
        
        # Speak out the shape
        speak(shape_str)
        
        # Overlay the shape information on the frame
        cv2.putText(frame, shape_str, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Display the frame
        cv2.imshow('Camera Feed', frame)
        
        # Wait for a key press and check if it's the 'q' key to exit the loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Release the camera and close all OpenCV windows
    cap.release()
    cv2.destroyAllWindows()


def set_brightness(brightness_level):
    subprocess.run(['xrandr', '--output', 'YOUR_DISPLAY_NAME', '--brightness', str(brightness_level)])

sleep_mode = False 
previous_queries = []

# the knowledge bank
knowledge_bank = {} # will be filled with info until I can figure out how to either create an llm or integrate one wiithout any costs 

wake_word = "friday" # this will activate the ai when said, else the assistant will not do anything

# jokes that the ai will have access to
jokes_bank = [
            "Why don't skeletons fight each other? They don't have the guts.",
            "I told my wife she should embrace her mistakes. She gave me a hug.",
            "Parallel lines have so much in common. It's a shame they'll never meet.",
            "Why did the scarecrow win an award? Because he was outstanding in his field.",
            "I'm reading a book on anti-gravity. It's impossible to put down!",
            "Why don't scientists trust atoms? Because they make up everything!",
            "What do you call fake spaghetti? An impasta!",
            "Why don't eggs tell jokes? They'd crack each other up!",
            "Did you hear about the claustrophobic astronaut? He needed space.",
            "I'm on a whiskey diet. I've lost three days already.",
            "I told my computer I needed a break. Now it won't stop sending me vacation ads.",
            "Why did the math book look sad? Because it had too many problems.",
            "I'm reading a horror story in Braille. Something bad is about to happen... I can feel it.",
            "Why don't skeletons fight each other? They don't have the guts.",
            "I'm writing a book on reverse psychology. Please don't buy it.",
            "What do you call a bear with no teeth? A gummy bear!",
            "I told my wife she should embrace her mistakes. She gave me a hug.",
            "Why did the bicycle fall over? Because it was two-tired!",
            "I told my wife she should embrace her mistakes. She gave me a hug.",
            "Did you hear about the cheese factory that exploded? There was nothing left but de-brie!",
            "Why don't scientists trust atoms... Because they make up everything",
            "Did you hear about the mathematician who's afraid of negative numbers? He'll stop at nothing to avoid them.",
            "Why did the scarecrow win an award? Because he was outstanding in his field!",
            "Why couldn't the bicycle stand up by itself? Because it was two-tired!",
            "Why did the tomato turn red? Because it saw the salad dressing!",
            "What did one ocean say to the other ocean? Nothing, they just waved!",
            "Why don't skeletons fight each other? They don't have the guts!",
            "What did one hat say to the other hat? You stay here, I'll go on ahead!",
            "Why did the golfer bring two pairs of pants? In case he got a hole in one!"
        ]

# Create an instance of the keyboard controller
keyboard = KeyboardController()

# ai assistant GUI layout 
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)  # Make the window resizable
pygame.display.set_caption("AI Assistant")
clock = pygame.time.Clock()

# ai assistant gui font
font = pygame.font.Font('fonts/Arial.ttf', 16)
title_font = pygame.font.Font('fonts/Elianto-Regular.ttf', 60)
subtitle_font = pygame.font.Font('fonts/PPStellar-Light.otf', 45)

def get_assistant_response(user_input):
    # placeholder function for assistant's response logic
    return "I am your assistant. How can I help you?"

def increase_volume(percentage_increase):
    # Get the current volume
    current_volume = int(subprocess.check_output(["osascript", "-e", "output volume of (get volume settings)"]).decode("utf-8").strip())
    
    # Calculate the new volume level
    new_volume = min(current_volume + percentage_increase, 100)  # Ensure new volume doesn't exceed 100%

    # Set the new volume level using subprocess
    subprocess.run(["osascript", "-e", f'set volume output volume {new_volume}'])

def decrease_volume(percentage_decrease):
    # Get the current volume
    current_volume = int(subprocess.check_output(["osascript", "-e", "output volume of (get volume settings)"]).decode("utf-8").strip())
    
    # Calculate the new volume level
    new_volume = max(current_volume - percentage_decrease, 0)  # Ensure new volume doesn't go below 0%
    
    # Set the new volume level using subprocess
    subprocess.run(["osascript", "-e", f'set volume output volume {new_volume}'])

def increase_brightness():
    current_brightness = int(subprocess.check_output(['brightness', '-l']).splitlines()[0].split()[-1])
    new_brightness = min(current_brightness + 0.1, 1.0)  # Increase by 0.1 or less, capped at 1.0
    subprocess.run(['brightness', str(new_brightness)])

def decrease_brightness():
    current_brightness = int(subprocess.check_output(['brightness', '-l']).splitlines()[0].split()[-1])
    new_brightness = max(current_brightness - 0.1, 0.0)  # Decrease by 0.1 or less, capped at 0.0
    subprocess.run(['brightness', str(new_brightness)])

def get_battery_percentage():
    output = subprocess.check_output(['pmset', '-g', 'batt'])
    output = output.decode('utf-8')  # Convert bytes to string for parsing
    lines = output.split('\n')
    for line in lines:
        if 'InternalBattery' in line:
            percentage_index = line.find('%')
            if percentage_index != -1:
                percentage = line[percentage_index-3:percentage_index+1].strip()
                return int(percentage)
    return None
 
def display():
    # Pre-load frames
    ai_frames = [pygame.image.load(f'frames/{i:03d}.png').convert_alpha() for i in range(162)]
    frame_count = len(ai_frames)
    frame_index = 0

    # load the gui title + subtitle texts
    title_text = title_font.render("AI ASSISTANT", True, WHITE)
    subtitle_text = subtitle_font.render("Say Friday to Activate", True, WHITE)

    running = True # flag to control the game loop

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False 

            elif event.type == pygame.VIDEORESIZE:  # Handle window resize event
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                WIDTH, HEIGHT = event.w, event.h  # Update WIDTH and HEIGHT variables
                
        screen.fill((3, 3, 20))  # Adjust background color
        
        # Adjust position and size of AI frames dynamically
        frame_size = ai_frames[frame_index].get_size()
        frame_x = (WIDTH - frame_size[0]) // 2
        frame_y = (HEIGHT - frame_size[1]) // 2
        screen.blit(ai_frames[frame_index], (frame_x, frame_y))

        # the exit button to leave the screen
        exit_button = Button(screen, BLACK, 1100, 800, 192, 51, "Exit", WHITE, font, hover_colour=WHITE)

        exit_button.draw()
        if exit_button.is_clicked():
            running = False 
        
        # draw the fonts on the screen
        screen.blit(title_text, (450, 20))
        screen.blit(subtitle_text, (480, 700))

        frame_index = (frame_index + 1) % frame_count

        pygame.display.update()

        clock.tick(30)
    
    pygame.quit()

def main():
    while True:
        query = take_command()
        print("You: " + query)

        if wake_word in query:
            speak("Friday here!, your virtual assistant. What can I do for you?")

            while True:
                query = take_command()
                print("You: " + query)

                if "hello" in query or "hi" in query or "yo" in query or "greetings" in query:
                    responses = ["Hello! How are you today?", "Hey there! What's up?", "Hi! What can I do for you?"]
                    speak(random.choice(responses))

                elif "how are you" in query:
                    responses = ["I'm doing well, thank you!", "I'm here and ready to assist!", "Feeling great, thanks for asking!"]
                    speak(random.choice(responses))

                elif any(word in query for word in ["sad", "not good", "unhappy"]):
                    speak("I'm sorry to hear that. Is there anything I can do to help?")

                elif "hey friday" in query:
                    responses = ["Yes? Is there anything you need?", "Mhm? What is it?", "Hey there! What can I assist you with?"]
                    speak(random.choice(responses))

                elif "what is your name" in query:
                    speak("I am Friday, and i'm ready to help.")
                
                elif "assalam alaikum" in query:
                    speak("Wa Alaikum Assalaam")

                # Add more diverse responses based on context
                elif "open" in query:
                    responses = ["Sure thing!", "Opening it up for you!", "Here we go!"]
                    speak(random.choice(responses))
                    app_name = query.replace("open", "").strip()  # Remove "open" and any leading/trailing spaces
                    try:
                        # Use subprocess to open the application on macOS
                        subprocess.run(["open", "-a", app_name])
                    except Exception as e:
                        print(e)
                        speak(f"Sorry, I couldn't open {app_name}.")

                elif "close" in query:
                    responses = ["Closing it down!", "Got it, shutting it!", "Closing up shop!"]
                    speak(random.choice(responses))
                    app_name = query.replace("close", "").strip()  # Remove "close" and any leading/trailing spaces
                    try:
                        # Use osascript to execute AppleScript to close the application
                        os.system(f"osascript -e 'quit app \"{app_name}\"'")
                    except Exception as e:
                        print(e)
                        speak(f"Sorry, I couldn't close {app_name}.")

                elif "play" in query:
                    responses = ["Sure, playing that for you!", "Let's get some music going!", "Time for some tunes!"]
                    speak(random.choice(responses))
                    song_name = query.replace("play", " ").strip()
                    # Open YouTube URL for the song in the default web browser
                    webbrowser.open(f"https://www.youtube.com/results?search_query={song_name}")

                elif "pause" in query:
                    try:
                        speak("Pausing now.")
                        pyautogui.hotkey('k')
                    except Exception as e:
                        print(e)
                        speak(f"Sorry couldn't pause it.")

                elif "resume" in query:
                    try:
                        speak("Resuming now")
                        pyautogui.hotkey('k')
                    except Exception as e:
                        print(e)
                        speak(f"Sorry couldn't pause it.")

                elif "time" in query:
                    current_time = datetime.now().strftime("%I:%M %p")  # %I for 12-hour format
                    responses = [f"The current time is {current_time}.", f"It's {current_time} now.", f"{current_time} at the moment."]
                    speak(random.choice(responses))
                
                elif "date" in query:
                    pass

                elif "what is rizz" in query:
                    speak("Rizz is the ability to charm and woo a person")
                    speak("Something that CLYDE DOES NOT HAVE")

                elif "tell me a joke" in query:
                    jokes = jokes_bank
                    speak(random.choice(jokes))

                elif "search" in query:
                    query = query.replace("search", "").strip()
                    speak("Searching the web for you.")
                    # Perform a Google search and get the text content of the first search result
                    search_url = f"https://www.google.com/search?q={query}"
                    web_content = get_web_content(search_url)
                    # Analyze the web content and generate a response
                    # For simplicity, let's just speak the first 500 characters of the web content
                    speak(web_content[:500])

                elif "set a reminder that" in query:
                    rememberMessage = query.replace("remeber that", "")
                    speak("you told me to remember that" + rememberMessage)
                    remember = open("remember.txt", "a")
                    remember.write(rememberMessage)
                    remember.close()

                elif "tell reminders" in query:
                    remember = open("remember.txt", "r")
                    speak("you told me to remember" + remember.read())

                elif "clear reminders" in query:
                    file = open("remember.txt", "w")
                    file.write(f"")
                    speak("all done all the reminders have been cleared. Anything else?")

                # Add more responses for interacting with tabs, setting timers, etc.
                elif "next tab" in query:
                    speak("Switching tabs now")
                    with keyboard.pressed(Key.cmd):
                        keyboard.press(Key.tab)
                        keyboard.release(Key.tab)
                
                elif "previous tab" in query:
                    speak("Switching tabs now")
                    with keyboard.pressed(Key.cmd) and keyboard.pressed(Key.shift):
                        keyboard.pressed(Key.tab)
                        keyboard.release(Key.tab)
                        

                elif "close tab" in query:
                    speak("Closing the current tab")
                    with keyboard.pressed(Key.cmd):
                        keyboard.press('w')
                        keyboard.release('w')

                elif "swipe right" in query:
                    speak("Swiping to the next window")
                    with keyboard.pressed(Key.ctrl):
                        keyboard.press(Key.right)
                        keyboard.release(Key.right)

                elif "swipe left" in query:
                    speak("Swipe to the previous window")
                    with keyboard.pressed(Key.ctrl):
                        keyboard.press(Key.left)
                        keyboard.release(Key.left)
                
                elif "image" in query:
                    speak("Capturing image for analysis") # outputs the imagge 
                    capture_and_display() # performs the image capturing and analysis 
                
                # battery checking
                elif "battery" in query:
                    battery_percentage= get_battery_percentage()
                    if battery_percentage is not None:
                        speak(f"Your battery is {battery_percentage}%")
                    else:
                        speak("Battery percentage not found")
                
                # volume control
                elif "increase volume" in query:
                    increase_volume(15)
                    speak("volume increased")
                
                elif "decrease volume" in query:
                    decrease_volume(15)
                    speak("volume decreased")
                
                elif "increase brightness" in query:
                    speak("increasing brightness")
                    increase_brightness(10)
                
                elif "decrease brightness" in query:
                    speak("decreasing brightness")
                    decrease_brightness(10)

                elif "sleep" in query:
                    speak("Ok, I am going to sleep now, you can call me anytime you need, just say wake up and I'll be there.")
                    sleep_mode = True

                elif "goodbye" in query:
                    speak("Ok, goodbye, see you next time. Have a good one!")
                    break 

                else:
                    speak("I'm not sure I understand. Can you repeat that?")

            while sleep_mode:
                query = take_command().lower()
                print(query)

                if "wake up" in query:
                    speak("Oh hello, I am awake now, what's up?")
                    sleep_mode = False 

                if "sorry where were we" in query:
                    speak("Its alright no problem, I was going to ask if you needed anything.")
                    sleep_mode = False 

                elif "hey friday" in query:
                    responses = ["Yes, sorry, was a bit tired. what's up? What can I do for you?", 
                                "Hey there! Back in action. How can I assist?", 
                                "I'm up! What do you need?"]
                    speak(random.choice(responses))

if __name__ == "__main__":
    # Start the main function in the main thread
    main_thread = threading.Thread(target=main)
    main_thread.start()

    # Run the display function in the main thread
    display()
