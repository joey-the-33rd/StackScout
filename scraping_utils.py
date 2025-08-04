"""
Utility functions for safe web scraping operations.
Addresses the three main issues identified in the codebase.
"""

from bs4 import BeautifulSoup, Tag
from typing import Optional, List, Any, Union
import logging

logger = logging.getLogger("stackscout_web")

def safe_get_text(element: Any, default: str = "N/A") -> str:
    """
    Safely extract text from a BeautifulSoup element.
    
    Args:
        element: The BeautifulSoup element to extract text from
        default: Default value to return if text cannot be extracted
        
    Returns:
        The extracted text or the default value
    """
    if element is None:
        return default
    
    if isinstance(element, Tag):
        if hasattr(element, 'get_text'):
            text = element.get_text(strip=True)
            return text if text else default
    
    return str(element).strip() if str(element).strip() else default

def safe_get_attribute(element: Any, attribute: str, default: Optional[str] = None) -> Optional[str]:
    """
    Safely get an attribute from a BeautifulSoup element.
    
    Args:
        element: The BeautifulSoup element
        attribute: The attribute name to retrieve
        default: Default value to return if attribute doesn't exist
        
    Returns:
        The attribute value or the default value
    """
    if element is None or not isinstance(element, Tag):
        return default
    
    if hasattr(element, 'get'):
        value = element.get(attribute)
        if isinstance(value, list):
            # Handle case where attribute returns a list (e.g., class attribute)
            return ' '.join(value) if value else default
        return str(value) if value is not None else default
    
    return default

def extract_job_field(job: Any, selectors: List[str], attribute: Optional[str] = None, default: str = "N/A") -> str:
    """
    Unified job field extraction with multiple fallback selectors.
    
    Args:
        job: The job element to extract from
        selectors: List of CSS selectors to try
        attribute: Optional attribute to extract instead of text
        default: Default value if nothing found
        
    Returns:
        The extracted value or default
    """
    if job is None or not isinstance(job, Tag):
        return default
    
    for selector in selectors:
        element = job.select_one(selector)
        if element:
            if attribute:
                value = safe_get_attribute(element, attribute, default)
                if value is None:
                    value = default
            else:
                value = safe_get_text(element, default)
            
            if value != default:
                return value
    
    return default

def safe_find_element(job: Any, selectors: List[str]) -> Optional[Tag]:
    """
    Safely find an element using multiple fallback selectors.
    
    Args:
        job: The parent element to search in
        selectors: List of CSS selectors to try
        
    Returns:
        The found element or None
    """
    if job is None or not isinstance(job, Tag):
        return None
    
    for selector in selectors:
        element = job.select_one(selector)
        if element:
            return element
    
    return None

def extract_tags(job: Any, tag_selector: str, class_name: str = "tag") -> List[str]:
    """
    Safely extract tags from job listings.
    
    Args:
        job: The job element
        tag_selector: CSS selector for tag elements
        class_name: Optional class name for tag elements
        
    Returns:
        List of extracted tag texts
    """
    if job is None or not isinstance(job, Tag):
        return []
    
    tag_elements = job.find_all(tag_selector, class_=class_name)
    tags = []
    
    for tag_elem in tag_elements:
        text = safe_get_text(tag_elem)
        if text and text != "N/A":
            tags.append(text)
    
    return tags
