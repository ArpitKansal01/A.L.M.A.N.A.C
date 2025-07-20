import pyttsx3
import speech_recognition as sr
import eel
import time
import subprocess
import os 

def speak(text):
    text = str(text)
    engine = pyttsx3.init('sapi5')
    voices = engine.getProperty('voices')       #getting details of current voice
    engine.setProperty('voice', voices[0].id)   #changing index, changes voices. 1 for female
    rate = engine.getProperty('rate')   # getting details of current speaking rate                       #printing current voice rate
    engine.setProperty('rate', 160)
    eel.DisplayMessage(text)
    engine.say(text)
    eel.receiverText(text)
    engine.runAndWait()

def takecommand():
    speak("Hello, I am Almanac. How can I help you?")

    r = sr.Recognizer()
    mic_index = 2  # ✅ Use your working mic index here

    with sr.Microphone(device_index=mic_index) as source:
        print("🎙️ Listening...")
        eel.DisplayMessage("Listening...")
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source)

        try:
            audio = r.listen(source, timeout=10, phrase_time_limit=6)
            print("🧠 Recognizing...")
            eel.DisplayMessage("Recognizing...")

            query = r.recognize_google(audio, language='en-IN')
            print(f"User said: {query}")
            eel.DisplayMessage(query)
            time.sleep(2)
            return query.lower()

        except sr.WaitTimeoutError:
            eel.DisplayMessage("⏱️ Timeout: No speech detected.")
        except sr.UnknownValueError:
            eel.DisplayMessage("🤷 Could not understand the audio.")
        except sr.RequestError:
            eel.DisplayMessage("🔌 Could not reach Google servers.")
        except Exception as e:
            eel.DisplayMessage(f"⚠️ Error: {e}")

        return ""

@eel.expose
def allcommand(message=1):

    if message == 1:
        query = takecommand()
        print(query)
        eel.senderText(query)
    else:
        query = message
        eel.senderText(query)
    try:
        if "run developing mode" in query:
            try:
                project_dir = r"C:\Users\Asus\OneDrive\Desktop\Projects\IMAGE RECOGNIZE - Copy - Copy - Copy\server"  # ✅ Replace with actual path
                script_path = os.path.join(project_dir, "developer.py")
                
                subprocess.Popen(["python", script_path], cwd=project_dir)
                speak("Running Developing Mode")
            
            except Exception as e:
                print(f"Cannot start Developing Module: {e}")
                speak("Cannot start Developing Module")
        elif "run disease detection" in query:
            try:
                speak("Opening disease detection module")
                eel.loadDiseasePage()  # this calls a JS function you'll define on the frontend
            except Exception as e:
                print("Cannot open disease detection page")
                speak("Cannot open disease detection page")
        elif "what can you do" in query:
            speak("i am a fully functional voice assistant that can perform various tasks such as answering your questions. I can message or call anyone from your contacts, open any application of your laptop, play videos and can also create 3d shapes in a interactive developing module like blender using hand recognition. i can also predict potato disease using deep learning ")
        elif "open" in query:
            from engine.features import openCommand
            openCommand(query)
        elif "on youtube" in query:
            from engine.features import PlayYoutube
            PlayYoutube(query)
        elif "send message" in query or "phone call" in query or "video call" in query:
            from engine.features import findContact, whatsApp
            message = ""
            contact_no, name = findContact(query)
            if(contact_no != 0):

                if "send message" in query:
                    message = 'message'
                    speak("what message to send")
                    query = takecommand()
                    eel.receiverText(query)
                    
                elif "phone call" in query:
                    message = 'call'
                else:
                    message = 'video call'
                    
                whatsApp(contact_no, query, message, name)
        else:
            from engine.features import chatBot
            print(query)
            try:
                chatBot(query)
                print("✅ chatBot completed")
            except Exception as e:
                print("❌ chatBot failed with error:", e)

    except:
        print("Error in command")
    
    eel.ShowHood()
    