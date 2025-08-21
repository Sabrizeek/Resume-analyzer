import spacy
from textblob import TextBlob
import re

nlp = spacy.load("en_core_web_sm")

def clean_text(text):
    """Adds spaces before capital letters to split run-on words."""
    return re.sub(r"(\w)([A-Z])", r"\1 \2", text)

def extract_key_concepts(text):
    """Extracts meaningful noun phrases and entities from the text with better filtering."""
    doc = nlp(clean_text(text))
    concepts = set()
    
    # Extract noun chunks (e.g., "web-based motorcycle and part management system")
    for chunk in doc.noun_chunks:
        # Filter out very short/long chunks and those that are just names or noisy
        if 1 < len(chunk.text.split()) < 6 and chunk.root.pos_ != 'PROPN':
            concepts.add(chunk.text.strip().title())
            
    # Extract named entities (e.g., organizations, products)
    for ent in doc.ents:
        if ent.label_ in ["ORG", "PRODUCT"] and len(ent.text.split()) < 5:
            concepts.add(ent.text.strip())
            
    return sorted(list(concepts), key=len, reverse=True)[:10]

def analyze_sentiment(text):
    """Analyzes the sentiment of the resume text."""
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    
    if polarity > 0.2:
        return "Very Positive", "The language used is highly positive and action-oriented."
    elif polarity > 0.05:
        return "Positive", "The language is generally positive and confident."
    else:
        return "Neutral", "The language is objective and neutral."