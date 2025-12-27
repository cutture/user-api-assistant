
import bleach

def sanitize_html(content: str) -> str:
    """
    Sanitizes HTML content to prevent XSS.
    Allows only a restricted set of tags and attributes safe for rendering.
    """
    if not content:
        return ""
        
    allowed_tags = [
        'a', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
        'h1', 'h2', 'h3', 'p', 'br', 'span'
    ]
    
    allowed_attributes = {
        'a': ['href', 'title', 'target'],
        'span': ['class'],
    }
    
    clean_content = bleach.clean(
        content,
        tags=allowed_tags,
        attributes=allowed_attributes,
        strip=True
    )
    
    return clean_content

def sanitize_filename(filename: str) -> str:
    """
    Removes dangerous characters from filenames.
    """
    import re
    # Keep only alphanumeric, dots, dashes, underscores
    cleaned = re.sub(r'[^a-zA-Z0-9._-]', '', filename)
    # Prevent directory traversal
    cleaned = cleaned.replace('..', '')
    return cleaned
