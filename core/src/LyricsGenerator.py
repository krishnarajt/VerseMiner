import os
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional
from core.common_constants.constants import (
    WHISPER_ENGINE,
    WHISPER_MODEL,
    WHISPER_DEVICE,
    FASTER_WHISPER_MODEL,
    FASTER_WHISPER_COMPUTE_TYPE,
    AUDIO_EXTENSIONS,
    MUSIC_ROOT_PATH,
)
from core.utils.llm_utils import LLMUtils
from core.utils.logging_utils import get_logger
from core.utils.sql_utils import SQLUtils

logger = get_logger(__name__)


class LyricsGenerator:
    def __init__(self):
        """Initialize Whisper model (either openai-whisper or faster-whisper) and LLM utilities."""
        self.engine_type = WHISPER_ENGINE.lower()

        if self.engine_type == "faster":
            logger.info(
                f"Loading Faster-Whisper model: {FASTER_WHISPER_MODEL} (compute_type: {FASTER_WHISPER_COMPUTE_TYPE})"
            )
            from faster_whisper import WhisperModel

            self.model = WhisperModel(
                FASTER_WHISPER_MODEL,
                device="cpu" if WHISPER_DEVICE.lower() == "cpu" else "cuda",
                compute_type=FASTER_WHISPER_COMPUTE_TYPE,
            )
            # self.model = self.model.half()
            logger.info("Faster-Whisper model loaded successfully")
        elif self.engine_type == "openai":
            logger.info(f"Loading OpenAI Whisper model: {WHISPER_MODEL}")
            import whisper

            self.model = whisper.load_model(WHISPER_MODEL, device=WHISPER_DEVICE)
            logger.info("OpenAI Whisper model loaded successfully")
        else:
            raise ValueError(
                f"Unsupported WHISPER_ENGINE: {WHISPER_ENGINE}. Use 'openai' or 'faster'"
            )

        self.llm = LLMUtils()
        self.sql_utils = SQLUtils()

    def get_all_audio_files(self, root_directory):
        """
        Recursively find all audio files in the directory.

        Args:
            root_directory: Root directory to search

        Returns:
            List of Path objects for audio files
        """
        audio_files = []
        root_path = Path(root_directory)

        for ext in AUDIO_EXTENSIONS:
            audio_files.extend(root_path.rglob(f"*{ext}"))

        return sorted(audio_files)

    def get_relative_path(self, absolute_path):
        """Convert absolute path to relative path from MUSIC_ROOT_PATH."""
        try:
            return str(Path(absolute_path).relative_to(MUSIC_ROOT_PATH))
        except ValueError:
            # If path is not relative to MUSIC_ROOT_PATH, return as-is
            return str(absolute_path)

    def _to_wav(self, audio_path: Path) -> Path:
        """Convert audio to mono 16k WAV for Whisper."""
        wav_path = audio_path.with_suffix(".wav")
        logger.debug(f"Converting {audio_path.name} to WAV format")

        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(audio_path),
                "-ar",
                "16000",
                "-ac",
                "1",
                str(wav_path),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        return wav_path

    def transcribe_audio(self, audio_file_path):
        """
        Transcribe audio file using either OpenAI Whisper or Faster-Whisper.

        Args:
            audio_file_path: Path to the audio file

        Returns:
            Transcription result with timestamps
        """
        logger.info(f"Transcribing: {audio_file_path}")

        if self.engine_type == "faster":
            # Faster-whisper requires WAV conversion
            wav_path = self._to_wav(Path(audio_file_path))
            try:
                segments, info = self.model.transcribe(
                    str(wav_path),
                    task="transcribe",
                    language=None,  # auto-detect
                    no_speech_threshold=0.3,
                )

                # Override Urdu with Hindi if needed
                if info.language == "ur":
                    logger.debug("Detected Urdu language, overriding with Hindi")
                    segments, info = self.model.transcribe(
                        str(wav_path),
                        task="transcribe",
                        language="hi",
                    )

                # Convert faster-whisper segments to openai-whisper format
                result = {
                    "text": " ".join([seg.text for seg in segments]),
                    "segments": [],
                }

                # Re-run to get segments list (faster-whisper returns generator)
                segments, _ = self.model.transcribe(
                    str(wav_path),
                    task="transcribe",
                    language=info.language if info.language != "ur" else "hi",
                )

                for seg in segments:
                    result["segments"].append(
                        {"start": seg.start, "end": seg.end, "text": seg.text}
                    )

                return result
            finally:
                if wav_path.exists():
                    wav_path.unlink()
                    logger.debug(f"Cleaned up temporary WAV file: {wav_path.name}")
        else:
            # OpenAI Whisper
            result = self.model.transcribe(
                str(audio_file_path),
                task="transcribe",
                word_timestamps=True,
                verbose=False,
                no_speech_threshold=0.3,
            )
            return result

    def format_lrc_timestamp(self, seconds):
        """
        Convert seconds to LRC timestamp format [mm:ss.xx]

        Args:
            seconds: Time in seconds

        Returns:
            Formatted timestamp string
        """
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"[{minutes:02d}:{secs:05.2f}]"

    def create_lrc_content(self, transcription_result):
        """
        Create LRC file content from Whisper transcription.

        Args:
            transcription_result: Result from Whisper transcription

        Returns:
            LRC formatted string
        """
        lrc_lines = []

        # Add metadata
        lrc_lines.append("[ti:Unknown Title]")
        lrc_lines.append("[ar:Unknown Artist]")
        lrc_lines.append("[al:Unknown Album]")
        lrc_lines.append(f"[by:Whisper AI - {datetime.now().strftime('%Y-%m-%d')}]")
        lrc_lines.append("")

        # Add timestamped lyrics
        for segment in transcription_result["segments"]:
            timestamp = self.format_lrc_timestamp(segment["start"])
            text = segment["text"].strip()
            lrc_lines.append(f"{timestamp}{text}")

        return "\n".join(lrc_lines)

    def save_lrc_file(self, audio_file_path, lrc_content):
        """
        Save LRC content to file with same name as audio file.

        Args:
            audio_file_path: Path to the audio file
            lrc_content: LRC formatted content
        """
        lrc_file_path = Path(audio_file_path).with_suffix(".lrc")
        with open(lrc_file_path, "w", encoding="utf-8") as f:
            f.write(lrc_content)
        logger.info(f"LRC file saved: {lrc_file_path}")

    def process_directory(self, root_directory):
        """
        Process all audio files in directory and generate LRC files.

        Args:
            root_directory: Root directory to process
        """
        audio_files = self.get_all_audio_files(root_directory)
        total_files = len(audio_files)

        logger.info(f"\nFound {total_files} audio files to process\n")

        for idx, audio_file in enumerate(audio_files, 1):
            try:
                relative_path = self.get_relative_path(audio_file)

                # Check if already processed
                if self.sql_utils.file_exists(relative_path):
                    logger.info(
                        f"[{idx}/{total_files}] Skipping (already processed): {audio_file.name}"
                    )
                    continue

                logger.info(f"\n[{idx}/{total_files}] Processing: {audio_file.name}")

                # Transcribe audio
                result = self.transcribe_audio(audio_file)

                # Extract raw text
                raw_text = result["text"]

                # Improve lyrics with LLM
                logger.info("Improving lyrics with Gemini...")
                improved_text = self.llm.improve_lyrics(raw_text, audio_file.name)

                # Create LRC content
                lrc_content = self.create_lrc_content(result)

                # Add improved lyrics as comment
                lrc_with_improved = (
                    f"{lrc_content}\n\n[Improved Lyrics]\n{improved_text}"
                )

                # Save LRC file
                self.save_lrc_file(audio_file, lrc_with_improved)

                # Record in database
                self.sql_utils.add_file(
                    file_location=relative_path,
                    date_transcribed=datetime.now(),
                    date_added=datetime.now(),
                )

                logger.info(f"Successfully processed: {audio_file.name}")

            except Exception as e:
                logger.error(f"Error processing {audio_file}: {e}", exc_info=True)
                continue

        logger.info(f"\n\nProcessing complete! Processed {total_files} files.")
