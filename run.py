#!/usr/bin/env python3
"""
AI Resume Analyzer - Main Entry Point

This script starts the Flask application with proper configuration and error handling.
"""

import os
import sys
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def setup_environment():
    """Set up the environment for the application."""
    # Set default environment if not specified
    if 'FLASK_ENV' not in os.environ:
        os.environ['FLASK_ENV'] = 'development'
    
    # Set default debug mode
    if 'FLASK_DEBUG' not in os.environ:
        os.environ['FLASK_DEBUG'] = 'true' if os.environ['FLASK_ENV'] == 'development' else 'false'
    
    # Create necessary directories
    directories = ['logs', 'instance', 'uploads']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)

def setup_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/startup.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def check_dependencies():
    """Check if all required dependencies are available."""
    required_modules = [
        'flask',
        'spacy',
        'sentence_transformers',
        'pdfplumber'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"❌ Missing required modules: {', '.join(missing_modules)}")
        print("Please install them using: pip install -r requirements.txt")
        return False
    
    print("✅ All required dependencies are available")
    return True

def main():
    """Main application entry point."""
    try:
        # Setup environment
        setup_environment()
        setup_logging()
        
        logger = logging.getLogger(__name__)
        logger.info("Starting AI Resume Analyzer...")
        
        # Check dependencies
        if not check_dependencies():
            sys.exit(1)
        
        # Import and create app
        from project import create_app
        from config import get_config
        
        config = get_config()
        app = create_app(config)
        
        # Initialize configuration
        config.init_app(app)
        
        # Get configuration values
        host = os.environ.get('FLASK_HOST', '127.0.0.1')
        port = int(os.environ.get('FLASK_PORT', 5000))
        debug = app.config.get('DEBUG', False)
        
        logger.info(f"Application configured successfully")
        logger.info(f"Environment: {os.environ.get('FLASK_ENV', 'development')}")
        logger.info(f"Debug mode: {debug}")
        logger.info(f"Host: {host}")
        logger.info(f"Port: {port}")
        
        # Print startup message
        print("\n" + "="*60)
        print("🚀 AI Resume Analyzer Starting Up!")
        print("="*60)
        print(f"📍 Environment: {os.environ.get('FLASK_ENV', 'development')}")
        print(f"🔧 Debug Mode: {'Enabled' if debug else 'Disabled'}")
        print(f"🌐 Server: http://{host}:{port}")
        print(f"📊 Health Check: http://{host}:{port}/health")
        print(f"📈 Status: http://{host}:{port}/api/status")
        print("="*60)
        print("Press CTRL+C to stop the server")
        print("="*60 + "\n")
        
        # Run the application
        app.run(
            host=host,
            port=port,
            debug=debug,
            use_reloader=debug
        )
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all dependencies are installed:")
        print("pip install -r requirements.txt")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        logging.error(f"Application startup failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()