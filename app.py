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
            cursor.execute(
                'SELECT * FROM users WHERE username = %s', (username,))
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
        cursor.execute(
            'SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
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
def add_weight():
    try:
        data = request.get_json()
        user_id = data['user_id']
        weight = data['weight']
        current_datetime = datetime.now()
        date_of_measure = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

        cursor = conn.cursor()
        cursor.execute('INSERT INTO weight (user_id, weight, date_of_measure) VALUES (%s, %s, %s)',
                       (user_id, weight, date_of_measure))
        cursor.close()
        conn.commit()

        return jsonify({'message': 'Weight data inserted successfully'}), 201
    except Exception as e:
        print('Error inserting weight data:', e)
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/weight/<int:user_id>', methods=['GET'])
def get_weight(user_id):
    try:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT weight, date_of_measure FROM weight WHERE user_id = %s', (user_id,))
        rows = cursor.fetchall()
        cursor.close()

        if not rows:
            return jsonify({'message': 'No weight data found for the user'}), 404

        weight_data = []
        for row in rows:
            weight_data.append({
                'weight': row[0],
                'date_of_measure': row[1].strftime('%Y-%m-%d %H:%M:%S')
            })

        return jsonify(weight_data)
    except Exception as e:
        print('Error retrieving weight data:', e)
        return jsonify({'error': 'Internal server error'}), 500

# ... Existing routes and functions ...


if __name__ == '_main_':
    app.run(debug=True)
