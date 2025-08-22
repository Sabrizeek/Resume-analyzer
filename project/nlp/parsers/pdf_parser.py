"""
Advanced Document Parser

This module provides robust parsing capabilities for various document formats:
- PDF files using pdfplumber
- Text files
- Enhanced text extraction and analysis
"""

import logging
import re
import io
from typing import Tuple, Dict, Any, Optional
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    logger.warning("pdfplumber not available. PDF parsing will be disabled.")
    PDFPLUMBER_AVAILABLE = False

try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    logger.warning("python-docx not available. DOCX parsing will be disabled.")
    DOCX_AVAILABLE = False


def parse_name_from_layout(page) -> Optional[str]:
    """
    Finds the name by looking for the largest text at the top of the page.
    This is the most reliable method for PDFs.
    
    Args:
        page: PDF page object from pdfplumber
        
    Returns:
        Optional[str]: Extracted name or None
    """
    try:
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
    except Exception as e:
        logger.warning(f"Error parsing name from layout: {e}")
        return None


def parse_contact_info(full_text: str) -> Tuple[str, str]:
    """
    Finds the first valid email and phone number in the text.
    
    Args:
        full_text (str): Text content to search
        
    Returns:
        Tuple[str, str]: (email, phone)
    """
    email = "Not Found"
    phone = "Not Found"
    
    try:
        # Enhanced email regex
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', full_text)
        if email_match:
            email = email_match.group(0)

        # Enhanced phone regex for various formats
        phone_patterns = [
            r'(?:\+\d{1,3}[-.\s]?)?(?:\(?\d{2,4}\)?[-.\s]?)?\d{3,4}[-.\s]?\d{3,4}',  # Standard format
            r'\(\d{3}\)\s*\d{3}-\d{4}',  # (123) 456-7890
            r'\d{3}-\d{3}-\d{4}',  # 123-456-7890
            r'\d{3}\.\d{3}\.\d{4}',  # 123.456.7890
        ]
        
        for pattern in phone_patterns:
            phone_match = re.search(pattern, full_text)
            if phone_match and sum(c.isdigit() for c in phone_match.group(0)) >= 9:
                phone = phone_match.group(0).strip()
                break
                
    except Exception as e:
        logger.warning(f"Error parsing contact info: {e}")
        
    return email, phone


def parse_name_from_filename(filename: str) -> str:
    """
    Cleans a filename to extract a plausible name as a fallback.
    
    Args:
        filename (str): Original filename
        
    Returns:
        str: Cleaned name
    """
    try:
        # Remove file extensions
        name = re.sub(r'\.(pdf|docx|txt|doc)$', '', filename, flags=re.IGNORECASE)
        # Remove common resume/CV prefixes
        name = re.sub(r'(resume|cv|curriculum|vitae)[\s_-]*', '', name, flags=re.IGNORECASE)
        # Replace underscores and hyphens with spaces
        name = re.sub(r'[-_]', ' ', name)
        # Clean up extra whitespace
        name = re.sub(r'\s+', ' ', name).strip()
        return name.title()
    except Exception as e:
        logger.warning(f"Error parsing name from filename: {e}")
        return "Unknown"


def extract_text_from_pdf(file_stream) -> Tuple[Dict[str, Any], str]:
    """
    Extract text and metadata from PDF files.
    
    Args:
        file_stream: PDF file stream
        
    Returns:
        Tuple[Dict[str, Any], str]: (basic_info, full_text)
    """
    if not PDFPLUMBER_AVAILABLE:
        raise ImportError("pdfplumber is required for PDF parsing")
    
    try:
        with pdfplumber.open(file_stream) as pdf:
            first_page = pdf.pages[0]
            full_text = "\n".join([
                page.extract_text(x_tolerance=1, y_tolerance=1) 
                for page in pdf.pages
            ])
            page_count = len(pdf.pages)
            
            # Try layout analysis first
            name = parse_name_from_layout(first_page)
            
            # Fallback to filename if layout analysis fails
            if not name:
                name = parse_name_from_filename("resume.pdf")  # Generic fallback
            
            # Extract contact information
            email, phone = parse_contact_info(full_text)
            
            basic_info = {
                "name": name,
                "email": email,
                "phone": phone,
                "pages": page_count,
                "format": "PDF"
            }
            
            return basic_info, full_text
            
    except Exception as e:
        logger.error(f"Error parsing PDF: {e}")
        raise


def extract_text_from_docx(file_stream) -> Tuple[Dict[str, Any], str]:
    """
    Extract text and metadata from DOCX files.
    
    Args:
        file_stream: DOCX file stream
        
    Returns:
        Tuple[Dict[str, Any], str]: (basic_info, full_text)
    """
    if not DOCX_AVAILABLE:
        raise ImportError("python-docx is required for DOCX parsing")
    
    try:
        doc = docx.Document(file_stream)
        full_text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        
        # Extract basic info (simplified for DOCX)
        basic_info = {
            "name": "Extracted from DOCX",
            "email": "Not Found",
            "phone": "Not Found",
            "pages": 1,  # DOCX doesn't have page concept
            "format": "DOCX"
        }
        
        return basic_info, full_text
        
    except Exception as e:
        logger.error(f"Error parsing DOCX: {e}")
        raise


def extract_text_from_txt(file_stream) -> Tuple[Dict[str, Any], str]:
    """
    Extract text from plain text files.
    
    Args:
        file_stream: Text file stream
        
    Returns:
        Tuple[Dict[str, Any], str]: (basic_info, full_text)
    """
    try:
        # Reset file pointer to beginning
        file_stream.seek(0)
        full_text = file_stream.read().decode('utf-8', errors='ignore')
        
        basic_info = {
            "name": "Extracted from TXT",
            "email": "Not Found",
            "phone": "Not Found",
            "pages": 1,
            "format": "TXT"
        }
        
        return basic_info, full_text
        
    except Exception as e:
        logger.error(f"Error parsing TXT: {e}")
        raise


def extract_all_data(file_stream, filename: str) -> Tuple[Dict[str, Any], str]:
    """
    Main function to extract structured data from various document formats.
    
    Args:
        file_stream: File stream object
        filename (str): Name of the uploaded file
        
    Returns:
        Tuple[Dict[str, Any], str]: (basic_info, full_text)
    """
    try:
        file_extension = Path(filename).suffix.lower()
        
        if file_extension == '.pdf':
            basic_info, full_text = extract_text_from_pdf(file_stream)
        elif file_extension == '.docx':
            basic_info, full_text = extract_text_from_docx(file_stream)
        elif file_extension == '.txt':
            basic_info, full_text = extract_text_from_txt(file_stream)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
        
        # Update name from filename if not already extracted
        if basic_info.get("name") in ["Extracted from DOCX", "Extracted from TXT"]:
            basic_info["name"] = parse_name_from_filename(filename)
        
        # Ensure we have valid text content
        if not full_text or len(full_text.strip()) < 50:
            raise ValueError("Document appears to be empty or contains insufficient text")
        
        logger.info(f"Successfully extracted data from {filename}")
        return basic_info, full_text
        
    except Exception as e:
        logger.error(f"Failed to extract data from {filename}: {e}")
        raise


def get_supported_formats() -> list:
    """
    Get list of supported file formats.
    
    Returns:
        list: Supported file extensions
    """
    formats = []
    if PDFPLUMBER_AVAILABLE:
        formats.append('.pdf')
    if DOCX_AVAILABLE:
        formats.append('.docx')
    formats.append('.txt')
    return formats