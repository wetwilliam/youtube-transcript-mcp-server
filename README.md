# YouTube Transcript MCP Server

A Model Context Protocol (MCP) server for downloading YouTube video transcripts. This server allows Claude Desktop to extract video IDs from YouTube URLs and download transcripts in various formats.

## Features

- **Extract Video ID**: Extract YouTube video ID from URLs or validate existing IDs
- **Download Transcripts**: Download video transcripts with language preferences
- **Multiple Formats**: Support for JSON, text, SRT, and WebVTT formats
- **Language Support**: Automatic language detection and translation capabilities

## Installation

1. Clone or download this repository
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Add the following configuration to your Claude Desktop config file:

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "youtube-transcript": {
      "command": "python",
      "args": ["C:\\path\\to\\youtube-transcript-mcp-server\\simple_server.py"],
      "env": {}
    }
  }
}
```

Replace `C:\\path\\to\\youtube-transcript-mcp-server\\simple_server.py` with the actual path to your server file.

## Usage

Once configured, you can use the following tools in Claude Desktop:

### Extract Video ID
Extract a YouTube video ID from a URL:
```
Extract the video ID from: https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

### Download Transcript
Download a video transcript:
```
Download the transcript for video ID: dQw4w9WgXcQ
```

You can also specify language preferences and output format:
```
Download the transcript for video ID: dQw4w9WgXcQ in Chinese (zh-TW) format as SRT
```

## Supported Languages

The server supports automatic language detection and can translate transcripts to available languages. Common language codes include:
- `en` - English
- `zh-TW` - Chinese (Taiwan)
- `zh-CN` - Chinese (Simplified)
- `ja` - Japanese
- `ko` - Korean
- `es` - Spanish
- `fr` - French
- `de` - German

## Output Formats

- **text**: Plain text format (default)
- **json**: JSON format with timestamps
- **srt**: SubRip subtitle format
- **vtt**: WebVTT subtitle format

## Requirements

- Python 3.7+
- youtube-transcript-api
- Claude Desktop with MCP support

## Troubleshooting

1. **Server not starting**: Check that Python is installed and accessible
2. **No transcripts available**: Some videos may not have transcripts or may be region-locked
3. **Language not found**: Try different language codes or let the server auto-detect

## License

This project uses the youtube-transcript-api library. Please check the original library's license for usage terms.