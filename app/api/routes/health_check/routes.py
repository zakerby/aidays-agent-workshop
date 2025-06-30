from flask import Blueprint, jsonify,current_app
    
health_check_blueprint = Blueprint('health_check', __name__)

@health_check_blueprint.route('/health_check', methods=['GET'])
def health_check():
    if current_app.config["HEALTHY"]:
        current_app.logger.info("Healthcheck passed")
        return jsonify({'status': 'ok'}), 200
    else:
        current_app.logger.error("Healthcheck failed, service is unhealthy must be restarted")
        return jsonify({'status': 'unhealthy'}), 500

@health_check_blueprint.route("/fail")
def fail():
    current_app.config["HEALTHY"] = False
    return "Healthcheck will now fail", 200
