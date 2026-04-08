import re

# Simple sets of words for demonstration.
# In a real production app, this would be backed by a strong AI service or comprehensive list.

BANNED_WORDS = {"spam", "scam", "phishing"}
SENSITIVE_WORDS = {"hate", "kill", "murder", "abuse", "ugly", "idiot"}

def mask_sensitive_words(text: str) -> str:
    """Masks sensitive words with asterisks."""
    if not text:
        return text
        
    for word in SENSITIVE_WORDS:
        # Case insensitive replacement
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        # We mask the word but leave first letter and last letter if we wanted, or just full mask
        text = pattern.sub("****", text)
        
    return text

def contains_banned_words(text: str) -> bool:
    """Checks if the text contains strictly banned words."""
    if not text:
        return False
        
    text_lower = text.lower()
    for word in BANNED_WORDS:
        if word in text_lower:
            return True
            
    return False

def moderate_content(text: str) -> str:
    """
    Main moderation pipeline.
    Raises ValueError if banned content is found, otherwise returns masked text.
    """
    if contains_banned_words(text):
        raise ValueError("Content violates community guidelines and is blocked.")
    return mask_sensitive_words(text)
