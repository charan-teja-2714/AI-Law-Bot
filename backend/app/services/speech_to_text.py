import os
import tempfile
from typing import Dict, Any
from fastapi import UploadFile
# Lazy imports: whisper and pydub will be imported when needed


class SpeechToTextService:
    """
    Speech-to-text service using OpenAI Whisper
    Supports audio and video files (extracts audio from video)
    """

    SUPPORTED_AUDIO_FORMATS = {".mp3", ".wav", ".m4a", ".flac", ".ogg", ".webm", ".mp4"}
    SUPPORTED_VIDEO_FORMATS = {".mp4", ".avi", ".mov", ".mkv", ".webm"}

    def __init__(self, model_size: str = "base"):
        """
        Initialize Whisper model (lazy loading)

        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
                       'base' is good balance between speed and accuracy
        """
        self.model_size = model_size
        self._model = None

    @property
    def model(self):
        """Lazy load Whisper model only when needed"""
        if self._model is None:
            import whisper  # Import only when model is actually used
            print(f"Loading Whisper model: {self.model_size}")
            self._model = whisper.load_model(self.model_size)
            print("Whisper model loaded successfully")
        return self._model

    def extract_audio_from_video(self, video_path: str) -> str:
        """
        Extract audio from video file using ffmpeg directly

        Args:
            video_path: Path to video file

        Returns:
            Path to extracted audio file (WAV format)
        """
        audio_path = os.path.splitext(video_path)[0] + "_extracted.wav"

        # Try ffmpeg directly (most reliable, avoids pyaudioop issues)
        try:
            import subprocess
            print(f"[AUDIO] Converting to WAV with ffmpeg: {video_path}")
            result = subprocess.run(
                ["ffmpeg", "-i", video_path, "-vn", "-acodec", "pcm_s16le",
                 "-ar", "16000", "-ac", "1", "-y", audio_path],
                capture_output=True, text=True, timeout=60
            )
            if result.returncode == 0 and os.path.exists(audio_path) and os.path.getsize(audio_path) > 100:
                print(f"[AUDIO] ffmpeg conversion successful: {audio_path}")
                return audio_path
            else:
                print(f"[AUDIO] ffmpeg failed: {result.stderr}")
        except FileNotFoundError:
            print("[AUDIO] ffmpeg not found, trying pydub...")
        except Exception as e:
            print(f"[AUDIO] ffmpeg error: {e}")

        # Fallback to pydub
        try:
            from pydub import AudioSegment
            print(f"[AUDIO] Loading with pydub: {video_path}")
            video = AudioSegment.from_file(video_path)
            print(f"[AUDIO] Exporting audio to: {audio_path}")
            video.export(audio_path, format="wav")
            return audio_path
        except Exception as e:
            print(f"[AUDIO] pydub error: {e}")

        # Last resort: return original path
        print("[AUDIO] Warning: Could not convert audio, will try direct transcription")
        return video_path

    def transcribe_audio(self, audio_path: str, language: str = None) -> Dict[str, Any]:
        """
        Transcribe audio file to text

        Args:
            audio_path: Path to audio file
            language: Optional language code (en, hi, etc.)

        Returns:
            Dict with:
                - text: Transcribed text
                - language: Detected language
                - segments: List of segments with timestamps
        """
        import os
        print(f"[WHISPER] Transcribing file: {audio_path}")
        print(f"[WHISPER] File exists: {os.path.exists(audio_path)}")
        print(f"[WHISPER] File size: {os.path.getsize(audio_path) if os.path.exists(audio_path) else 0} bytes")
        
        # Transcribe using Whisper with fp16=False for CPU
        # Lower no_speech_threshold to avoid filtering out speech as silence
        whisper_options = {
            "fp16": False,
            "verbose": True,
            "no_speech_threshold": 0.3,
            "logprob_threshold": -1.0,
            "condition_on_previous_text": False,
        }
        if language:
            whisper_options["language"] = language

        result = self.model.transcribe(audio_path, **whisper_options)
        
        print(f"[WHISPER] Transcription complete. Text length: {len(result['text'])}")
        print(f"[WHISPER] Text: {result['text']}")
        print(f"[WHISPER] Segments: {len(result.get('segments', []))}")

        return {
            "text": result["text"].strip(),
            "language": result["language"],
            "segments": result["segments"]
        }

    async def process_file(self, file: UploadFile) -> Dict[str, Any]:
        """
        Process audio or video file and extract text

        Args:
            file: Uploaded file (audio or video)

        Returns:
            Dict with:
                - text: Transcribed text
                - language: Detected language
                - file_type: 'audio' or 'video'
        """
        # Get file extension
        file_ext = os.path.splitext(file.filename)[1].lower()

        # Verify file is supported
        if not self.is_supported_file(file.filename):
            raise Exception(f"Unsupported file format: {file_ext}. Supported formats: {self.SUPPORTED_AUDIO_FORMATS | self.SUPPORTED_VIDEO_FORMATS}")

        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            # Save uploaded file
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name

        try:
            audio_path = tmp_path
            file_type = "audio"

            # If video, extract audio first
            if file_ext in self.SUPPORTED_VIDEO_FORMATS:
                file_type = "video"
                print(f"Extracting audio from video: {file.filename}")
                audio_path = self.extract_audio_from_video(tmp_path)
            elif file_ext in (".webm", ".ogg", ".m4a", ".flac") and file_ext != ".wav":
                # Convert non-wav audio formats to wav for better Whisper compatibility
                print(f"Converting audio to WAV: {file.filename}")
                audio_path = self.extract_audio_from_video(tmp_path)

            # Transcribe
            print(f"Transcribing audio: {file.filename}")
            result = self.transcribe_audio(audio_path)

            # Cleanup
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            if audio_path != tmp_path and os.path.exists(audio_path):
                os.remove(audio_path)

            return {
                "text": result["text"],
                "language": result["language"],
                "file_type": file_type,
                "filename": file.filename
            }

        except Exception as e:
            # Cleanup on error
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            if audio_path != tmp_path and os.path.exists(audio_path):
                os.remove(audio_path)

            error_msg = str(e)
            print(f"ERROR in speech_to_text.process_file: {error_msg}")

            # Provide specific error messages
            if "ffmpeg" in error_msg.lower() or "decoder" in error_msg.lower():
                raise Exception("FFmpeg not found or not properly installed. Please install FFmpeg to process audio/video files.")
            elif "whisper" in error_msg.lower():
                raise Exception("Whisper model failed to load. Please check if the model is properly installed.")
            else:
                raise Exception(f"Error processing audio/video file: {error_msg}")

    def is_supported_file(self, filename: str) -> bool:
        """Check if file format is supported"""
        ext = os.path.splitext(filename)[1].lower()
        return ext in self.SUPPORTED_AUDIO_FORMATS or ext in self.SUPPORTED_VIDEO_FORMATS


# Global instance
speech_to_text_service = SpeechToTextService()
