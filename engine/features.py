from playsound import playsound
import eel
import os
import webbrowser
from engine.command import speak
import pywhatkit as kit
import re
import sqlite3
from engine.helper import extract_yt_term
import pvporcupine
import pyaudio
import struct
import time
from engine.helper import remove_words
from urllib.parse import quote
import subprocess
import pyautogui
import pygame
import time
conn = sqlite3.connect('almanac.db')
cursor = conn.cursor()


# Playing Assistant Sound 
@eel.expose
def playAssistantSound():
    # music_dir="UI\\assets\\audio\\start_sound.mp3"
    # playsound(music_dir)
    pygame.mixer.init()
    pygame.mixer.music.load("UI/assets/audio/start_sound.mp3")
    pygame.mixer.music.play()
    
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)  # Wait until the sound finishes playing


def openCommand(query): 
    query = query.replace("almanac", "")
    query = query.replace("open", "")
    query.lower()
    app_name = query.strip()

    if app_name != "":

        try:
            cursor.execute(
                'SELECT path FROM sys_command WHERE name = (?)', (app_name,))
            results = cursor.fetchall()

            if len(results) != 0:
                speak("Opening "+query)
                os.startfile(results[0][0])

            elif len(results) == 0: 
                cursor.execute(
                'SELECT url FROM web_command WHERE name = (?)', (app_name,))
                results = cursor.fetchall()
                
                if len(results) != 0:
                    speak("Opening "+query)
                    webbrowser.open(results[0][0])

                else:
                    speak("Opening "+query)
                    try:
                        os.system('start '+query)
                    except:
                        speak("not found")
        except:
            speak("some thing went wrong")


def PlayYoutube(query):
    search_term = extract_yt_term(query)
    speak("Playing "+search_term+" on YouTube")
    kit.playonyt(search_term)  

def hotword():
    porcupine=None
    paud=None
    audio_stream=None
    try:
       
        # pre trained keywords    
        porcupine=pvporcupine.create(keywords=["jarvis","alexa"]) 
        paud=pyaudio.PyAudio()
        audio_stream=paud.open(rate=porcupine.sample_rate,channels=1,format=pyaudio.paInt16,input=True,frames_per_buffer=porcupine.frame_length)
        
        # loop for streaming
        while True:
            keyword=audio_stream.read(porcupine.frame_length)
            keyword=struct.unpack_from("h"*porcupine.frame_length,keyword)

            # processing keyword comes from mic 
            keyword_index=porcupine.process(keyword)

            # checking first keyword detetcted for not
            if keyword_index>=0:
                print("hotword detected")

                # pressing shorcut key win+j
                import pyautogui as autogui
                autogui.keyDown("win")
                autogui.press("z")
                time.sleep(2)
                autogui.keyUp("win")
                
    except:
        if porcupine is not None:
            porcupine.delete()
        if audio_stream is not None:
            audio_stream.close()
        if paud is not None:
            paud.terminate()

# Whatsapp Message Sending
def findContact(query):    
    
    words_to_remove = ["almanac", 'make', 'a', 'to', 'phone', 'call', 'send', 'message', 'wahtsapp', 'video']
    query = remove_words(query, words_to_remove)

    try:
        query = query.strip().lower()
        cursor.execute("SELECT mobile_no FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?", ('%' + query + '%', query + '%'))
        results = cursor.fetchall()
        print(results[0][0])
        mobile_number_str = str(results[0][0])
        if not mobile_number_str.startswith('+'):
            mobile_number_str = '+' + mobile_number_str
        elif not mobile_number_str.startswith('+91'):
            mobile_number_str = '+91' + mobile_number_str

        return mobile_number_str, query
    except:
        speak('not exist in contacts')
        return 0, 0

def whatsApp(mobile_no, message, flag, name):

    if flag == 'message':
        target_tab = 13
        jarvis_message = "message send successfully to "+name

    elif flag == 'call':
        target_tab = 7
        message = ''
        jarvis_message = "calling to "+name

    else:
        target_tab = 6
        message = ''
        jarvis_message = "starting video call with "+name

    # Encode the message for URL
    encoded_message = quote(message)

    # Construct the URL
    whatsapp_url = f"whatsapp://send?phone={mobile_no}&text={encoded_message}"

    # Construct the full command
    full_command = f'start "" "{whatsapp_url}"'

    # Open WhatsApp with the constructed URL using cmd.exe
    subprocess.run(full_command, shell=True)
    time.sleep(5)
    subprocess.run(full_command, shell=True)
    
    time.sleep(2)
    pyautogui.hotkey('ctrl', 'f')
    for i in range(1, target_tab):
        pyautogui.hotkey('tab')
    pyautogui.hotkey('enter')
    speak(jarvis_message)

# chat bot 
def chatBot(query):
    import google.generativeai as genai
    from google.generativeai.types import GenerationConfig
    genai.configure(api_key="AIzaSyDME1zikC3YA5ZCg2R6Q6iPMoMAJrfWk6E")
    try:
        
        model = genai.GenerativeModel("gemini-2.0-flash")
        short_query = f"{query}\n\nPlease reply in less than 100 words."
        response = model.generate_content(
            short_query,
            generation_config=GenerationConfig(
                temperature=0.7,
                top_p=1.0,
                top_k=1,
                max_output_tokens=2048,
            )
        )
        ai_reply = response.text.strip()
        print(ai_reply)
        speak(ai_reply)
        return ai_reply
    except Exception as e:
        print(f"[ERROR] Gemini API: {e}")
        return "I couldn't connect to AI services."
