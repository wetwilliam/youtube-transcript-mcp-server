"""
YouTube Transcript MCP Server

A Model Context Protocol (MCP) server for downloading YouTube video transcripts.
"""

__version__ = "1.0.0"
__author__ = "YouTube Transcript MCP Server"
__description__ = "MCP server for downloading YouTube video transcripts"

from .transcript_tools import YouTubeTranscriptManager
from .utils import extract_video_id, format_transcript_output, validate_language_code

__all__ = [
    "YouTubeTranscriptManager",
    "extract_video_id",
    "format_transcript_output",
    "validate_language_code",
]