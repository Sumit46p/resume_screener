from pydantic import BaseModel
from typing import List


class ResumeInput(BaseModel):
    resume_text: str
    job_description: str


class ResumeEvaluation(BaseModel):
    score: int
    strengths: List[str]
    weaknesses: List[str]
    recommendation: str
