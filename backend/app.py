from flask import Flask, request, jsonify, send_from_directory
import sqlite3
import os

app = Flask(__name__, static_folder='../frontend', static_url_path='')

# Path to the SQLite database
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'database/maritime.db')

# Function to initialize the database
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            user_type TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Initialize the database
init_db()

# Route to serve static files
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'login.html')

# Endpoint for user signup
@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data['username']
    password = data['password']
    user_type = data['user_type']
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO users (username, password, user_type)
            VALUES (?, ?, ?)
        ''', (username, password, user_type))
        conn.commit()
        response = {'message': 'User registered successfully'}
    except sqlite3.IntegrityError:
        response = {'message': 'Username already exists'}
    finally:
        conn.close()
    
    return jsonify(response)

# Endpoint for user login
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT user_type FROM users WHERE username = ? AND password = ?
    ''', (username, password))
    
    user = cursor.fetchone()
    conn.close()
    
    if user:
        response = {'user_type': user[0]}
    else:
        response = {'message': 'Invalid credentials'}
    
    return jsonify(response)

# Serve dashboard pages based on user type
@app.route('/<user_type>')
def serve_dashboard(user_type):
    valid_user_types = ['ship_owner', 'crew_member', 'management_employee', 'ship']
    if user_type in valid_user_types:
        return send_from_directory(app.static_folder, f'{user_type}.html')
    else:
        return "Invalid user type", 404

if __name__ == '__main__':
    app.run(debug=True)
