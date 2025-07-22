"""FastAPI application for video Q&A."""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse
from pathlib import Path
import os

from video_ama.core.video_processor import VideoProcessor
from video_ama.core.qa_engine import QAEngine
from video_ama.api.models import QuestionRequest, QuestionResponse

app = FastAPI(title="Video AMA", version="0.1.0")

# Initialize core components
video_processor = VideoProcessor()
qa_engine = QAEngine()

# Store current video path for serving
current_video_path = None

# Mount static files
static_dir = Path(__file__).parent.parent / "frontend" / "static"
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML page."""
    html_file = Path(__file__).parent.parent / "frontend" / "index.html"
    if html_file.exists():
        return FileResponse(html_file)
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head><title>Video AMA</title></head>
    <body>
        <h1>Video AMA - Setup in Progress</h1>
        <p>Frontend will be available soon!</p>
    </body>
    </html>
    """)


@app.post("/api/upload-video")
async def upload_video(video_file: UploadFile = File(...)):
    """Process an uploaded video file and extract transcript."""
    import traceback
    import tempfile
    import shutil
    
    try:
        print(f"Processing uploaded video: {video_file.filename}")
        
        # Create a temporary file to store the uploaded video
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(video_file.filename)[1]) as temp_file:
            temp_video_path = temp_file.name
            
            # Copy uploaded file to temporary location
            shutil.copyfileobj(video_file.file, temp_file)
        
        print(f"Video saved to temporary file: {temp_video_path}")
        print("Starting video processing...")
        
        try:
            # Process video and extract transcript
            transcript = await video_processor.process_video(temp_video_path)
            
            print(f"Transcript generated with {len(transcript.get('segments', []))} segments")
            
            # Store transcript for Q&A
            qa_engine.set_transcript(transcript)
            
            # Store video path for serving
            global current_video_path
            current_video_path = temp_video_path
            
            return {
                "status": "success",
                "message": "Video processed successfully",
                "transcript_length": len(transcript.get("segments", []))
            }
            
        except Exception as processing_error:
            # Clean up temporary file on processing error
            if os.path.exists(temp_video_path):
                os.unlink(temp_video_path)
            raise processing_error
            
    except Exception as e:
        error_detail = f"Error: {str(e)}\nTraceback: {traceback.format_exc()}"
        print(error_detail)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """Answer a question based on the video transcript."""
    try:
        response = await qa_engine.answer_question(request.question)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/video")
async def serve_video():
    """Serve the current video file."""
    global current_video_path
    if not current_video_path or not os.path.exists(current_video_path):
        raise HTTPException(status_code=404, detail="No video available")
    
    return FileResponse(
        current_video_path,
        media_type="video/mp4",
        headers={"Accept-Ranges": "bytes"}
    )


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}