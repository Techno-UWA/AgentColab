import os
import subprocess
import tkinter as tk
from tkinter import scrolledtext
import speech_recognition as sr
from groq import Groq

class ChatBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice AI Chatbot")
        self.root.geometry("500x600")
        self.root.configure(bg="#121212")

        # Chat display area
        self.chat_display = scrolledtext.ScrolledText(root, wrap=tk.WORD, bg="#1E1E1E", fg="white", font=("Arial", 12))
        self.chat_display.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Entry field
        self.user_input = tk.Entry(root, font=("Arial", 12), bg="#333333", fg="white")
        self.user_input.pack(pady=5, padx=10, fill=tk.X)

        # Buttons
        self.send_button = tk.Button(root, text="Send", command=self.send_message, bg="#0078D7", fg="white", font=("Arial", 12))
        self.send_button.pack(pady=5, padx=10, fill=tk.X)

        self.voice_button = tk.Button(root, text="🎤 Voice Input", command=self.voice_input, bg="#444444", fg="white", font=("Arial", 12))
        self.voice_button.pack(pady=5, padx=10, fill=tk.X)

        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    def speak(self, text):
        """Convert text to speech and play it."""
        voice = "en-US-AvaNeural"
        command = f'edge-tts --voice "{voice}" --text "{text}" --write-media "audio/output.mp3"'
        os.system(command)
        subprocess.run(["afplay", "audio/output.mp3"])  # Use afplay on macOS

    def send_message(self):
        """Handle user input and get AI response."""
        query = self.user_input.get().strip()
        if query:
            self.chat_display.insert(tk.END, f"You: {query}\n", "user")
            self.user_input.delete(0, tk.END)

            # Call AI API
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": query}],
                model="llama3-8b-8192",
            )
            response = chat_completion.choices[0].message.content

            self.chat_display.insert(tk.END, f"AI: {response}\n", "bot")
            self.speak(response)
            self.chat_display.yview(tk.END)

    def voice_input(self):
        """Capture voice and send as input."""
        r = sr.Recognizer()
        with sr.Microphone() as source:
            self.chat_display.insert(tk.END, "Listening...\n", "system")
            self.chat_display.yview(tk.END)
            r.pause_threshold = 1
            audio = r.listen(source)

        try:
            query = r.recognize_google(audio, language="en-us").lower()
            self.user_input.insert(0, query)
            self.send_message()
        except Exception as e:
            self.chat_display.insert(tk.END, "Error: Could not understand voice input.\n", "error")
            self.chat_display.yview(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    chatbot = ChatBotGUI(root)
    root.mainloop()
