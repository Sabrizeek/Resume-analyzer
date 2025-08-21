from .nlp.parsers import pdf_parser
from .nlp.analysis import topic_modeler, feedback_generator, text_analyzer
from .nlp.utils import skill_graph
from .nlp.utils.skill_db import SKILLS_DB
from sentence_transformers import SentenceTransformer, util
import spacy
from spacy.matcher import PhraseMatcher # <-- Import the PhraseMatcher

# Load models once
try:
    nlp = spacy.load("en_core_web_sm")
    similarity_model = SentenceTransformer('all-MiniLM-L6-v2')
except Exception as e:
    raise RuntimeError(f"Failed to load NLP models: {e}")

# --- NEW: Initialize the PhraseMatcher for high-accuracy skill extraction ---
skill_matcher = PhraseMatcher(nlp.vocab, attr='LOWER')
# Create spaCy doc objects for each skill in the database for efficient matching
skill_patterns = [nlp(skill) for skill in SKILLS_DB]
skill_matcher.add("SKILL_MATCHER", skill_patterns)

def extract_skills(text):
    """
    Extracts skills using spaCy's high-accuracy PhraseMatcher.
    """
    doc = nlp(text)
    found_skills = set()
    
    # Run the matcher over the document
    matches = skill_matcher(doc)
    
    # For each match, get the original text and add it to our set
    for match_id, start, end in matches:
        skill = doc[start:end].text
        found_skills.add(skill)
            
    return sorted(list(found_skills))

def analyze_resume(file_stream, jd_text, filename):
    """
    The main orchestration pipeline for a deep resume analysis.
    """
    # STAGE 1: Advanced Positional Parsing
    basic_info, resume_text = pdf_parser.extract_all_data(file_stream, filename)
    if not resume_text:
        return {"error": "Could not extract text from the document."}

    # STAGE 2: Core Analysis using the NEW PhraseMatcher-based function
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text)

    # --- DEBUGGING TOOL (Optional) ---
    # Uncomment the following lines to see exactly what skills are being extracted in your terminal
    # print("----------- DEBUGGING -----------")
    # print(f"Skills found in RESUME: {resume_skills}")
    # print(f"Skills found in JOB DESC: {jd_skills}")
    # print("-----------------------------")
    
    similarity_score = 0
    if resume_text and jd_text:
        resume_embedding = similarity_model.encode(resume_text, convert_to_tensor=True)
        jd_embedding = similarity_model.encode(jd_text, convert_to_tensor=True)
        cosine_score = util.cos_sim(resume_embedding, jd_embedding)
        similarity_score = round(cosine_score.item() * 100, 2)

    # STAGE 3: Deeper AI Analysis
    experience_topics = topic_modeler.find_topics(resume_text)
    key_concepts = text_analyzer.extract_key_concepts(resume_text)
    sentiment, sentiment_desc = text_analyzer.analyze_sentiment(resume_text)
    
    skill_network = skill_graph.build_skill_network(resume_skills)

    # STAGE 4: Feedback Generation
    missing_skills = sorted(list(set(jd_skills) - set(resume_skills)))
    tips = feedback_generator.generate_resume_tips(resume_text, basic_info)
    
    # STAGE 5: Aggregate All Results
    return {
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