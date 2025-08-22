"""
AI Resume Analyzer Application Factory

This module creates and configures the Flask application with all necessary
extensions, blueprints, and error handlers.
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify
from config import Config

def create_app(config_class=Config):
    """
    Application factory function to create and configure the Flask app.
    
    Args:
        config_class: Configuration class to use
        
    Returns:
        Flask: Configured Flask application
    """
    # Create Flask app instance
    app = Flask(__name__, instance_relative_config=True)
    
    # Load configuration
    app.config.from_object(config_class)
    
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError as e:
        app.logger.warning(f"Could not create instance folder: {e}")
    
    # Configure logging
    if not app.debug and not app.testing:
        # Production logging
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = RotatingFileHandler(
            'logs/resume_analyzer.log', 
            maxBytes=10240000, 
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('AI Resume Analyzer startup')
    
    # Register blueprints
    try:
        from .main.routes import main as main_blueprint
        app.register_blueprint(main_blueprint)
        app.logger.info("Main blueprint registered successfully")
    except Exception as e:
        app.logger.error(f"Failed to register main blueprint: {e}")
        raise
    
    # Register error handlers
    register_error_handlers(app)
    
    # Health check route
    @app.route('/health')
    def health_check():
        """Basic health check endpoint."""
        return jsonify({
            "status": "healthy",
            "service": "AI Resume Analyzer",
            "version": "1.0.0"
        })
    
    app.logger.info("Application factory completed successfully")
    return app


def register_error_handlers(app):
    """Register custom error handlers for the application."""
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 errors."""
        return jsonify({
            "error": "Resource not found",
            "code": "NOT_FOUND",
            "message": "The requested resource was not found on this server."
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        app.logger.error(f"Internal server error: {error}")
        return jsonify({
            "error": "Internal server error",
            "code": "INTERNAL_ERROR",
            "message": "An unexpected error occurred. Please try again later."
        }), 500
    
    @app.errorhandler(413)
    def too_large_error(error):
        """Handle file too large errors."""
        return jsonify({
            "error": "File too large",
            "code": "FILE_TOO_LARGE",
            "message": "The uploaded file exceeds the maximum allowed size."
        }), 413
    
    @app.errorhandler(400)
    def bad_request_error(error):
        """Handle 400 errors."""
        return jsonify({
            "error": "Bad request",
            "code": "BAD_REQUEST",
            "message": "The request could not be processed due to invalid data."
        }), 400
    
    app.logger.info("Error handlers registered successfully")