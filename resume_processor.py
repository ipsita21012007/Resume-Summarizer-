import os
import re
import pdfplumber
from docx import Document
from typing import Dict, List, Optional
import io

class ResumeSummarizer:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
    
    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
        return text
    
    def extract_text_from_docx(self, docx_file) -> str:
        """Extract text from DOCX file"""
        text = ""
        try:
            doc = Document(docx_file)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        except Exception as e:
            raise Exception(f"Error reading DOCX: {str(e)}")
        return text
    
    def extract_text_from_txt(self, txt_file) -> str:
        """Extract text from TXT file"""
        try:
            if hasattr(txt_file, 'read'):
                content = txt_file.read()
                if isinstance(content, bytes):
                    text = content.decode('utf-8')
                else:
                    text = str(content)
            else:
                text = str(txt_file)
            return text
        except Exception as e:
            raise Exception(f"Error reading TXT file: {str(e)}")
    
    def extract_text(self, file) -> str:
        """Extract text from various file formats"""
        filename = file.name.lower() if hasattr(file, 'name') else "uploaded_file"
        
        if filename.endswith('.pdf'):
            return self.extract_text_from_pdf(file)
        elif filename.endswith('.docx'):
            return self.extract_text_from_docx(file)
        elif filename.endswith('.txt'):
            return self.extract_text_from_txt(file)
        else:
            # Try to detect file type
            try:
                return self.extract_text_from_txt(file)
            except:
                raise Exception("Unsupported file format. Please upload PDF, DOCX, or TXT.")
    
    def clean_text(self, text: str) -> str:
        """Clean and preprocess resume text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?;:()\-@]', '', text)
        return text.strip()
    
    def parse_resume_sections(self, text: str) -> Dict[str, str]:
        """Parse resume into sections using regex patterns"""
        sections = {
            'contact': '',
            'summary': '',
            'experience': '',
            'education': '',
            'skills': '',
            'projects': '',
            'certifications': ''
        }
        
        # Common section headers pattern
        section_patterns = {
            'contact': r'(?:contact|personal|details)[\s\S]*?(?=\n\s*\n|[A-Z][a-z]+:)',
            'summary': r'(?:summary|objective|profile)[\s\S]*?(?=\n\s*\n|[A-Z][a-z]+:)',
            'experience': r'(?:experience|work\s*history|employment)[\s\S]*?(?=\n\s*\n|[A-Z][a-z]+:)',
            'education': r'(?:education|academic)[\s\S]*?(?=\n\s*\n|[A-Z][a-z]+:)',
            'skills': r'(?:skills|technical\s*skills|competencies)[\s\S]*?(?=\n\s*\n|[A-Z][a-z]+:)',
            'projects': r'(?:projects|portfolio)[\s\S]*?(?=\n\s*\n|[A-Z][a-z]+:)',
            'certifications': r'(?:certifications|certificates)[\s\S]*?(?=\n\s*\n|[A-Z][a-z]+:)'
        }
        
        text_lower = text.lower()
        
        for section, pattern in section_patterns.items():
            matches = re.findall(pattern, text_lower, re.IGNORECASE | re.MULTILINE)
            if matches:
                sections[section] = ' '.join(matches)
        
        return sections
    
    def generate_basic_summary(self, resume_text: str, sections: Dict[str, str]) -> Dict[str, str]:
        """Generate basic summary"""
        summary_parts = []
        
        if sections['summary']:
            summary_parts.append(f"PROFESSIONAL SUMMARY:\n{sections['summary']}")
        
        if sections['experience']:
            exp_preview = sections['experience'][:300] + "..." if len(sections['experience']) > 300 else sections['experience']
            summary_parts.append(f"EXPERIENCE HIGHLIGHTS:\n{exp_preview}")
        
        if sections['skills']:
            skills_preview = sections['skills'][:200] + "..." if len(sections['skills']) > 200 else sections['skills']
            summary_parts.append(f"KEY SKILLS:\n{skills_preview}")
        
        if sections['education']:
            edu_preview = sections['education'][:200] + "..." if len(sections['education']) > 200 else sections['education']
            summary_parts.append(f"EDUCATION:\n{edu_preview}")
        
        full_summary = "\n\n".join(summary_parts) if summary_parts else "No significant sections found in the resume."
        
        insights = """
        SUGGESTED IMPROVEMENTS:
        • Add quantifiable achievements and metrics
        • Include specific technologies and tools used
        • Add project descriptions with outcomes and impact
        • Consider adding a professional summary at the top
        • Include relevant certifications and training
        
        💡 Tip: For AI-powered insights and detailed analysis, add your OpenAI API key in the sidebar.
        """
        
        return {
            'full_summary': full_summary,
            'insights': insights,
            'extracted_sections': sections
        }
    
    def extract_key_information(self, text: str) -> Dict[str, List[str]]:
        """Extract key information using regex patterns"""
        # Email pattern
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        
        # Phone pattern (basic)
        phones = re.findall(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
        
        # Education degrees
        degrees = re.findall(r'\b(B\.?S\.?|B\.?A\.?|B\.?Tech|M\.?S\.?|M\.?A\.?|M\.?Tech|PhD|Bachelor|Master|Doctorate)\b', text, re.IGNORECASE)
        
        # Common skills
        common_skills = [
            'python', 'java', 'javascript', 'sql', 'aws', 'docker', 'kubernetes',
            'machine learning', 'ai', 'data analysis', 'project management',
            'agile', 'scrum', 'react', 'node.js', 'mongodb', 'postgresql',
            'html', 'css', 'typescript', 'angular', 'vue', 'express', 'django',
            'flask', 'fastapi', 'git', 'jenkins', 'linux', 'windows', 'macos'
        ]
        
        found_skills = []
        for skill in common_skills:
            if re.search(r'\b' + re.escape(skill) + r'\b', text, re.IGNORECASE):
                found_skills.append(skill.title())
        
        return {
            'emails': emails[:3],  # Limit to first 3
            'phones': phones[:3],   # Limit to first 3
            'degrees': list(set(degrees)),
            'skills': found_skills[:15]  # Limit to top 15 skills
        }
    
    def process_resume(self, file) -> Dict:
        """Main method to process resume and generate summary"""
        # Extract text
        raw_text = self.extract_text(file)
        
        # Clean text
        cleaned_text = self.clean_text(raw_text)
        
        # Parse sections
        sections = self.parse_resume_sections(cleaned_text)
        
        # Extract key information
        key_info = self.extract_key_information(cleaned_text)
        
        # Generate basic summary
        summary = self.generate_basic_summary(cleaned_text, sections)
        
        return {
            'raw_text': raw_text,
            'cleaned_text': cleaned_text,
            'sections': sections,
            'key_info': key_info,
            'summary': summary,
            'text_length': len(cleaned_text),
            'word_count': len(cleaned_text.split())
        }