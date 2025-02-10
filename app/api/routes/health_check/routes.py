from flask import Blueprint, jsonify

health_check_blueprint = Blueprint('health_check', __name__)

@health_check_blueprint.route('/health_check', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'}), 200