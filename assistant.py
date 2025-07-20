import os
from engine.features import *
import eel
from engine.command import *

def start():
    eel.init('UI')  # Initializes the folder where your frontend files (HTML, CSS, JS) are located.
    
    os.system('start chrome  --app=http://localhost:8000/Dashboard.html')  # Opens Chrome in app mode.
    
    playAssistantSound()  # Plays a sound (presumably a custom function for assistant feedback).
    
    eel.start('Dashboard.html', mode=None, host='localhost', block=True)  # Starts the Eel server.
