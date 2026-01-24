import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Use the model directly
model = genai.GenerativeModel(model_name="gemini-2.5-flash")

response = model.generate_content(
    prompt="Say hello",
    generation_config={
        "temperature": 0.0
    }
)

print(response.text)
