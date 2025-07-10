"""
Utility functions for the YouTube Transcript MCP Server.
"""

import json
import re
from typing import Optional
from urllib.parse import parse_qs, urlparse


def extract_video_id(url_or_id: str) -> Optional[str]:
    """
    Extract YouTube video ID from a URL or return the ID if already provided.
    
    Args:
        url_or_id: YouTube URL or video ID
        
    Returns:
        Video ID if found, None otherwise
        
    Examples:
        >>> extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        'dQw4w9WgXcQ'
        >>> extract_video_id("https://youtu.be/dQw4w9WgXcQ")
        'dQw4w9WgXcQ'
        >>> extract_video_id("dQw4w9WgXcQ")
        'dQw4w9WgXcQ'
    """
    if not url_or_id:
        return None
    
    # If it's already just a video ID (11 characters, alphanumeric + underscore + hyphen)
    if re.match(r'^[a-zA-Z0-9_-]{11}$', url_or_id):
        return url_or_id
    
    # Parse different YouTube URL formats
    patterns = [
        # Standard YouTube URLs
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
        # YouTube short URLs
        r'(?:https?://)?youtu\.be/([a-zA-Z0-9_-]{11})',
        # YouTube embed URLs
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})',
        # YouTube playlist URLs with video
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?.*v=([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    
    return None


def validate_language_code(language_code: str) -> bool:
    """
    Validate if a language code is in the correct format.
    
    Args:
        language_code: Language code to validate
        
    Returns:
        True if valid, False otherwise
        
    Examples:
        >>> validate_language_code("en")
        True
        >>> validate_language_code("zh-TW")
        True
        >>> validate_language_code("invalid")
        False
    """
    if not language_code:
        return False
    
    # Accept common language codes (2-5 characters, letters, numbers, hyphens)
    return bool(re.match(r'^[a-zA-Z]{2,3}(-[a-zA-Z]{2,4})?$', language_code))


def format_transcript_output(transcript, format_type: str) -> str:
    """
    Format a transcript for output.
    
    Args:
        transcript: FetchedTranscript object
        format_type: Output format ('json', 'text', 'srt', 'vtt')
        
    Returns:
        Formatted transcript string
    """
    if format_type == "json":
        # Convert transcript to JSON format
        data = {
            "video_id": transcript.video_id,
            "language": transcript.language,
            "language_code": transcript.language_code,
            "is_generated": transcript.is_generated,
            "transcript": []
        }
        
        for snippet in transcript:
            data["transcript"].append({
                "text": snippet.text,
                "start": snippet.start,
                "duration": snippet.duration
            })
        
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    elif format_type == "text":
        # Simple text format with timestamps
        lines = []
        for snippet in transcript:
            lines.append(f"[{snippet.start:.2f}s] {snippet.text}")
        return "\n".join(lines)
    
    elif format_type == "srt":
        # SRT subtitle format
        lines = []
        for i, snippet in enumerate(transcript, 1):
            start_time = seconds_to_srt_time(snippet.start)
            end_time = seconds_to_srt_time(snippet.start + snippet.duration)
            
            lines.append(f"{i}")
            lines.append(f"{start_time} --> {end_time}")
            lines.append(snippet.text)
            lines.append("")  # Empty line between entries
        
        return "\n".join(lines)
    
    elif format_type == "vtt":
        # WebVTT subtitle format
        lines = ["WEBVTT", ""]
        
        for snippet in transcript:
            start_time = seconds_to_vtt_time(snippet.start)
            end_time = seconds_to_vtt_time(snippet.start + snippet.duration)
            
            lines.append(f"{start_time} --> {end_time}")
            lines.append(snippet.text)
            lines.append("")  # Empty line between entries
        
        return "\n".join(lines)
    
    else:
        raise ValueError(f"Unsupported format type: {format_type}")


def seconds_to_srt_time(seconds: float) -> str:
    """
    Convert seconds to SRT time format (HH:MM:SS,mmm).
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Time in SRT format
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millisecs = int((seconds % 1) * 1000)
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"


def seconds_to_vtt_time(seconds: float) -> str:
    """
    Convert seconds to WebVTT time format (HH:MM:SS.mmm).
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Time in WebVTT format
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millisecs = int((seconds % 1) * 1000)
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millisecs:03d}"


def get_file_extension(format_type: str) -> str:
    """
    Get the appropriate file extension for a format type.
    
    Args:
        format_type: Format type
        
    Returns:
        File extension
    """
    extensions = {
        "json": "json",
        "text": "txt",
        "srt": "srt",
        "vtt": "vtt"
    }
    
    return extensions.get(format_type, "txt")


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to remove invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Replace invalid characters with underscores
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '_', filename)
    
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(' .')
    
    return sanitized