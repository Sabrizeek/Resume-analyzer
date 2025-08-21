import os
from flask import Flask
from config import Config

def create_app(config_class=Config):
    """
    Application factory function to create and configure the Flask app.
    """
    app = Flask(__name__, instance_relative_config=True)
    
    # Load configuration from the config object
    app.config.from_object(config_class)
    
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Register blueprints here
    from .main.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app