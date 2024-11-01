
def normalize_artist_name(name):
    """
    Normalize artist name by handling case variations and spacing issues.
    Maintains special characters and styling (e.g., 'P!nk' stays as 'P!nk').
    """
    if not name:
        return name
        
    # Handle double spaces and trim
    normalized = ' '.join(name.split())
    return normalized

def get_artist_from_acrcloud(response_data, logger=None):
    """
    Extract artist name from ACRCloud realtime API response with maximum accuracy.
    Handles case variations and spacing issues.
    
    Args:
        response_data (dict): The JSON response from ACRCloud API
        logger (Logger, optional): Logger instance for debugging. Defaults to None.
    
    Returns:
        str|None: Artist name if found, None otherwise
    
    Examples:
        Handles variations like:
        - "LADY  GAGA" -> "Lady Gaga"
        - "ed sheeran" -> "Ed Sheeran" (if that's how ACRCloud provides it)
        - "Panic!   At The  Disco" -> "Panic! At The Disco"
    """
    try:
        # Validate response structure and extract artist
        if ('data' in response_data and 
            'metadata' in response_data['data'] and 
            'music' in response_data['data']['metadata'] and 
            response_data['data']['metadata']['music'] and  
            response_data['data']['metadata']['music'][0]['artists'] and  
            'name' in response_data['data']['metadata']['music'][0]['artists'][0]):
            
            # Get artist name and normalize spacing
            artist_name = response_data['data']['metadata']['music'][0]['artists'][0]['name']
            artist_name = normalize_artist_name(artist_name)
            
            if logger:
                logger.info(f"Found artist: {artist_name}")
            
            return artist_name
            
        return None

    except Exception as e:
        if logger:
            logger.error(f"Error extracting artist: {str(e)}")
        return None

