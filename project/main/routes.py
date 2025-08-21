from flask import Blueprint, render_template, request, jsonify
from project import orchestrator

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/api/analyze', methods=['POST'])
def analyze():
    if 'resume' not in request.files or request.files['resume'].filename == '':
        return jsonify({"error": "No resume file provided."}), 400
    
    jd_text = request.form.get('jd', '').strip()
    if not jd_text:
        return jsonify({"error": "Job description is empty."}), 400

    resume_file = request.files['resume']
    resume_filename = resume_file.filename
    
    # Pass the file stream and filename to the orchestrator
    results = orchestrator.analyze_resume(resume_file.stream, jd_text, resume_filename)
    
    if "error" in results:
         return jsonify(results), 500

    return jsonify(results)