def run(text, target_lang="en"):
    """
    Mock translation function (returns original text with language tag)
    
    Args:
        text: Text to translate
        target_lang: Target language code
    
    Returns:
        Translated text (mock)
    """
    # This is a mock - real translation would use a translation API
    return f"[{target_lang.upper()}] {text}"

def reverse_text(text):
    """Reverse the text"""
    return text[::-1]