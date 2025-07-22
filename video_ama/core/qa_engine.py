"""Q&A engine for answering questions based on video transcripts."""

import re
from typing import Dict, Any, List, Optional
from openai import AsyncOpenAI

from video_ama.api.models import QuestionResponse, Timestamp


class QAEngine:
    """Handles question answering based on video transcripts."""
    
    def __init__(self):
        """Initialize the Q&A engine with OpenAI client."""
        self.openai_client = AsyncOpenAI()
        self.transcript: Optional[Dict[str, Any]] = None
    
    def set_transcript(self, transcript: Dict[str, Any]) -> None:
        """Set the current transcript for Q&A."""
        self.transcript = transcript
    
    async def answer_question(self, question: str) -> QuestionResponse:
        """
        Answer a question based on the video transcript.
        
        Args:
            question: The user's question
            
        Returns:
            QuestionResponse with answer and relevant timestamps
        """
        if not self.transcript:
            return QuestionResponse(
                answer="No transcript available. Please upload and process a video first.",
                timestamps=[],
                confidence=0.0
            )
        
        # Create context from transcript and get the segments used
        context, relevant_segments = self._create_context_and_segments(question)
        
        # Generate answer using OpenAI
        answer = await self._generate_answer(question, context)
        
        # Use the same segments that were used to generate the answer, but limit to top 10
        timestamps = [
            Timestamp(
                start=segment["start"],
                end=segment["end"],
                text=segment["text"]
            )
            for segment in relevant_segments[:10]
        ]
        
        return QuestionResponse(
            answer=answer,
            timestamps=timestamps,
            confidence=0.8  # You could implement actual confidence scoring
        )
    
    def _create_context_and_segments(self, question: str) -> tuple[str, list]:
        """Create a formatted context string and return the segments used."""
        if not self.transcript or "segments" not in self.transcript:
            return "", []
        
        # Find relevant segments based on question keywords
        question_keywords = self._extract_keywords(question.lower())
        relevant_segments = []
        
        for segment in self.transcript["segments"]:
            segment_text = segment["text"].lower()
            # Check for keyword matches
            matches = sum(1 for keyword in question_keywords if keyword in segment_text)
            if matches > 0:
                relevant_segments.append((segment, matches))
        
        # Sort by relevance and limit to top segments to stay within token limits
        relevant_segments.sort(key=lambda x: x[1], reverse=True)
        
        # Take top 50 most relevant segments (adjust as needed)
        context_parts = []
        selected_segments = []
        max_segments = 50
        
        for segment, _ in relevant_segments[:max_segments]:
            timestamp_str = f"[{self._format_timestamp(segment['start'])} - {self._format_timestamp(segment['end'])}]"
            context_parts.append(f"{timestamp_str} {segment['text']}")
            selected_segments.append(segment)
        
        # If no relevant segments found, take a sample from the beginning
        if not context_parts:
            for segment in self.transcript["segments"][:20]:
                timestamp_str = f"[{self._format_timestamp(segment['start'])} - {self._format_timestamp(segment['end'])}]"
                context_parts.append(f"{timestamp_str} {segment['text']}")
                selected_segments.append(segment)
        
        return "\n".join(context_parts), selected_segments
    
    async def _generate_answer(self, question: str, context: str) -> str:
        """Generate an answer using OpenAI API."""
        system_prompt = """You are a helpful assistant that answers questions based on video transcripts. 
        You will be provided with a transcript that includes timestamps in the format [MM:SS - MM:SS].
        
        When answering:
        1. Base your answer solely on the information in the transcript
        2. If the answer involves specific quotes or references, mention the approximate timestamp
        3. If you cannot find the information in the transcript, say so clearly
        4. Be concise but comprehensive
        5. When referencing specific parts of the video, use natural language like "around 2 minutes and 30 seconds" or "at the beginning of the video"
        """
        
        user_prompt = f"""Based on this video transcript:

{context}

Question: {question}

Please provide a helpful answer based on the transcript content."""
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            return response.choices[0].message.content or "I couldn't generate an answer."
            
        except Exception as e:
            return f"Error generating answer: {str(e)}"
    
    
    def _extract_keywords(self, text: str) -> set:
        """Extract meaningful keywords from text."""
        # Remove common stop words and extract meaningful terms
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", 
            "of", "with", "by", "is", "are", "was", "were", "be", "been", "have", 
            "has", "had", "do", "does", "did", "will", "would", "could", "should",
            "what", "when", "where", "why", "how", "who", "which", "that", "this",
            "these", "those", "i", "you", "he", "she", "it", "we", "they"
        }
        
        # Extract words (alphanumeric, at least 3 characters)
        words = re.findall(r'\b[a-zA-Z0-9]{3,}\b', text)
        keywords = {word.lower() for word in words if word.lower() not in stop_words}
        
        return keywords
    
    def _format_timestamp(self, seconds: float) -> str:
        """Format seconds into MM:SS format."""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"