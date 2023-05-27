from flask import Flask, jsonify, request
import psycopg2

app = Flask(__name__)

# PostgreSQL database configuration
conn = psycopg2.connect(
    host='dpg-chlrr4fdvk4sq14sv42g-a.oregon-postgres.render.com',
    database='pandafit',
    user='pandafit_user',
    password='87juV5ghHEfCQxcHSUddSMx6fmjTdrDi'
)

# Retrieve all users
@app.route('/users', methods=['GET'])
def get_users():
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users')
        rows = cursor.fetchall()
        cursor.close()
        users = []
        for row in rows:
            user = {
                'userid': row[0],
                'username': row[1],
                'password': row[2],
                'role': row[3],
                'created_at': row[4]
            }
            users.append(user)
        return jsonify(users)
    except Exception as e:
        print('Database error:', e)
        return jsonify({'error': 'Internal server error'}), 500

# Create a new user
@app.route('/users', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        username = data['username']
        password = data['password']
        role = data['role']
        cursor = conn.cursor()
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

# Retrieve a specific user by ID
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE userid = %s', (user_id,))
        row = cursor.fetchone()
        cursor.close()
        if row is None:
            return jsonify({'error': 'User not found'}), 404
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

# Update a user
@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        data = request.get_json()
        username = data['username']
        password = data['password']
        role = data['role']
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET username = %s, password = %s, role = %s WHERE userid = %s RETURNING *',
                       (username, password, role, user_id))
        row = cursor.fetchone()
        cursor.close()
        if row is None:
            return jsonify({'error': 'User not found'}), 404
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

# Delete a user
@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE userid = %s RETURNING *', (user_id,))
        row = cursor.fetchone()
        cursor.close()
        if row is None:
            return jsonify({'error': 'User not found'}), 404
        return '', 204
    except Exception as e:
        print('Database error:', e)
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)
