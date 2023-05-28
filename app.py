from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2

app = Flask(__name__)
CORS(app)

# PostgreSQL database configuration
conn = psycopg2.connect(
    host='dpg-chlrr4fdvk4sq14sv42g-a.oregon-postgres.render.com',
    database='pandafit',
    user='pandafit_user',
    password='87juV5ghHEfCQxcHSUddSMx6fmjTdrDi'
)

# User registration
@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data['username']
        password = data['password']
        role = data['role']
        # Check if the username already exists
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        row = cursor.fetchone()
        if row is not None:
            cursor.close()
            return jsonify({'error': 'Username already exists'}), 409
        # Create a new user
        cursor.execute('INSERT INTO users (username, password, role) VALUES (%s, %s, %s) RETURNING *',
                       (username, password, role))
        row = cursor.fetchone()
        cursor.close()
        user = {
            'userid': row[0],
            'username': row[1],
            'password': row[2],
            'role': row[3],
            'created_at': row[4]
        }
        return jsonify(user), 201
    except Exception as e:
        print('Database error:', e)
        return jsonify({'error': 'Internal server error'}), 500

# User login
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data['username']
        password = data['password']
        # Check if the username and password match
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        row = cursor.fetchone()
        cursor.close()
        if row is None:
            return jsonify({'error': 'Invalid username or password'}), 401
        user = {
            'userid': row[0],
            'username': row[1],
            'password': row[2],
            'role': row[3],
            'created_at': row[4]
        }
        return jsonify(user)
    except Exception as e:
        print('Database error:', e)
        return jsonify({'error': 'Internal server error'}), 500

# ... Existing routes and functions ...

if __name__ == '_main_':
    app.run(debug=True)