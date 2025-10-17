def run(text, max_length=100):
    """
    Summarize text to a maximum length
    
    Args:
        text: Text to summarize
        max_length: Maximum length of summary
    
    Returns:
        Summarized text
    """
    if len(text) <= max_length:
        return text
    
    # Simple truncation with ellipsis
    return text[:max_length-3].rsplit(' ', 1)[0] + '...'

def word_count(text):
    """Count words in text"""
    return len(text.split())
