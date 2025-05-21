from typing import Dict
import pdfplumber
import docx
import re
from pathlib import Path

class ResumeParser:
    def __init__(self):
        # Regular expressions for common patterns
        self.patterns = {
            'email': r'[\w\.-]+@[\w\.-]+\.\w+',
            'phone': r'\+?\d{10,12}',
            'skills': r'python|javascript|react|node\.js|sql|aws'
        }

    def parse(self, file_path: str) -> Dict:
        """Parse resume and extract key information"""
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
        # Extract basic information
        info = {
            'email': self._find_pattern(text, self.patterns['email']),
            'phone': self._find_pattern(text, self.patterns['phone']),
            'education': [],
            'experience_years': None,
            'skills': self._extract_skills(text),
            'name': None,
            'location': None
        }
        
        return info

    def _find_pattern(self, text: str, pattern: str) -> str:
        """Find first match of a pattern in text"""
        match = re.search(pattern, text)
        return match.group() if match else ""

    def _extract_skills(self, text: str) -> list:
        """Extract technical skills"""
        skills = set()
        matches = re.finditer(self.patterns['skills'], text.lower())
        for match in matches:
            skills.add(match.group())
        return list(skills)
