#!/usr/bin/env python3
"""
Simple YouTube Transcript MCP Server - Direct approach
"""

import asyncio
import json
import logging
import sys
import os

# Add src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

from youtube_transcript_mcp.transcript_tools import YouTubeTranscriptManager
from youtube_transcript_mcp.utils import extract_video_id, format_transcript_output

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the YouTube transcript manager
transcript_manager = YouTubeTranscriptManager()

class SimpleYouTubeTranscriptServer:
    def __init__(self):
        self.tools = [
            {
                "name": "extract_video_id",
                "description": "Extract YouTube video ID from a URL or return the ID if already provided",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url_or_id": {
                            "type": "string",
                            "description": "YouTube URL or video ID"
                        }
                    },
                    "required": ["url_or_id"]
                }
            },
            {
                "name": "get_video_transcript",
                "description": "Download transcript for a YouTube video",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "video_id": {
                            "type": "string",
                            "description": "YouTube video ID"
                        },
                        "languages": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of preferred language codes (e.g., ['en', 'zh-TW', 'es'])",
                            "default": ["en"]
                        },
                        "format": {
                            "type": "string",
                            "enum": ["json", "text", "srt", "vtt"],
                            "description": "Output format",
                            "default": "text"
                        }
                    },
                    "required": ["video_id"]
                }
            }
        ]

    async def handle_request(self, request):
        """Handle MCP request"""
        method = request.get("method")
        
        # Handle notification requests (no id field)
        if method == "notifications/initialized":
            # Notifications don't need a response, just log and continue
            logger.info("Received initialization notification")
            return None
        
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request["id"],
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "youtube-transcript-mcp",
                        "version": "1.0.0"
                    }
                }
            }
        
        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request["id"],
                "result": {
                    "tools": self.tools
                }
            }
        
        elif method == "tools/call":
            params = request.get("params", {})
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            result = await self.call_tool(tool_name, arguments)
            
            return {
                "jsonrpc": "2.0",
                "id": request["id"],
                "result": result
            }
        
        else:
            return {
                "jsonrpc": "2.0",
                "id": request["id"],
                "error": {
                    "code": -32601,
                    "message": "Method not found"
                }
            }

    async def call_tool(self, name, arguments):
        """Call a specific tool"""
        try:
            if name == "extract_video_id":
                url_or_id = arguments.get("url_or_id", "")
                video_id = extract_video_id(url_or_id)
                
                if not video_id:
                    return {
                        "content": [{
                            "type": "text",
                            "text": f"Error: Could not extract valid video ID from '{url_or_id}'"
                        }],
                        "isError": True
                    }
                
                return {
                    "content": [{
                        "type": "text",
                        "text": f"Video ID: {video_id}"
                    }],
                    "isError": False
                }
            
            elif name == "get_video_transcript":
                video_id = arguments.get("video_id", "")
                languages = arguments.get("languages", ["en"])
                format_type = arguments.get("format", "text")
                
                if not video_id:
                    return {
                        "content": [{
                            "type": "text",
                            "text": "Error: video_id is required"
                        }],
                        "isError": True
                    }
                
                try:
                    transcript = transcript_manager.get_transcript(video_id, languages)
                    formatted_output = format_transcript_output(transcript, format_type)
                    
                    return {
                        "content": [{
                            "type": "text",
                            "text": formatted_output
                        }],
                        "isError": False
                    }
                    
                except Exception as e:
                    return {
                        "content": [{
                            "type": "text",
                            "text": f"Error getting transcript: {str(e)}"
                        }],
                        "isError": True
                    }
            
            else:
                return {
                    "content": [{
                        "type": "text",
                        "text": f"Unknown tool: {name}"
                    }],
                    "isError": True
                }
        
        except Exception as e:
            return {
                "content": [{
                    "type": "text",
                    "text": f"Unexpected error: {str(e)}"
                }],
                "isError": True
            }

async def main():
    """Run the simple MCP server"""
    logger.info("=== STARTING SIMPLE YOUTUBE TRANSCRIPT MCP SERVER ===")
    
    server = SimpleYouTubeTranscriptServer()
    
    # Read from stdin and write to stdout
    while True:
        try:
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                break
            
            request = json.loads(line.strip())
            logger.info(f"Received request: {request.get('method')}")
            
            response = await server.handle_request(request)
            
            # Only write response if it's not None (notifications don't need responses)
            if response is not None:
                print(json.dumps(response))
                sys.stdout.flush()
            
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            error_response = {
                "jsonrpc": "2.0",
                "id": request.get("id") if 'request' in locals() else None,
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }
            print(json.dumps(error_response))
            sys.stdout.flush()

if __name__ == "__main__":
    asyncio.run(main())