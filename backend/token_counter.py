"""
Token counting utilities for estimating OpenAI token usage
"""
import tiktoken

def estimate_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    """
    Estimate the number of tokens in a text string
    
    Args:
        text: The text to count tokens for
        model: The model name (default: gpt-4o-mini)
    
    Returns:
        Estimated token count
    """
    try:
        # Get the encoding for the model
        encoding = tiktoken.encoding_for_model(model)
        tokens = encoding.encode(text)
        return len(tokens)
    except Exception as e:
        # Fallback: rough estimate (1 token ≈ 4 characters)
        return len(text) // 4

def estimate_file_tokens(file_content: bytes, filename: str, model: str = "gpt-4o-mini") -> dict:
    """
    Estimate tokens for a file based on its content
    
    Args:
        file_content: The file content as bytes
        filename: The filename (to determine type)
        model: The model name
    
    Returns:
        Dict with token estimates and file info
    """
    # Try to decode as text
    try:
        if filename.endswith(('.csv', '.txt', '.json', '.md', '.py', '.js')):
            text = file_content.decode('utf-8')
            tokens = estimate_tokens(text, model)
            return {
                "tokens": tokens,
                "size_bytes": len(file_content),
                "size_kb": round(len(file_content) / 1024, 2),
                "estimated": False,
                "type": "text"
            }
    except:
        pass
    
    # For binary files or decode errors, use rough estimate
    # OpenAI processes files, so estimate based on size
    # Rough estimate: 1KB ≈ 250 tokens for text files
    size_kb = len(file_content) / 1024
    estimated_tokens = int(size_kb * 250)
    
    return {
        "tokens": estimated_tokens,
        "size_bytes": len(file_content),
        "size_kb": round(size_kb, 2),
        "estimated": True,
        "type": "binary"
    }

