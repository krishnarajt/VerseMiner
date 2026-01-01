import os
import whisper
from pathlib import Path
from datetime import datetime
from common_constants.constants import WHISPER_MODEL, AUDIO_EXTENSIONS, MUSIC_ROOT_PATH
from sql_utils import SQLUtils
from llm_utils import LLMUtils


class LyricsGenerator:
    def __init__(self):
        """Initialize Whisper model and LLM utilities."""
        print(f"Loading Whisper model: {WHISPER_MODEL}")
        self.model = whisper.load_model(WHISPER_MODEL)
        self.llm = LLMUtils()
        self.sql_utils = SQLUtils()
        print("Whisper model loaded successfully")

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

    def transcribe_audio(self, audio_file_path):
        """
        Transcribe audio file using Whisper.

        Args:
            audio_file_path: Path to the audio file

        Returns:
            Transcription result with timestamps
        """
        print(f"Transcribing: {audio_file_path}")
        result = self.model.transcribe(
            str(audio_file_path), task="transcribe", word_timestamps=True, verbose=False
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
        print(f"LRC file saved: {lrc_file_path}")

    def process_directory(self, root_directory):
        """
        Process all audio files in directory and generate LRC files.

        Args:
            root_directory: Root directory to process
        """
        audio_files = self.get_all_audio_files(root_directory)
        total_files = len(audio_files)

        print(f"\nFound {total_files} audio files to process\n")

        for idx, audio_file in enumerate(audio_files, 1):
            try:
                relative_path = self.get_relative_path(audio_file)

                # Check if already processed
                if self.sql_utils.file_exists(relative_path):
                    print(
                        f"[{idx}/{total_files}] Skipping (already processed): {audio_file.name}"
                    )
                    continue

                print(f"\n[{idx}/{total_files}] Processing: {audio_file.name}")

                # Transcribe audio
                result = self.transcribe_audio(audio_file)

                # Extract raw text
                raw_text = result["text"]

                # Improve lyrics with LLM
                print("Improving lyrics with Gemini...")
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

                print(f"Successfully processed: {audio_file.name}")

            except Exception as e:
                print(f"Error processing {audio_file}: {e}")
                continue

        print(f"\n\nProcessing complete! Processed {total_files} files.")
