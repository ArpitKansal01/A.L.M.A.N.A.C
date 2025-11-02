from flask import Flask, request, jsonify, send_from_directory
import mysql.connector
import util
import json
import os
import webbrowser
import threading
import subprocess


app = Flask(__name__, static_folder='UI', static_url_path='')



# MySQL connection configuration
def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',    # Change to your MySQL server if it's not on localhost
        user='root',         # Your MySQL username
        password='root', # Your MySQL password
        database='Users' # Your database name
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

    # 👉 Check if the user already exists
    cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
    existing_user = cursor.fetchone()

    if existing_user:
        cursor.close()
        conn.close()
        return jsonify({"message": "User already exists!"}), 409  # Conflict status code

    # 👉 If not exists, insert the new user
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
        return jsonify({"message": "Invalid email or password!"}), 401  # Unauthorized

def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')

classDictionary = {"Arpit_Kansal": 0, "Daljeet_Kaur": 1, "Ishani_Dutt": 2, "Kashish_Gupta": 3, "Tevik_Rathore": 4}

@app.route('/verify_face', methods=['POST'])
def verify_face():
    image_data = request.form['image_data']

    # Save the base64 data to b64.txt
    with open('b64.txt', 'w') as f:
        f.write(image_data)

    # Run classification
    result = util.classify_image(image_data)
    print(result)
    if not result:
        return jsonify({'success': False, 'message': 'No face detected.'})

    best_result = result[0]
    top_confidence = max(best_result['class_probability'])  # Highest probability
    predicted_class_name = best_result['class']  # The predicted class index

    if top_confidence >= 50.0:
        # Now map index to name using class_dictionary
        print(f"Recognized: {predicted_class_name} with confidence: {top_confidence}%")
        return jsonify({'success': True, 'name': predicted_class_name})
    else:
        return jsonify({'success': False})

@app.route('/run_assistant', methods=['POST'])
def run_assistant():
    try:
        subprocess.Popen(['python', 'run.py'])  # Runs assistant.py without blocking
        return jsonify({'message': 'Assistant started successfully!'})
    except Exception as e:
        return jsonify({'message': f'Error starting assistant: {str(e)}'}), 500

if __name__ == '__main__':
    print("Starting Python Flask Server for facial recognition...")
    util.load_saved_artifacts()
    # Open the browser after a slight delay
    threading.Timer(1.25, open_browser).start()
    app.run(port=5000)
