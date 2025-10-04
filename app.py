import streamlit as st
import os
import re
from io import StringIO

# Configure the page first
st.set_page_config(
    page_title="Resume Summarizer",
    page_icon="📄",
    layout="wide"
)

# Simple Resume Processor without external dependencies
class SimpleResumeSummarizer:
    def extract_text(self, file):
        """Extract text from file or text input"""
        if hasattr(file, 'read'):
            if hasattr(file, 'name'):
                filename = file.name.lower()
                if filename.endswith('.txt'):
                    content = file.read()
                    if isinstance(content, bytes):
                        return content.decode('utf-8')
                    return str(content)
            # Treat as text
            content = file.read()
            return str(content)
        return str(file)
    
    def clean_text(self, text):
        """Clean the text"""
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s.,!?;:()\-@]', '', text)
        return text.strip()
    
    def extract_emails(self, text):
        """Extract email addresses"""
        return re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    
    def extract_phones(self, text):
        """Extract phone numbers"""
        return re.findall(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
    
    def extract_skills(self, text):
        """Extract common skills"""
        common_skills = [
            'python', 'java', 'javascript', 'sql', 'aws', 'docker', 'kubernetes',
            'machine learning', 'ai', 'data analysis', 'project management',
            'agile', 'scrum', 'react', 'node.js', 'mongodb', 'postgresql',
            'html', 'css', 'typescript', 'angular', 'vue'
        ]
        found_skills = []
        for skill in common_skills:
            if re.search(r'\b' + re.escape(skill) + r'\b', text, re.IGNORECASE):
                found_skills.append(skill.title())
        return found_skills
    
    def generate_summary(self, text):
        """Generate a basic summary"""
        sections = {
            'experience': self.extract_section(text, ['experience', 'work', 'employment']),
            'education': self.extract_section(text, ['education', 'academic']),
            'skills': self.extract_section(text, ['skills', 'technical']),
            'summary': self.extract_section(text, ['summary', 'objective', 'profile'])
        }
        
        summary_parts = []
        
        if sections['summary']:
            summary_parts.append(f"**Professional Summary:**\n{sections['summary'][:300]}...")
        
        if sections['experience']:
            summary_parts.append(f"**Experience:**\n{sections['experience'][:400]}...")
        
        if sections['skills']:
            summary_parts.append(f"**Skills:**\n{sections['skills'][:200]}...")
        
        if sections['education']:
            summary_parts.append(f"**Education:**\n{sections['education'][:200]}...")
        
        return "\n\n".join(summary_parts) if summary_parts else "No significant sections found."
    
    def extract_section(self, text, keywords):
        """Extract section based on keywords"""
        text_lower = text.lower()
        for keyword in keywords:
            # Simple pattern to find content after section headers
            pattern = rf'{keyword}[^a-z]*?([a-z].*?)(?=\n\s*\n|[A-Z][a-z]+\:|$)'
            matches = re.findall(pattern, text_lower, re.IGNORECASE | re.DOTALL)
            if matches:
                return matches[0].strip()
        return ""

def main():
    st.title("📄 Simple Resume Summarizer")
    st.markdown("Upload your resume or paste text to get a quick summary!")
    
    # Initialize session state
    if 'summarizer' not in st.session_state:
        st.session_state.summarizer = SimpleResumeSummarizer()
    if 'processed' not in st.session_state:
        st.session_state.processed = False
    
    # Sidebar
    with st.sidebar:
        st.header("About")
        st.markdown("""
        This tool helps you:
        - Extract key information from resumes
        - Identify skills and experience
        - Generate quick summaries
        - No external dependencies needed!
        """)
        
        if st.button("Use Sample Resume"):
            sample_text = """
            JOHN DOE
            Software Engineer
            Email: john.doe@email.com | Phone: (555) 123-4567
            
            SUMMARY
            Experienced software developer with 5+ years in web development.
            Strong skills in Python, JavaScript, and cloud technologies.
            
            EXPERIENCE
            Senior Developer - Tech Company (2020-Present)
            - Developed web applications using Python and React
            - Led team of 4 developers
            - Improved performance by 40%
            
            EDUCATION
            BS Computer Science - University (2014-2018)
            """
            st.session_state.sample_text = sample_text
            st.rerun()
    
    # Main content
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("Input")
        
        input_method = st.radio("Choose input method:", ["Text Input", "File Upload"])
        
        if input_method == "Text Input":
            resume_text = st.text_area(
                "Paste your resume text:",
                height=300,
                value=st.session_state.get('sample_text', ''),
                placeholder="Paste your resume content here..."
            )
            
            if st.button("Analyze Text") and resume_text:
                with st.spinner("Analyzing..."):
                    try:
                        st.session_state.text = resume_text
                        st.session_state.processed = True
                        st.success("Analysis complete!")
                    except Exception as e:
                        st.error(f"Error: {e}")
        
        else:  # File Upload
            uploaded_file = st.file_uploader("Upload text file", type=['txt'])
            
            if uploaded_file is not None:
                if st.button("Analyze File"):
                    with st.spinner("Analyzing file..."):
                        try:
                            text_content = st.session_state.summarizer.extract_text(uploaded_file)
                            st.session_state.text = text_content
                            st.session_state.processed = True
                            st.success("File analyzed successfully!")
                        except Exception as e:
                            st.error(f"Error reading file: {e}")
    
    with col2:
        st.header("Results")
        
        if st.session_state.get('processed', False) and st.session_state.get('text'):
            text = st.session_state.text
            cleaned_text = st.session_state.summarizer.clean_text(text)
            
            # Display metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Words", len(cleaned_text.split()))
            with col2:
                st.metric("Characters", len(cleaned_text))
            with col3:
                st.metric("Lines", len(text.split('\n')))
            
            # Extract information
            emails = st.session_state.summarizer.extract_emails(text)
            phones = st.session_state.summarizer.extract_phones(text)
            skills = st.session_state.summarizer.extract_skills(text)
            
            # Display extracted info
            st.subheader(" Contact Information")
            if emails:
                st.write("Emails:", ", ".join(emails))
            else:
                st.write("No emails found")
                
            if phones:
                st.write("Phones:", ", ".join(phones[:2]))
            else:
                st.write("No phone numbers found")
            
            st.subheader("Skills Found")
            if skills:
                st.write(", ".join(skills))
            else:
                st.write("No specific skills detected")
            
            st.subheader(" Summary")
            summary = st.session_state.summarizer.generate_summary(text)
            st.write(summary)
            
            # Raw text preview
            with st.expander("View processed text"):
                st.text_area("Cleaned text", cleaned_text[:1000] + "..." if len(cleaned_text) > 1000 else cleaned_text, height=200)
            
            # Clear button
            if st.button("Analyze Another"):
                st.session_state.processed = False
                st.session_state.text = ""
                st.rerun()
        
        else:
            st.info(" Enter some text or upload a file to see analysis results!")

if __name__ == "__main__":
    main()