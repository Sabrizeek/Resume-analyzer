from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter
import re

def find_topics(text, num_themes=5):
    """
    Extracts key themes by finding the most common relevant words in the text.
    This is more reliable than LDA for short documents like resumes.
    """
    # Isolate text between experience and education/projects for better focus
    experience_text = text
    sections = ['work experience', 'experience', 'projects', 'education', 'skills']
    
    # Try to narrow down to the experience section
    for section in sections:
        match = re.search(rf'\b({section})\b', experience_text, re.IGNORECASE)
        if match:
            experience_text = experience_text[match.end():]
            break # Stop after the first major section header is found

    stop_words = set(stopwords.words('english'))
    # Add custom words to ignore that are common in resumes but not insightful
    custom_stopwords = {'responsibilities', 'company', 'ltd', 'sri', 'lanka', 'work', 'role', 'assisted', 'development', 'management'}
    stop_words.update(custom_stopwords)

    tokens = word_tokenize(experience_text.lower())
    
    # Use part-of-speech tagging to only keep nouns and adjectives
    # This is a placeholder for a more advanced implementation. For now, we filter with a basic list.
    filtered_words = [
        word for word in tokens 
        if word.isalpha() and word not in stop_words and len(word) > 3
    ]
    
    # Get the most common words
    most_common = Counter(filtered_words).most_common(num_themes)
    
    # Return just the words
    themes = [word.title() for word, freq in most_common]
    
    return themes