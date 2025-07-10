"""
YouTube Transcript Tools

This module provides tools for interacting with YouTube video transcripts
using the youtube-transcript-api.
"""

import logging
from typing import List, Optional, Union

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import (
    JSONFormatter,
    TextFormatter,
    SRTFormatter,
    WebVTTFormatter,
)

logger = logging.getLogger(__name__)


class YouTubeTranscriptManager:
    """Manager class for YouTube transcript operations."""
    
    def __init__(self):
        """Initialize the YouTube transcript manager."""
        self.api = YouTubeTranscriptApi()
        self.formatters = {
            'json': JSONFormatter(),
            'text': TextFormatter(),
            'srt': SRTFormatter(),
            'vtt': WebVTTFormatter(),
        }
    
    def list_transcripts(self, video_id: str):
        """
        List all available transcripts for a video.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            TranscriptList object containing available transcripts
            
        Raises:
            Exception: If transcripts cannot be retrieved
        """
        try:
            transcript_list = self.api.list(video_id)
            # Count transcripts manually since TranscriptList doesn't have len()
            transcript_count = sum(1 for _ in transcript_list)
            logger.info(f"Found {transcript_count} transcripts for video {video_id}")
            return transcript_list
        except Exception as e:
            logger.error(f"Error listing transcripts for {video_id}: {str(e)}")
            raise Exception(f"Could not list transcripts for video {video_id}: {str(e)}")
    
    def get_transcript(
        self, 
        video_id: str, 
        languages: Optional[List[str]] = None,
        preserve_formatting: bool = False
    ):
        """
        Get transcript for a video in the specified languages.
        
        Args:
            video_id: YouTube video ID
            languages: List of preferred language codes (e.g., ['en', 'zh-TW'])
            preserve_formatting: Whether to preserve HTML formatting
            
        Returns:
            FetchedTranscript object
            
        Raises:
            Exception: If transcript cannot be retrieved
        """
        if languages is None:
            languages = ['en']
        
        try:
            transcript = self.api.fetch(
                video_id, 
                languages=languages,
                preserve_formatting=preserve_formatting
            )
            logger.info(f"Retrieved transcript for video {video_id} in language {transcript.language}")
            return transcript
        except Exception as e:
            logger.error(f"Error getting transcript for {video_id}: {str(e)}")
            raise Exception(f"Could not get transcript for video {video_id}: {str(e)}")
    
    def translate_transcript(
        self,
        video_id: str,
        source_language: str = "auto",
        target_language: str = "en"
    ):
        """
        Translate a video transcript to a different language.
        
        Args:
            video_id: YouTube video ID
            source_language: Source language code (or 'auto' to detect)
            target_language: Target language code for translation
            
        Returns:
            FetchedTranscript object with translated content
            
        Raises:
            Exception: If transcript cannot be translated
        """
        try:
            # Get the transcript list
            transcript_list = self.list_transcripts(video_id)
            
            # Find the source transcript
            if source_language == "auto":
                # Try to find any available transcript
                transcript = None
                for t in transcript_list:
                    if t.is_translatable:
                        transcript = t
                        break
                
                if transcript is None:
                    raise Exception("No translatable transcripts found")
            else:
                transcript = transcript_list.find_transcript([source_language])
            
            # Translate the transcript
            translated_transcript = transcript.translate(target_language)
            
            # Fetch the translated transcript
            result = translated_transcript.fetch()
            
            logger.info(f"Translated transcript for video {video_id} from {transcript.language} to {target_language}")
            return result
            
        except Exception as e:
            logger.error(f"Error translating transcript for {video_id}: {str(e)}")
            raise Exception(f"Could not translate transcript for video {video_id}: {str(e)}")
    
    def format_transcript(self, transcript, format_type: str = "json", **kwargs):
        """
        Format a transcript using the specified formatter.
        
        Args:
            transcript: FetchedTranscript object
            format_type: Format type ('json', 'text', 'srt', 'vtt')
            **kwargs: Additional formatting options
            
        Returns:
            Formatted transcript string
            
        Raises:
            ValueError: If format_type is not supported
        """
        if format_type not in self.formatters:
            raise ValueError(f"Unsupported format type: {format_type}")
        
        formatter = self.formatters[format_type]
        return formatter.format_transcript(transcript, **kwargs)
    
    def get_video_info(self, video_id: str) -> dict:
        """
        Get basic information about a video's available transcripts.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Dictionary containing video transcript information
        """
        try:
            transcript_list = self.list_transcripts(video_id)
            
            info = {
                "video_id": video_id,
                "total_transcripts": len(transcript_list),
                "available_languages": [],
                "manually_created": [],
                "auto_generated": [],
                "translatable": []
            }
            
            for transcript in transcript_list:
                lang_info = {
                    "language": transcript.language,
                    "language_code": transcript.language_code,
                    "is_generated": transcript.is_generated,
                    "is_translatable": transcript.is_translatable
                }
                
                info["available_languages"].append(lang_info)
                
                if transcript.is_generated:
                    info["auto_generated"].append(lang_info)
                else:
                    info["manually_created"].append(lang_info)
                
                if transcript.is_translatable:
                    info["translatable"].append(lang_info)
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting video info for {video_id}: {str(e)}")
            raise Exception(f"Could not get video info for {video_id}: {str(e)}")