SYSTEM_PROMPT = """
You are a professional technical recruiter.
You evaluate resumes objectively and strictly.
Return output ONLY in valid JSON format.
"""


def resume_screening_prompt(resume_text: str, job_description: str) -> str:
    return f"""
Compare the resume with the job description.

Job Description:
{job_description}

Resume:
{resume_text}

IMPORTANT:
- Return ONLY valid JSON.
- Do NOT include any text outside the JSON.
- Format exactly like this:

{{
  "score": number between 0 and 100,
  "strengths": [list of strings],
  "weaknesses": [list of strings],
  "recommendation": "Hire" or "Reject"
}}
"""
