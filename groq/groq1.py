import os
import openai
import os
import pygame
import tempfile
import time
from gtts import gTTS
import speech_recognition as sr
from dotenv import load_dotenv
import gradio as gr


load_dotenv()

#from newvoices import speak

from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

MODEL= "mixtral-8x7b-32768"


def chat_lm(input_text, history):
    history = history or []
    if input_text.strip() != "":
        combined_input = " ".join(history + [input_text])
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": combined_input},
            ],
            temperature=0.7,
        )
        assistant_response = response.choices[0].message.content
        history.append(input_text)
        output = [("user", input_text), ("assistant", assistant_response)]
    else:
        output = []
    return history, output

# Function to listen to microphone
def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        print("Listening...")
        audio = r.listen(source)
    try:
        text = r.recognize_google(audio)
    except sr.RequestError as re:
        print(re)
        print("Sorry, I encountered an error. Please try again.")
        return ""
    except sr.UnknownValueError as uve:
        print(uve)
        print("Sorry, I couldn't understand. Please try again.")
        return ""
    text = text.lower()
    return text

# Function to speak the text
def speak(text):
    tts = gTTS(text=text, lang="en")
    temp = tempfile.NamedTemporaryFile(delete=False)
    temp.close()
    tts.save(temp.name)

    pygame.mixer.init()
    pygame.mixer.music.load(temp.name)
    pygame.mixer.music.play()
    print(text)
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    pygame.mixer.quit()

# Function to handle UI input and output
def generate_output(input_text, history):
    if input_text.strip() == "":
        return history, []

    history, output = chat_lm(input_text, history)
    if output:
        assistant_response = output[1][1]
        print("Assistant:", assistant_response)
        speak(assistant_response)

    return history, output

# UI setup
prompt = "Enter a message to chat with the AI"
block = gr.Interface(
    fn=generate_output,
    inputs=gr.Textbox(placeholder=prompt, type="text", label="Message"),
    outputs="text",
)

# Launch the UI
block.launch(debug=True)
