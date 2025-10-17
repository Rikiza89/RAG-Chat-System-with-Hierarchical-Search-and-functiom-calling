def json_prettify(data):
    """
    Prettify JSON data
    
    Args:
        data: String or dict to format
    
    Returns:
        Prettified JSON string
    """
    import json
    if isinstance(data, str):
        data = json.loads(data)
    return json.dumps(data, indent=2, ensure_ascii=False)

def run(text, style="upper"):
    """
    Format text according to style
    
    Args:
        text: Text to format
        style: One of 'upper', 'lower', 'title', 'capitalize'
    
    Returns:
        Formatted text
    """
    styles = {
        "upper": str.upper,
        "lower": str.lower,
        "title": str.title,
        "capitalize": str.capitalize
    }
    
    formatter = styles.get(style, str.upper)
    return formatter(text)
