from google import genai
from core.common_constants.constants import GEMINI_API_KEY, GEMINI_MODEL_ID


class LLMUtils:
    def __init__(self):
        """
        Initialize the Gemini API client.
        Tools are intentionally NOT used to avoid strict model-ID constraints.
        """
        self.client = genai.Client(api_key=GEMINI_API_KEY)

        # Alias is OK when tools are not used
        self.model_id = GEMINI_MODEL_ID

    def improve_lyrics(self, raw_transcription, file_name):
        """
        Clean and improve Whisper-generated timestamped lyrics
        while preserving timestamps and structure.

        NOTE:
        - No external search
        - No lyric fetching
        - Improvements are based purely on linguistic cleanup
        """

        prompt = f"""You are an expert music linguist and LRC (timed lyrics) formatter.

Given the raw timestamped transcription below from an audio file named "{file_name}", please:

1. **Preserve Timestamps**:
   - Every lyric line starts with a timestamp like [mm:ss.xx]
   - DO NOT change, remove, or reorder timestamps.

2. **Clean Lyrics**:
   - Fix obvious transcription errors.
   - Normalize spelling and casing.
   - Remove non-lyrical noise like [Music], [Applause], [Instrumental].

3. **Structure**:
   - Keep Verse / Chorus / Bridge headers if present.
   - Do not invent new sections.

4. **Language Handling**:
   - Automatically detect the language of each lyric line.
   - If the lyric is in English, output only the cleaned lyric line.
   - If the lyric is NOT in English:
     - Output the original lyric in its native script.
     - Add a **transliteration into Latin (Roman) script** on the next line.
     - Add an **English translation** on the following line.
     - All three lines MUST repeat the exact same timestamp.

Output format examples:

English lyric:
[00:12.34] Original English lyric line

Non-English lyric:
[00:12.34] Original lyric line (native script)
[00:12.34] Transliteration (Latin script)
[00:12.34] English translation

Raw transcription:
{raw_transcription}

Return ONLY the formatted lyrics. No explanations, no filler text.
"""
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
            )
            print(response.text)
            return response.text

        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            return raw_transcription
