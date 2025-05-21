from .config import Config
from openai import OpenAI
import logging
from typing import Optional

class AIService:
    """Service for AI-powered operations like resume customization and question answering"""
    
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.logger = logging.getLogger(__name__)

    async def customize_resume(self, resume_text: str, job_description: str) -> str:
        """Customize resume based on job description"""
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional resume writer."},
                    {"role": "user", "content": f"Customize this resume for the job:\n\nResume:\n{resume_text}\n\nJob Description:\n{job_description}"}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"Error customizing resume: {str(e)}")
            return resume_text

    async def answer_question(self, question: str, context: Optional[str] = None) -> str:
        """Generate an answer for a job application question"""
        try:
            prompt = f"Question: {question}\n"
            if context:
                prompt += f"Context: {context}\n"
            
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional job applicant."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"Error answering question: {str(e)}")
            return ""
