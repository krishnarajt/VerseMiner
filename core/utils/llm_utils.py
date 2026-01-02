import json
from google import genai
from core.common_constants.constants import GEMINI_API_KEY, GEMINI_MODEL_ID


class LLMUtils:
    def __init__(self):
        """
        Initialize the Gemini API client.
        Using native JSON support to ensure structured data retrieval.
        """
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model_id = GEMINI_MODEL_ID

    def improve_lyrics(self, raw_transcription, file_name):
        """
        Clean and improve transcription using native JSON mode for reliability.
        Processes lines individually to ensure timestamps remain mapped correctly.
        """
        # Split raw transcription into lines to provide context with indices
        lines = [line.strip() for line in raw_transcription.split("\n") if line.strip()]

        # Prepare the input data for the model
        input_data = []
        for i, line in enumerate(lines):
            input_data.append({"index": i, "raw_text": line})

        prompt = f"""You are an expert music linguist. Audio file: "{file_name}".
        
        Process the following timestamped lyric lines. 
        - Preserve the timestamp at the start of each line.
        - Fix transcription errors and normalize casing.
        - Determine if the line is English or Non-English.
        
        For each line:
        1. If English: Provide only the 'cleaned_lyric'.
        2. If Non-English: Provide 'cleaned_lyric', 'transliteration' (Latin script), and 'translation' (English).
        
        Input Data:
        {json.dumps(input_data)}
        """

        # Define the expected JSON schema
        response_schema = {
            "type": "OBJECT",
            "properties": {
                "processed_lines": {
                    "type": "ARRAY",
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "index": {"type": "NUMBER"},
                            "cleaned_lyric": {"type": "STRING"},
                            "transliteration": {
                                "type": "STRING",
                                "description": "Only for non-English",
                            },
                            "translation": {
                                "type": "STRING",
                                "description": "Only for non-English",
                            },
                            "is_english": {"type": "BOOLEAN"},
                        },
                        "required": ["index", "cleaned_lyric", "is_english"],
                    },
                }
            },
        }

        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": response_schema,
                },
            )

            # Parse the JSON response
            result = json.loads(response.text)
            processed_map = {
                item["index"]: item for item in result.get("processed_lines", [])
            }

            final_output = []

            # Reconstruct the output line by line based on original indices
            for i, original_line in enumerate(lines):
                # Extract timestamp from original line (e.g., "[00:12.34]")
                timestamp = (
                    original_line.split("]")[0] + "]" if "]" in original_line else ""
                )

                processed = processed_map.get(i)
                if not processed:
                    final_output.append(original_line)
                    continue

                if processed.get("is_english"):
                    final_output.append(f"{timestamp} {processed['cleaned_lyric']}")
                else:
                    # Multi-line output for non-English
                    final_output.append(f"{timestamp} {processed['cleaned_lyric']}")
                    if processed.get("transliteration"):
                        final_output.append(
                            f"{timestamp} {processed['transliteration']}"
                        )
                    if processed.get("translation"):
                        final_output.append(f"{timestamp} {processed['translation']}")

            return "\n".join(final_output)

        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            return raw_transcription
