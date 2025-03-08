"""
String processing utilities for the Blood Bond Enhanced Tools.

This module provides various string manipulation and comparison functions 
used throughout the application for tasks such as:
- String similarity calculation
- Capitalization handling
- Text normalization
- String pattern matching
"""

import re
import difflib
from typing import List, Dict, Tuple, Optional, Union, Callable
import unicodedata


def calculate_similarity(str1: str, str2: str) -> float:
    """
    Calculate similarity ratio between two strings using difflib's SequenceMatcher.
    
    Args:
        str1: First string to compare
        str2: Second string to compare
        
    Returns:
        Similarity ratio between 0.0 and 1.0 where 1.0 means identical strings
    """
    if not str1 and not str2:
        return 1.0
    if not str1 or not str2:
        return 0.0
    
    # Normalize strings for comparison
    norm_str1 = normalize_string(str1)
    norm_str2 = normalize_string(str2)
    
    return difflib.SequenceMatcher(None, norm_str1, norm_str2).ratio()


def find_best_match(query: str, candidates: List[str], 
                   threshold: float = 0.7) -> Optional[Tuple[str, float]]:
    """
    Find the best matching string from a list of candidates using string similarity.
    
    Args:
        query: The string to match
        candidates: List of potential matching strings
        threshold: Minimum similarity threshold to consider a match (0.0 to 1.0)
        
    Returns:
        Tuple of (best_match, similarity_score) or None if no match above threshold
    """
    if not query or not candidates:
        return None
    
    best_match = None
    best_score = 0.0
    
    for candidate in candidates:
        score = calculate_similarity(query, candidate)
        if score > best_score:
            best_score = score
            best_match = candidate
    
    if best_score >= threshold:
        return (best_match, best_score)
    
    return None


def normalize_string(text: str) -> str:
    """
    Normalize a string by converting to lowercase, removing extra whitespace,
    and removing special characters.
    
    Args:
        text: Input string to normalize
        
    Returns:
        Normalized string
    """
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove extra whitespace
    text = " ".join(text.split())
    
    # Remove punctuation and normalize unicode
    text = unicodedata.normalize('NFKD', text)
    text = re.sub(r'[^\w\s]', '', text)
    
    return text


def capitalize_properly(text: str) -> str:
    """
    Capitalize a string properly for spell names and descriptions.
    
    Capitalizes the first letter of each word except for certain
    articles, conjunctions, and prepositions unless they're the
    first word of the string.
    
    Args:
        text: Input string to capitalize
        
    Returns:
        Properly capitalized string
    """
    if not text:
        return ""
    
    # List of words to keep lowercase unless they start the string
    lowercase_words = {'a', 'an', 'the', 'and', 'but', 'or', 'for', 'nor',
                      'on', 'at', 'to', 'from', 'by', 'with', 'in', 'of'}
    
    words = text.split()
    result = []
    
    for i, word in enumerate(words):
        if i == 0 or word.lower() not in lowercase_words:
            result.append(word.capitalize())
        else:
            result.append(word.lower())
    
    return " ".join(result)


def format_spell_name(effect: str, element: str) -> str:
    """
    Format a spell name from effect and element.
    
    Args:
        effect: The spell effect (e.g., "create", "damage")
        element: The spell element (e.g., "fire", "water")
        
    Returns:
        Formatted spell name (e.g., "Create Fire", "Water Damage")
    """
    if not effect or not element:
        return ""
    
    # Clean up inputs
    effect = effect.strip()
    element = element.strip()
    
    # Determine order - some effects sound better before the element, others after
    effects_before = {"create", "summon", "conjure", "form"}
    
    if effect.lower() in effects_before:
        spell_name = f"{effect} {element}"
    else:
        spell_name = f"{element} {effect}"
    
    return capitalize_properly(spell_name)


def match_pattern(text: str, patterns: Dict[str, List[str]]) -> Optional[str]:
    """
    Match a text against a dictionary of regex patterns.
    
    Args:
        text: Text to match
        patterns: Dictionary where keys are category names and values are lists of regex patterns
        
    Returns:
        The matching category name or None if no match found
    """
    if not text or not patterns:
        return None
    
    normalized_text = normalize_string(text)
    
    for category, pattern_list in patterns.items():
        for pattern in pattern_list:
            if re.search(pattern, normalized_text, re.IGNORECASE):
                return category
    
    return None


def find_keywords(text: str, keywords: Dict[str, List[str]]) -> List[str]:
    """
    Find all categories whose keywords appear in the given text.
    
    Args:
        text: Text to search for keywords
        keywords: Dictionary mapping categories to lists of keywords
        
    Returns:
        List of categories whose keywords were found in the text
    """
    if not text or not keywords:
        return []
    
    normalized_text = normalize_string(text)
    matches = []
    
    for category, keyword_list in keywords.items():
        for keyword in keyword_list:
            if normalize_string(keyword) in normalized_text:
                matches.append(category)
                break
    
    return matches


def extract_numeric_value(text: str) -> Optional[int]:
    """
    Extract a numeric value from text.
    
    Args:
        text: Text that may contain numeric values
        
    Returns:
        Extracted numeric value or None if no number found
    """
    if not text:
        return None
    
    # Try to find a number in the text
    numbers = re.findall(r'\b\d+\b', text)
    
    if numbers:
        return int(numbers[0])
    
    # Check for number words
    number_words = {
        'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
        'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
        'twenty': 20, 'thirty': 30, 'forty': 40, 'fifty': 50,
        'hundred': 100, 'thousand': 1000
    }
    
    normalized_text = normalize_string(text)
    for word, value in number_words.items():
        if word in normalized_text:
            return value
    
    return None

