from .nlp.parsers import pdf_parser
from .nlp.analysis import topic_modeler, feedback_generator, text_analyzer
from .nlp.utils import skill_graph
from sentence_transformers import SentenceTransformer, util
import spacy

# Load models once
try:
    nlp = spacy.load("en_core_web_sm")
    similarity_model = SentenceTransformer('all-MiniLM-L6-v2')
except Exception as e:
    raise RuntimeError(f"Failed to load NLP models: {e}")

SKILL_KEYWORDS = [
    'python', 'java', 'c++', 'sql', 'javascript', 'react', 'vue', 'aws', 'docker', 'git', 'flask', 
    'django', 'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'node.js', 'express.js',
    'mongodb', 'mysql', 'php', 'spring boot', 'kotlin'
]

def extract_skills(text):
    doc = nlp(text.lower())
    skills = [token.text for token in doc if token.text in SKILL_KEYWORDS]
    return list(set(skills))

def analyze_resume(file_stream, jd_text, filename):
    """
    The main orchestration pipeline for a deep resume analysis.
    """
    # STAGE 1: Advanced Positional Parsing
    basic_info, resume_text = pdf_parser.extract_all_data(file_stream, filename)
    if not resume_text:
        return {"error": "Could not extract text from the document."}

    # STAGE 2: Core Analysis
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text)
    
    similarity_score = 0
    if resume_text and jd_text:
        resume_embedding = similarity_model.encode(resume_text, convert_to_tensor=True)
        jd_embedding = similarity_model.encode(jd_text, convert_to_tensor=True)
        cosine_score = util.cos_sim(resume_embedding, jd_embedding)
        similarity_score = round(cosine_score.item() * 100, 2)

    # STAGE 3: Deeper AI Analysis (NEW)
    experience_topics = topic_modeler.find_topics(resume_text)
    key_concepts = text_analyzer.extract_key_concepts(resume_text)
    sentiment, sentiment_desc = text_analyzer.analyze_sentiment(resume_text)
    
    skill_network = skill_graph.build_skill_network(resume_skills)

    # STAGE 4: Feedback Generation
    missing_skills = list(set(jd_skills) - set(resume_skills))
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