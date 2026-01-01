import google.generativeai as genai
from common_constants.constants import GEMINI_API_KEY


class LLMUtils:
    def __init__(self):
        """Initialize the Gemini API client."""
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel("gemini-pro")

    def improve_lyrics(self, raw_transcription, file_name):
        """
        Use Gemini to improve and format the raw transcription.

        Args:
            raw_transcription: Raw text from Whisper
            file_name: Name of the audio file

        Returns:
            Improved and formatted lyrics
        """
        prompt = f"""You are a lyrics formatter. Given the raw transcription below from a song file named "{file_name}", please:

1. Fix any obvious transcription errors
2. Add proper capitalization and punctuation
3. Structure the text into verses, chorus, bridge, etc. if applicable
4. Remove any non-lyrical content (like "[Music]", "[Applause]", etc.)
5. Ensure the output is clean and properly formatted

Raw transcription:
{raw_transcription}

Please provide only the cleaned and formatted lyrics, nothing else."""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            return raw_transcription  # Return original if API fails
