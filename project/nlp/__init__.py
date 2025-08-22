"""
Natural Language Processing Module

This module provides comprehensive NLP capabilities for resume analysis:
- Document parsing and text extraction
- Text analysis and sentiment detection
- Topic modeling and skill extraction
- Feedback generation and recommendations
"""

from . import parsers
from . import analysis
from . import utils

__all__ = ['parsers', 'analysis', 'utils']
