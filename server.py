from flask import Flask, request, jsonify, send_from_directory
import mysql.connector
import util
import json
import os
import webbrowser
import threading
import subprocess
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__, static_folder='UI', static_url_path='')

# MySQL connection configuration
def get_db_connection():
    connection = mysql.connector.connect(
        host=os.environ.get("host"),
        port=os.environ.get("port"),
        user=os.environ.get("user"),
        password=os.environ.get("password"),
        database=os.environ.get("database")
    )
    return connection

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/classify_image', methods=['GET', 'POST'])
def classify_image():
    image_data = request.form['image_data']
    response = jsonify(util.classify_image(image_data))
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/sign_up', methods=['POST'])
def sign_up():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
    existing_user = cursor.fetchone()

    if existing_user:
        cursor.close()
        conn.close()
        return jsonify({"message": "User already exists!"}), 409

    cursor.execute('INSERT INTO users (name, email, password) VALUES (%s, %s, %s)', 
                   (name, email, password))
    conn.commit()

    cursor.close()
    conn.close()
    return jsonify({"message": "User created successfully!"})

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = %s AND password = %s', (email, password))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user:
        return jsonify({"message": "Login successful!"})
    else:
        return jsonify({"message": "Invalid email or password!"}), 401

classDictionary = {"Arpit_Kansal": 0, "Daljeet_Kaur": 1, "Ishani_Dutt": 2, "Kashish_Gupta": 3, "Tevik_Rathore": 4}

@app.route('/verify_face', methods=['POST'])
def verify_face():
    image_data = request.form['image_data']

    with open('b64.txt', 'w') as f:
        f.write(image_data)

    result = util.classify_image(image_data)
    if not result:
        return jsonify({'success': False, 'message': 'No face detected.'})

    best_result = result[0]
    top_confidence = max(best_result['class_probability'])
    predicted_class_name = best_result['class']

    if top_confidence >= 50.0:
        return jsonify({'success': True, 'name': predicted_class_name})
    else:
        return jsonify({'success': False})

@app.route('/run_assistant', methods=['POST'])
def run_assistant():
    try:
        subprocess.Popen(['python', 'run.py'])
        return jsonify({'message': 'Assistant started successfully!'})
    except Exception as e:
        return jsonify({'message': f'Error starting assistant: {str(e)}'}), 500


# ✅ Render-compatible server startup
if __name__ == '__main__':
    print("Starting Python Flask Server for facial recognition...")
    util.load_saved_artifacts()
    
    port = int(os.environ.get("PORT", 5000))  # Use Render's dynamic port
    app.run(host="0.0.0.0", port=port)
