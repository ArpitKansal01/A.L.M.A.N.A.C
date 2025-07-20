import mediapipe as mp

try:
    print("Testing MediaPipe Hands...")
    hands = mp.solutions.hands.Hands()
    print("MediaPipe Hands loaded successfully!")
except Exception as e:
    print("Error loading MediaPipe:", e)