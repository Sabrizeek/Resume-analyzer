"""
Main Application Routes

This module contains the main application routes for the AI Resume Analyzer.
"""

import logging
import os
from flask import Blueprint, render_template, request, jsonify, current_app
from werkzeug.utils import secure_filename
from project.orchestrator import analyze_resume, get_analysis_status

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
main = Blueprint('main', __name__)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'docx', 'doc'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_file_size(file):
    """Check if the file size is within limits."""
    try:
        file.seek(0, 2)  # Seek to end
        size = file.tell()
        file.seek(0)  # Reset to beginning
        return size <= MAX_FILE_SIZE
    except Exception as e:
        logger.error(f"Error checking file size: {e}")
        return False


@main.route('/')
def index():
    """Render the main application page."""
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering index page: {e}")
        return "Internal Server Error", 500


@main.route('/api/analyze', methods=['POST'])
def analyze():
    """
    API endpoint for resume analysis.
    
    Expected form data:
    - resume: File upload (PDF, TXT, DOCX)
    - jd: Job description text
    """
    try:
        # Validate file upload
        if 'resume' not in request.files:
            return jsonify({
                "error": "No resume file provided.",
                "code": "MISSING_FILE"
            }), 400
        
        resume_file = request.files['resume']
        if resume_file.filename == '':
            return jsonify({
                "error": "No resume file selected.",
                "code": "EMPTY_FILENAME"
            }), 400
        
        # Validate file extension
        if not allowed_file(resume_file.filename):
            return jsonify({
                "error": f"Unsupported file format. Allowed formats: {', '.join(ALLOWED_EXTENSIONS)}",
                "code": "INVALID_FORMAT"
            }), 400
        
        # Validate file size
        if not validate_file_size(resume_file):
            return jsonify({
                "error": f"File size exceeds maximum limit of {MAX_FILE_SIZE // (1024*1024)}MB",
                "code": "FILE_TOO_LARGE"
            }), 400
        
        # Validate job description
        jd_text = request.form.get('jd', '').strip()
        if not jd_text:
            return jsonify({
                "error": "Job description is required.",
                "code": "MISSING_JD"
            }), 400
        
        if len(jd_text) < 50:
            return jsonify({
                "error": "Job description must be at least 50 characters long.",
                "code": "JD_TOO_SHORT"
            }), 400
        
        # Secure filename and log analysis start
        filename = secure_filename(resume_file.filename)
        logger.info(f"Starting analysis for file: {filename}")
        
        # Perform analysis
        results = analyze_resume(resume_file.stream, jd_text, filename)
        
        # Check for analysis errors
        if "error" in results:
            logger.error(f"Analysis failed for {filename}: {results['error']}")
            return jsonify({
                "error": results["error"],
                "code": "ANALYSIS_FAILED"
            }), 500
        
        # Log successful analysis
        logger.info(f"Analysis completed successfully for {filename}")
        
        # Add metadata to response
        results["metadata"] = {
            "filename": filename,
            "file_size": resume_file.content_length if hasattr(resume_file, 'content_length') else "Unknown",
            "analysis_timestamp": "2024-08-22T00:00:00Z"  # You can add actual timestamp logic
        }
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Unexpected error during analysis: {e}")
        return jsonify({
            "error": "An unexpected error occurred during analysis.",
            "code": "INTERNAL_ERROR",
            "details": str(e) if current_app.debug else None
        }), 500


@main.route('/api/status')
def status():
    """Get the current status of the analysis system."""
    try:
        status_info = get_analysis_status()
        return jsonify({
            "status": "operational",
            "system_info": status_info,
            "supported_formats": list(ALLOWED_EXTENSIONS),
            "max_file_size_mb": MAX_FILE_SIZE // (1024*1024)
        })
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


@main.route('/api/health')
def health():
    """Simple health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "AI Resume Analyzer",
        "version": "1.0.0"
    })


@main.errorhandler(413)
def too_large(e):
    """Handle file too large errors."""
    return jsonify({
        "error": "File size exceeds maximum limit.",
        "code": "FILE_TOO_LARGE"
    }), 413


@main.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    return jsonify({
        "error": "Endpoint not found.",
        "code": "NOT_FOUND"
    }), 404


@main.errorhandler(500)
def internal_error(e):
    """Handle internal server errors."""
    logger.error(f"Internal server error: {e}")
    return jsonify({
        "error": "Internal server error occurred.",
        "code": "INTERNAL_ERROR"
    }), 500