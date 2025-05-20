from typing import Dict, Optional
import pdfplumber
import docx
import re
import spacy
from pathlib import Path

class ResumeParser:
    def __init__(self):
        # Load spaCy model for NER
        self.nlp = spacy.load("en_core_web_sm")
        
        # Regular expressions for common patterns
        self.patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b(\+\d{1,3}[-.]?)?\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'education': r'(?i)(Bachelor|Master|PhD|B\.?E\.?|B\.?Tech|M\.?E\.?|M\.?Tech)',
            'experience_years': r'(\d+)\+?\s*(?:years?|yrs?)',
            'skills': r'(?i)(python|java|javascript|sql|react|node\.?js|aws|docker|kubernetes|ai|ml)'
        }

    def parse_resume(self, file_path: str) -> Dict:
        """Parse resume file and extract relevant information"""
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.pdf':
            return self._parse_pdf(file_path)
        elif file_ext in ['.docx', '.doc']:
            return self._parse_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")

    def _parse_pdf(self, file_path: str) -> Dict:
        """Parse PDF resume"""
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        
        return self._extract_information(text)

    def _parse_docx(self, file_path: str) -> Dict:
        """Parse DOCX resume"""
        doc = docx.Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        
        return self._extract_information(text)

    def _extract_information(self, text: str) -> Dict:
        """Extract relevant information from text using NLP and regex"""
        # Process text with spaCy
        doc = self.nlp(text)
        
        # Extract basic information
        info = {
            'email': self._find_pattern(text, self.patterns['email']),
            'phone': self._find_pattern(text, self.patterns['phone']),
            'education': [],
            'experience_years': self._extract_experience_years(text),
            'skills': self._extract_skills(text),
            'name': self._extract_name(doc),
            'location': self._extract_location(doc)
        }
        
        # Extract education details
        education_matches = re.finditer(self.patterns['education'], text)
        for match in education_matches:
            # Get the line containing education information
            line_start = max(0, match.start() - 50)
            line_end = min(len(text), match.end() + 100)
            education_line = text[line_start:line_end]
            info['education'].append(education_line.strip())
        
        return info

    def _find_pattern(self, text: str, pattern: str) -> Optional[str]:
        """Find first match of a pattern in text"""
        match = re.search(pattern, text)
        return match.group() if match else None

    def _extract_experience_years(self, text: str) -> Optional[int]:
        """Extract years of experience"""
        match = re.search(self.patterns['experience_years'], text)
        if match:
            return int(match.group(1))
        return None

    def _extract_skills(self, text: str) -> list:
        """Extract technical skills"""
        skills = set()
        matches = re.finditer(self.patterns['skills'], text.lower())
        for match in matches:
            skills.add(match.group())
        return list(skills)

    def _extract_name(self, doc) -> Optional[str]:
        """Extract name using NER"""
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                return ent.text
        return None

    def _extract_location(self, doc) -> Optional[str]:
        """Extract location using NER"""
        for ent in doc.ents:
            if ent.label_ in ["GPE", "LOC"]:
                return ent.text
        return None

    def evaluate_resume_match(self, resume_info: Dict, job_requirements: Dict) -> float:
        """Calculate match percentage between resume and job requirements"""
        score = 0
        total_points = 0
        
        # Check skills match
        if 'required_skills' in job_requirements:
            total_points += len(job_requirements['required_skills'])
            for skill in job_requirements['required_skills']:
                if skill.lower() in [s.lower() for s in resume_info['skills']]:
                    score += 1
        
        # Check experience match
        if 'min_experience' in job_requirements and resume_info['experience_years']:
            total_points += 1
            if resume_info['experience_years'] >= job_requirements['min_experience']:
                score += 1
        
        # Check education match
        if 'education_level' in job_requirements:
            total_points += 1
            education_text = ' '.join(resume_info['education']).lower()
            if job_requirements['education_level'].lower() in education_text:
                score += 1
        
        return (score / total_points * 100) if total_points > 0 else 0
