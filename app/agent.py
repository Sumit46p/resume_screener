import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

from app.schemas import ResumeEvaluation
from app.prompts import SYSTEM_PROMPT, resume_screening_prompt

# Load API key
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Choose the model
model = genai.GenerativeModel(model_name="gemini-2.5-flash")

def screen_resume(resume_text: str, job_description: str) -> ResumeEvaluation:
    prompt = resume_screening_prompt(resume_text, job_description)
    
    try:
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.2,
                "response_mime_type": "application/json"
            }
        )

        content = response.text.strip()

        # Try to extract JSON even if extra text exists
        start = content.find("{")
        end = content.rfind("}") + 1
        json_text = content[start:end]
        
        data = json.loads(json_text)
        return ResumeEvaluation(**data)

    except json.JSONDecodeError:
        # AI returned invalid JSON
        return ResumeEvaluation(
            score=0,
            strengths=[],
            weaknesses=[],
            recommendation="Reject"
        )
    except Exception as e:
        print("Error in AI agent:", e)
        return ResumeEvaluation(
            score=0,
            strengths=[],
            weaknesses=[],
            recommendation="Reject"
        )
