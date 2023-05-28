from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from datetime import datetime

app = Flask(__name__)
CORS(app)

# PostgreSQL database configuration
conn = psycopg2.connect(
    host='dpg-chlrr4fdvk4sq14sv42g-a.oregon-postgres.render.com',
    database='pandafit',
    user='pandafit_user',
    password='87juV5ghHEfCQxcHSUddSMx6fmjTdrDi'
)

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if data is None:
            return jsonify({'error': 'Invalid JSON payload'}), 400
        try: 
            username = data['username']
            password = data['password']
            role = data['role']
        except Exception as e:
            return jsonify({'error': 'Invalid JSON payload'}), 400

        if not (username and password and role):
            return jsonify({'error': 'Missing required fields'}), 400

        error = None

        # Check if the username already exists
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
            row = cursor.fetchone()
            cursor.close()

            if row is not None:
                error = 'Username already exists'
        except Exception as e:
            error = 'Error checking username: {}'.format(e)

        if error is not None:
            return jsonify({'error': error}), 409

        # Create a new user
        try:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (username, password, role) VALUES (%s, %s, %s) RETURNING *',
                           (username, password, role))
            row = cursor.fetchone()
            cursor.close()
            conn.commit()

            user = {
                'userid': row[0],
                'username': row[1],
                'password': row[2],
                'role': row[3],
            }
            return jsonify(user), 201
        except Exception as e:
            error = 'Error creating new user: {}'.format(e)
        
        if error is not None:
            return jsonify({'error': error}), 500

    except Exception as e:
        error = 'Error processing registration: {}'.format(e)
        return jsonify({'error': error}), 500


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
        }
        return jsonify(user)
    except Exception as e:
        print('Database error:', e)
        return jsonify({'error': 'Internal server error'}), 500
    
@app.route('/weight', methods=['POST'])
def weight():
    # try:
        data= request.get_json()
        user_id = data['user_id']
        weight = data['weight']
        try :
            user_id = int(user_id)
            weight = float(weight)
        except Exception as e:
            return jsonify({'error': 'Invalid JSON payload'}), 400
        current_datetime = datetime.now()
        date_of_measure = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
        
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO weight (user_id, weight, Date_of_Measure) VALUES (%s, %s, %s)',
                       (user_id, weight, date_of_measure))
        except Exception as e:
            print('Error inserting weight data:', e)
            return jsonify({'error': 'Hey bruto, mira el problema está en el query'}), 500
        cursor.close()
        conn.commit()

        return jsonify({'message': 'Weight data inserted successfully'}), 201
    # except Exception as e:
    #     print('Error inserting weight data:', e)
    #     return jsonify({'error': 'Internal server error'}), 500

# ... Existing routes and functions ...

if __name__ == '_main_':
    app.run(debug=True)