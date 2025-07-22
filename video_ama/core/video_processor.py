"""Video processing module for extracting audio and generating transcripts."""

import os
import tempfile
from pathlib import Path
from typing import Dict, Any, List
import whisper
import ffmpeg


class VideoProcessor:
    """Handles video processing and transcription."""
    
    def __init__(self):
        """Initialize the video processor with Whisper model."""
        self.whisper_model = whisper.load_model("base")
    
    async def process_video(self, video_path: str) -> Dict[str, Any]:
        """
        Process a video file to extract transcript with timestamps.
        
        Args:
            video_path: Path to the video file
            
        Returns:
            Dictionary containing transcript segments with timestamps
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        # Extract audio from video
        audio_path = await self._extract_audio(video_path)
        
        try:
            # Transcribe audio using Whisper
            result = self.whisper_model.transcribe(audio_path)
            
            # Format the transcript with segments and timestamps
            transcript = {
                "text": result["text"],
                "segments": [
                    {
                        "start": segment["start"],
                        "end": segment["end"],
                        "text": segment["text"].strip()
                    }
                    for segment in result["segments"]
                ],
                "language": result["language"]
            }
            
            return transcript
            
        finally:
            # Clean up temporary audio file
            if os.path.exists(audio_path):
                os.unlink(audio_path)
    
    async def _extract_audio(self, video_path: str) -> str:
        """
        Extract audio from video file using ffmpeg.
        
        Args:
            video_path: Path to the video file
            
        Returns:
            Path to the extracted audio file
        """
        # Create temporary file for audio
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            audio_path = temp_file.name
        
        try:
            # Extract audio using ffmpeg
            (
                ffmpeg
                .input(video_path)
                .audio
                .output(audio_path, acodec='pcm_s16le', ac=1, ar='16k')
                .run(overwrite_output=True, quiet=True)
            )
            
            return audio_path
            
        except ffmpeg.Error as e:
            # Clean up on error
            if os.path.exists(audio_path):
                os.unlink(audio_path)
            raise Exception(f"Failed to extract audio: {e}")
    
    def get_segment_at_time(self, transcript: Dict[str, Any], timestamp: float) -> Dict[str, Any]:
        """
        Find the transcript segment at a specific timestamp.
        
        Args:
            transcript: The transcript dictionary
            timestamp: Time in seconds
            
        Returns:
            The segment dictionary containing the timestamp
        """
        segments = transcript.get("segments", [])
        
        for segment in segments:
            if segment["start"] <= timestamp <= segment["end"]:
                return segment
        
        # If no exact match, find the closest segment
        if segments:
            closest_segment = min(
                segments,
                key=lambda s: min(abs(s["start"] - timestamp), abs(s["end"] - timestamp))
            )
            return closest_segment
        
        return {}