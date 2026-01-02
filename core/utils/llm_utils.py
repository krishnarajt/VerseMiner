from google import genai
from core.common_constants.constants import GEMINI_API_KEY, GEMINI_MODEL_ID


class RateLimitError(Exception):
    """Custom exception for API rate limit errors."""

    pass


class LLMUtils:
    def __init__(self):
        """
        Initialize the Gemini API client.
        Tools are intentionally NOT used to avoid strict model-ID constraints.
        """
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model_id = GEMINI_MODEL_ID

    def detect_and_enhance_lyric_line(self, lyric_text, file_name):
        """
        Process a single lyric line to get transliteration and translation.

        Args:
            lyric_text: Single line of lyrics without timestamp
            file_name: Name of the audio file for context

        Returns:
            String with transliteration and translation (2 lines minimum)

        Raises:
            RateLimitError: If API rate limit is exceeded
        """
        prompt = f"""Song: "{file_name}"
Lyric: {lyric_text}

Output exactly 2 lines with NO numbering or labels:
Line 1: Romanized/transliterated version
Line 2: English translation

Example:
तुम मेरे साथ हो
Output:
tum mere saath ho
you are with me"""
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
            )

            result = response.text.strip()

            # Remove any numbering that might have been added (1. 2. etc)
            lines = []
            for line in result.split("\n"):
                line = line.strip()
                # Remove leading numbers and dots
                if line and (
                    line[0].isdigit() or line.startswith("1.") or line.startswith("2.")
                ):
                    # Strip numbering like "1. " or "2. "
                    line = line.lstrip("0123456789. ")
                if line:
                    lines.append(line)

            # Accept any number of lines (should be at least 2)
            if len(lines) < 2:
                print(
                    f"Warning: Expected at least 2 lines but got {len(lines)} for: {lyric_text}"
                )
                # Return whatever we got
                return "\n".join(lines) if lines else ""

            if len(lines) > 2:
                print(f"Info: Got {len(lines)} lines (expected 2) for: {lyric_text}")

            return "\n".join(lines)

        except Exception as e:
            # Check if this is a rate limit error
            error_str = str(e).lower()
            if "rate" in error_str or "quota" in error_str or "429" in error_str:
                print(f"RATE LIMIT HIT: {e}")
                raise RateLimitError(f"API rate limit exceeded: {e}") from e

            print(f"Error calling Gemini API for line '{lyric_text}': {e}")
            return ""

    def improve_lyrics(self, raw_transcription, file_name):
        """
        Process each lyric line individually to add transliteration and translation.

        Args:
            raw_transcription: Full transcription text with timestamps
            file_name: Name of the audio file

        Returns:
            Enhanced lyrics with transliteration and translation for non-English lines
        """
        lines = raw_transcription.strip().split("\n")
        enhanced_lyrics = []

        for line in lines:
            line = line.strip()

            # Skip empty lines
            if not line:
                enhanced_lyrics.append(line)
                continue

            # Check if line has timestamp format [mm:ss.xx]
            if line.startswith("[") and "]" in line:
                # Extract timestamp and lyric text
                timestamp_end = line.index("]")
                timestamp = line[: timestamp_end + 1]
                lyric_text = line[timestamp_end + 1 :].strip()

                # Add original line
                enhanced_lyrics.append(line)

                # Skip if it's a metadata line or empty lyric
                if not lyric_text or lyric_text.startswith("["):
                    continue

                # Process the lyric line
                print(f"Processing: {lyric_text}")
                enhancement = self.detect_and_enhance_lyric_line(lyric_text, file_name)

                # If we got enhancement (non-English), add it with same timestamp
                if enhancement:
                    for enhanced_line in enhancement.split("\n"):
                        enhanced_lyrics.append(f"{timestamp} {enhanced_line.strip()}")
            else:
                # Non-timestamped line (metadata, etc.)
                enhanced_lyrics.append(line)

        return "\n".join(enhanced_lyrics)
