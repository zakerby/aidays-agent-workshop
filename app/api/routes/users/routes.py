from flask import Blueprint, jsonify, request

users_blueprint = Blueprint('users', __name__)

# Mock database (replace with actual database in production)
users = [
    {
        'id': 1,
        'name': 'John Doe',
        'email': ''
    },
]

@users_blueprint.route('/users', methods=['GET'])
def get_users():
    return jsonify(users), 200

@users_blueprint.route('/user', methods=['POST'])
def create_user():
    if not request.json:
        return jsonify({'error': 'No request body'}), 400
    
    data = request.get_json()
    
    if 'name' not in data:
        return jsonify({'error': 'Name is required'}), 400
    if 'email' not in data:
        return jsonify({'error': 'Email is required'}), 400
    
    new_user = {
        'id': len(users) + 1,
        'name': data['name'],
        'email': data['email']
    }
    users.append(new_user)
    return jsonify(new_user), 201
    