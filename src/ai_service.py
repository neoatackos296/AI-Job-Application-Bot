from openai import OpenAI
from config import Config

class AIService:
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
    
    def customize_resume(self, job_description: str, base_resume: str) -> str:
        """Customize resume based on job description using AI"""
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert resume customization assistant."},
                {"role": "user", "content": f"""
                Please customize this resume for the following job description. 
                Highlight relevant skills and experience, and adjust the wording to match the job requirements.
                
                Job Description:
                {job_description}
                
                Base Resume:
                {base_resume}
                """}
            ]
        )
        return response.choices[0].message.content
    
    def generate_cover_letter(self, job_description: str, company_name: str) -> str:
        """Generate a customized cover letter using AI"""
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert cover letter writer."},
                {"role": "user", "content": f"""
                Please write a professional cover letter for the following job.
                Make it engaging, specific to the company, and highlight relevant skills.
                
                Company: {company_name}
                Job Description:
                {job_description}
                """}
            ]
        )
        return response.choices[0].message.content
    
    def answer_application_question(self, question: str, context: str) -> str:
        """Generate an answer for a job application question using AI"""
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert at answering job application questions professionally."},
                {"role": "user", "content": f"""
                Please provide a professional answer to this job application question.
                Use the context provided to make the answer specific and relevant.
                
                Question: {question}
                Context: {context}
                """}
            ]
        )
        return response.choices[0].message.content
