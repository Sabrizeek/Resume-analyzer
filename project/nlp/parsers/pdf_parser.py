import pdfplumber
import re

def parse_name_from_layout(page):
    """
    Finds the name by looking for the largest text at the top of the page.
    This is the most reliable method.
    """
    # Focus on the top 20% of the page
    top_of_page_chars = [char for char in page.chars if char['top'] < page.height * 0.20]
    if not top_of_page_chars:
        return None
    
    # Find the largest font size in that area
    largest_size = max(char['size'] for char in top_of_page_chars)
    
    # Get all text with that largest font size, allowing for minor floating point differences
    name_chars = [char['text'] for char in top_of_page_chars if abs(char['size'] - largest_size) < 0.1]
    name = "".join(name_chars).strip()

    # A final check to ensure it's a plausible name
    if len(name.split()) > 1 and len(name.split()) < 4:
        return name
    return None

def parse_contact_info(full_text):
    """Finds the first valid email and phone number."""
    email = "Not Found"
    phone = "Not Found"
    
    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', full_text)
    if email_match:
        email = email_match.group(0)

    phone_match = re.search(r'(?:\+\d{1,3}[-.\s]?)?(?:\(?\d{2,4}\)?[-.\s]?)?\d{3,4}[-.\s]?\d{3,4}', full_text)
    if phone_match and sum(c.isdigit() for c in phone_match.group(0)) >= 9:
        phone = phone_match.group(0).strip()
        
    return email, phone

def parse_name_from_filename(filename):
    """Cleans a filename to extract a plausible name as a fallback."""
    name = re.sub(r'\.(pdf|docx|txt)$', '', filename, flags=re.IGNORECASE)
    name = re.sub(r'(resume|cv)[\s_-]*', '', name, flags=re.IGNORECASE)
    name = re.sub(r'[-_]', ' ', name)
    return name.strip().title()

def extract_all_data(file_stream, filename):
    """
    Main function to extract structured data from a PDF using positional info.
    """
    with pdfplumber.open(file_stream) as pdf:
        first_page = pdf.pages[0]
        full_text = "\n".join([page.extract_text(x_tolerance=1, y_tolerance=1) for page in pdf.pages])
        page_count = len(pdf.pages)
        
        # --- New, More Reliable Extraction Pipeline ---
        # 1. Try the most accurate method first: layout analysis
        name = parse_name_from_layout(first_page)
        
        # 2. If layout analysis fails, fall back to the filename
        if not name:
            name = parse_name_from_filename(filename)
        
        # 3. Get contact info from the full text
        email, phone = parse_contact_info(full_text)

        basic_info = {
            "name": name,
            "email": email,
            "phone": phone,
            "pages": page_count
        }
        
        return basic_info, full_text