from flask import Flask, jsonify

from api.routes.users.routes import users_blueprint

def create_app() -> Flask:
    app = Flask(__name__)
    return app

def register_blueprints(app: Flask):
    app.register_blueprint(users_blueprint)
    
app = create_app()
register_blueprints(app)