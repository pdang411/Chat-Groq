import os
import openai
import pygame
import tempfile
import time
from gtts import gTTS
import speech_recognition as sr
from dotenv import load_dotenv
import gradio as gr

load_dotenv()

from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODEL = "mixtral-8x7b-32768"

def chat_lm(input_data, history, is_voice):
    history = [history] if isinstance(history, str) else (history or [])
    text, is_voice = input_data

    if is_voice:
        print("Voice: " + text)

    if text.strip() != "":
        combined_input = " ".join(history + [text])
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": combined_input},
            ],
            temperature=0.7,
        )
        assistant_response = response.choices[0].message.content
        history.append(text)
        output = [("user", text), ("assistant", assistant_response)]
    else:
        output = []

    return history, output, is_voice

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        print("Listening...")
        audio = r.listen(source)
    try:
        text = r.recognize_google(audio)
    except Exception as e:
        print("Sorry, I couldn't understand. Please try again.")
        return "", False

    text = text.lower()
    return text, True

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

def generate_output(input_data, history):
    if not input_data:
        return history, []
    elif len (input_data) == 2:
        text, is_voice= input_data
    else:
        text = input_data[0]
        is_voice = False
    

    if not is_voice:
        if text.strip() == "":
            return history, []

    chat_lm_output = chat_lm((text, is_voice), history, is_voice)
    if len(chat_lm_output) < 3:
        return history, []
    
    history, output, is_voice = chat_lm_output
    
    if output:
        assistant_response = output[1][1]
        print("Assistant:", assistant_response)
        speak(assistant_response)

    return history, output, is_voice

prompt = "Enter a message to chat with the AI or click the microphone to speak"
block = gr.Interface(
    fn=generate_output,
    inputs=[gr.Textbox(placeholder=prompt, type="text", label="Message"), gr.Audio(type="filepath")],
    outputs="text",


)

block.launch(debug=True)