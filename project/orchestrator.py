"""
Resume Analysis Orchestrator

This module coordinates the entire resume analysis pipeline, including:
- Document parsing and text extraction
- Skill extraction and matching
- Semantic similarity analysis
- Topic modeling and feedback generation
"""

import logging
from typing import Dict, Any, Tuple, Optional
from .nlp.parsers.pdf_parser import extract_all_data
from .nlp.analysis.topic_modeler import find_topics
from .nlp.analysis.feedback_generator import generate_resume_tips
from .nlp.analysis.text_analyzer import extract_key_concepts, analyze_sentiment
from .nlp.utils.skill_graph import build_skill_network
from .nlp.utils.skill_db import SKILLS_DB

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from sentence_transformers import SentenceTransformer, util
    import spacy
    from spacy.matcher import PhraseMatcher
    
    # Load models once
    nlp = spacy.load("en_core_web_sm")
    similarity_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Initialize the PhraseMatcher for high-accuracy skill extraction
    skill_matcher = PhraseMatcher(nlp.vocab, attr='LOWER')
    # Create spaCy doc objects for each skill in the database for efficient matching
    skill_patterns = [nlp(skill) for skill in SKILLS_DB]
    skill_matcher.add("SKILL_MATCHER", skill_patterns)
    
    MODELS_LOADED = True
    logger.info("NLP models loaded successfully")
    
except Exception as e:
    logger.error(f"Failed to load NLP models: {e}")
    MODELS_LOADED = False
    nlp = None
    similarity_model = None
    skill_matcher = None


def extract_skills(text: str) -> list:
    """
    Extracts skills using spaCy's high-accuracy PhraseMatcher.
    
    Args:
        text (str): Input text to extract skills from
        
    Returns:
        list: Sorted list of found skills
    """
    if not MODELS_LOADED or not text:
        return []
    
    try:
        doc = nlp(text)
        found_skills = set()
        
        # Run the matcher over the document
        matches = skill_matcher(doc)
        
        # For each match, get the original text and add it to our set
        for match_id, start, end in matches:
            skill = doc[start:end].text
            found_skills.add(skill)
                
        return sorted(list(found_skills))
    except Exception as e:
        logger.error(f"Error extracting skills: {e}")
        return []


def calculate_similarity(resume_text: str, jd_text: str) -> float:
    """
    Calculate semantic similarity between resume and job description.
    
    Args:
        resume_text (str): Resume text content
        jd_text (str): Job description text
        
    Returns:
        float: Similarity score (0-100)
    """
    if not MODELS_LOADED or not resume_text or not jd_text:
        return 0.0
    
    try:
        resume_embedding = similarity_model.encode(resume_text, convert_to_tensor=True)
        jd_embedding = similarity_model.encode(jd_text, convert_to_tensor=True)
        cosine_score = util.cos_sim(resume_embedding, jd_embedding)
        return round(cosine_score.item() * 100, 2)
    except Exception as e:
        logger.error(f"Error calculating similarity: {e}")
        return 0.0


def analyze_resume(file_stream, jd_text: str, filename: str) -> Dict[str, Any]:
    """
    The main orchestration pipeline for a deep resume analysis.
    
    Args:
        file_stream: File stream object
        jd_text (str): Job description text
        filename (str): Name of the uploaded file
        
    Returns:
        Dict[str, Any]: Analysis results or error information
    """
    try:
        # STAGE 1: Advanced Positional Parsing
        logger.info(f"Starting analysis for file: {filename}")
        basic_info, resume_text = extract_all_data(file_stream, filename)
        
        if not resume_text:
            return {"error": "Could not extract text from the document."}

        # STAGE 2: Core Analysis using the PhraseMatcher-based function
        logger.info("Extracting skills from resume and job description")
        resume_skills = extract_skills(resume_text)
        jd_skills = extract_skills(jd_text)
        
        # Calculate similarity score
        similarity_score = calculate_similarity(resume_text, jd_text)

        # STAGE 3: Deeper AI Analysis
        logger.info("Performing advanced text analysis")
        experience_topics = find_topics(resume_text)
        key_concepts = extract_key_concepts(resume_text)
        sentiment, sentiment_desc = analyze_sentiment(resume_text)
        
        # Build skill network
        skill_network = build_skill_network(resume_skills)

        # STAGE 4: Feedback Generation
        logger.info("Generating feedback and recommendations")
        missing_skills = sorted(list(set(jd_skills) - set(resume_skills)))
        tips = generate_resume_tips(resume_text, basic_info)
        
        # STAGE 5: Aggregate All Results
        results = {
            "basic_info": basic_info,
            "similarity_score": similarity_score,
            "resume_skills": resume_skills,
            "missing_skills": missing_skills,
            "experience_topics": experience_topics,
            "key_concepts": key_concepts,
            "sentiment": {"label": sentiment, "description": sentiment_desc},
            "skill_network": skill_network,
            "feedback_tips": tips
        }
        
        logger.info(f"Analysis completed successfully for {filename}")
        return results
        
    except Exception as e:
        logger.error(f"Error during resume analysis: {e}")
        return {"error": f"Analysis failed: {str(e)}"}


def get_analysis_status() -> Dict[str, Any]:
    """
    Get the current status of the analysis system.
    
    Returns:
        Dict[str, Any]: Status information
    """
    return {
        "models_loaded": MODELS_LOADED,
        "nlp_model": "en_core_web_sm" if nlp else None,
        "similarity_model": "all-MiniLM-L6-v2" if similarity_model else None,
        "skills_database_size": len(SKILLS_DB) if SKILLS_DB else 0
    }