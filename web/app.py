from flask import Flask
from configuration import Config
from web.blueprints_dashboard import dashboard_bp
from web.blueprints_api import api_bp

def create_app(config: Config):
    app = Flask(__name__, static_folder="../static", template_folder="../template")
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(api_bp, url_prefix = '/api')
    app.config['JSON_SORT_KEYS'] = False
    return app


