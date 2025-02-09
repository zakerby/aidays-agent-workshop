from flask import Flask, jsonify

def create__app() -> Flask:
    app = Flask(__name__)
    return app

def register_blueprints(app: Flask):
    app.register_blueprint()