# Video AMA

A web application that allows you to ask questions about video content using AI-powered transcript analysis and timestamp navigation.

*This was vibe coded with Claude Code.*

## Features

- **File Upload**: Select video files directly through a file browser
- **Video Processing**: Extract audio and generate transcripts using OpenAI Whisper
- **AI-Powered Q&A**: Ask questions about video content using GPT-4
- **Smart Timestamp Navigation**: Click timestamps to jump to relevant parts of the video
- **Clean UI**: Twitch-like interface with video player on left, chat on right
- **Relevant Context**: Shows only the most relevant transcript segments for each question

## Installation & Setup

### Prerequisites

1. **Python 3.9+**
2. **uv package manager** - Install from [astral-sh.github.io/uv](https://astral-sh.github.io/uv/)
3. **FFmpeg** - Required for video processing

### Step 1: Install FFmpeg

On macOS using Homebrew:
```bash
# If you don't have Homebrew, install it first:
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install FFmpeg
brew install ffmpeg
```

On other platforms, see [FFmpeg Download](https://ffmpeg.org/download.html)

### Step 2: Clone and Install

```bash
git clone <repository-url>
cd video-ama

# Install the package with uv
uv pip install -e .
```

### Step 3: Set up OpenAI API Key

1. Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Set up environment variables:

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file and add your API key
# Replace 'your_openai_api_key_here' with your actual API key
```

Your `.env` file should look like:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
HOST=0.0.0.0
PORT=8000
DEBUG=true
```

### Step 4: Run the Application

```bash
video-ama
```

The application will start at `http://localhost:8000`

## Usage

1. **Upload Video**: Click "Choose File" to select a video file from your computer
2. **Process Video**: Click "Process Video" and wait for transcription (this may take a few minutes)
3. **Ask Questions**: Type questions about the video content in the chat interface
4. **Navigate**: Click the timestamp buttons to jump to relevant parts of the video

## Example Questions

- "What was the main topic discussed?"
- "Can you find where they mention the API configuration?"
- "What arguments does the command take?"
- "Where do they explain the installation process?"

## Supported Video Formats

- MP4, AVI, MOV, MKV, WebM
- Any format supported by FFmpeg

## Architecture

```
video_ama/
├── api/           # FastAPI backend with upload and Q&A endpoints
├── core/          # Video processing and AI logic
│   ├── video_processor.py  # Audio extraction and transcription
│   └── qa_engine.py        # Question answering with GPT-4
├── frontend/      # Static web interface
│   ├── index.html
│   └── static/
│       ├── css/styles.css  # Twitch-like styling
│       └── js/app.js       # Frontend logic
└── main.py        # Application entry point
```

## Development

Install with development dependencies:
```bash
uv pip install -e ".[dev]"
```

Run with auto-reload for development:
```bash
video-ama  # Already includes reload=True in development
```

## Troubleshooting

**FFmpeg not found error**: Install FFmpeg using the instructions above

**OpenAI API error**: Check that your API key is correctly set in the `.env` file

**Video won't play**: Try a different video format (MP4 works best)

**Slow processing**: Large video files take longer to process. The transcription time depends on video length.