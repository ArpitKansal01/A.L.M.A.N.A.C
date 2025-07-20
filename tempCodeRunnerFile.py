from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import cv2
import mediapipe as mp
import math
import time
import logging
import threading
import os
import signal


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')


# MediaPipe Hand setup
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils  # For debug visualization

try:
    print("🟡 Initializing MediaPipe Hands...")
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7
    )
    print("🟢 MediaPipe Hands initialized successfully")
except Exception as e:
    print("🔴 MediaPipe Hands failed:", e)
    hands = None

camera_active = False

def detect_gesture(landmarks):
    try:
        # Thumb angle calculation
        thumb_tip = landmarks[mp_hands.HandLandmark.THUMB_TIP]
        thumb_base = landmarks[mp_hands.HandLandmark.THUMB_CMC]
        thumb_angle = math.degrees(math.atan2(
            thumb_tip.y - thumb_base.y,
            thumb_tip.x - thumb_base.x
        ))

        # Count extended fingers
        extended_fingers = 0
        finger_tips = [mp_hands.HandLandmark.INDEX_FINGER_TIP,
                       mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
                       mp_hands.HandLandmark.RING_FINGER_TIP,
                       mp_hands.HandLandmark.PINKY_TIP]
        finger_pips = [mp_hands.HandLandmark.INDEX_FINGER_PIP,
                       mp_hands.HandLandmark.MIDDLE_FINGER_PIP,
                       mp_hands.HandLandmark.RING_FINGER_PIP,
                       mp_hands.HandLandmark.PINKY_PIP]

        for tip, pip in zip(finger_tips, finger_pips):
            if landmarks[tip].y < landmarks[pip].y:
                extended_fingers += 1

        # Determine gesture
        if extended_fingers >= 3:
            gesture = "open"
        elif extended_fingers <= 1:
            gesture = "fist"
        else:
            gesture = "pinch"

        return gesture, thumb_angle, extended_fingers
    except Exception as e:
        logger.error(f"Gesture detection error: {e}")
        return "unknown", 0, 0


def track_hands():
    global camera_active

    logger.info("Initializing camera...")

    # Try multiple camera indices
    for camera_index in range(3):  # Try 3 different camera indices
        cap = cv2.VideoCapture(camera_index)
        if cap.isOpened():
            logger.info(f"Successfully opened camera index {camera_index}")
            break
        cap.release()
    else:
        logger.error("Failed to open any camera")
        socketio.emit('camera_error', {'message': 'Could not open any camera'})
        return

    camera_active = True

    try:
        # Set camera properties for better performance
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)

        # Warm-up camera
        for _ in range(5):
            cap.read()
            time.sleep(0.1)

        while camera_active:
            ret, frame = cap.read()
            if not ret:
                logger.warning("Frame read failed")
                time.sleep(0.1)
                continue

            # Flip frame for mirror effect
            frame = cv2.flip(frame, 1)

            # Convert to RGB for MediaPipe
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(image)

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Get gesture data
                    gesture, thumb_angle, finger_count = detect_gesture(hand_landmarks.landmark)
                    wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
                    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]

                    # Calculate pinch distance (Euclidean distance in normalized space)
                    pinch_distance = math.sqrt(
                        (thumb_tip.x - index_tip.x)**2 +
                        (thumb_tip.y - index_tip.y)**2 +
                        (thumb_tip.z - index_tip.z)**2
                    )

                    socketio.emit('gesture_data', {
                        'gesture': gesture,
                        'position': {
                            'x': wrist.x,
                            'y': wrist.y,
                            'z': wrist.z
                        },
                        'thumb_angle': thumb_angle,
                        'finger_count': finger_count,
                        'index_tip': {
                            'x': index_tip.x,
                            'y': index_tip.y,
                            'z': index_tip.z
                        },
                        'thumb_tip': {
                            'x': thumb_tip.x,
                            'y': thumb_tip.y,
                            'z': thumb_tip.z
                        },
                        'pinch_distance': pinch_distance
                    })

            # Small delay to prevent overwhelming the system
            time.sleep(0.03)  # ~30fps

    except Exception as e:
        logger.error(f"Tracking error: {e}")
        socketio.emit('camera_error', {'message': str(e)})
    finally:
        if cap and cap.isOpened():
            cap.release()
        camera_active = False
        logger.info("Camera released")


@app.route('/')
def index():
    return render_template('index.html')  # Boot screen


@app.route('/web.html')
def web():
    return render_template('web.html')  # Main app


@socketio.on('connect')
def handle_connect():
    logger.info("New client connected")
    if not camera_active:
        threading.Thread(target=track_hands, daemon=True).start()


@socketio.on('disconnect')
def handle_disconnect():
    logger.info("Client disconnected")


if __name__ == '__main__':
    print("🚀 Starting Flask-SocketIO server...")
    logger.info("Starting server on http://localhost:8000")
    socketio.run(app,
                 host='0.0.0.0',
                 port=8000,
                 allow_unsafe_werkzeug=True,
                 debug=True)
