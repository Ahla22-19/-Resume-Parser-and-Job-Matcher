import pdfplumber
from docx import Document
import tempfile
import os
from typing import Optional, Tuple

class FileProcessor:
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            raise Exception(f"PDF extraction failed: {str(e)}")
        return text
    
    @staticmethod
    def extract_text_from_docx(file_path: str) -> str:
        """Extract text from DOCX file"""
        text = ""
        try:
            doc = Document(file_path)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        except Exception as e:
            raise Exception(f"DOCX extraction failed: {str(e)}")
        return text
    
    @staticmethod
    def extract_text_from_file(file_path: str, file_type: str) -> str:
        """Extract text based on file type"""
        if file_type == "application/pdf":
            return FileProcessor.extract_text_from_pdf(file_path)
        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return FileProcessor.extract_text_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    
    @staticmethod
    def save_uploaded_file(uploaded_file, temp_dir: str = None) -> Tuple[str, str]:
        """Save uploaded file to temporary location"""
        if temp_dir is None:
            temp_dir = tempfile.gettempdir()
        
        # Create a temporary file
        file_ext = uploaded_file.filename.split('.')[-1]
        temp_file = tempfile.NamedTemporaryFile(
            delete=False, 
            dir=temp_dir, 
            suffix=f'.{file_ext}'
        )
        
        # Write uploaded content
        content = uploaded_file.file.read()
        temp_file.write(content)
        temp_file.close()
        
        return temp_file.name, uploaded_file.content_type