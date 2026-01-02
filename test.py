from google import genai
from core.common_constants.constants import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)
print("Listing available models:")
try:
    # Use client.models.list() - it returns a pager of Model objects
    for model in client.models.list():
        # The attribute is 'name' (e.g., 'models/gemini-1.5-flash')
        # or 'base_model_id' (e.g., 'gemini-1.5-flash')
        print(f"Model Name: {model.name}")
except Exception as e:
    print(f"Error listing models: {e}")

#
response = client.models.generate_content(
    model="gemma-3-27b-it",
    contents="Explain how AI works in a few words",
)

print(response.text)
