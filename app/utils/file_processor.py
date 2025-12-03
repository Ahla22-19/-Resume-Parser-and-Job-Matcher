import pdfplumber
from docx import Document
import tempfile
import os
from typing import Optional

class FileProcessor:
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    
    @staticmethod
    def extract_text_from_docx(file_path: str) -> str:
        """Extract text from DOCX file"""
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
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
    def save_uploaded_file(uploaded_file, temp_dir: str = None) -> tuple:
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
    
    # ==============================================================
# 📌 FILE_PROCESSOR.PY — WHAT THIS FILE DOES & WHY
# ==============================================================
#
# FileProcessor class handles all resume file operations:
#   1️⃣ Save uploaded files safely to a temporary folder
#   2️⃣ Extract text from PDFs using pdfplumber
#   3️⃣ Extract text from DOCX using python-docx
#   4️⃣ Automatically select extraction method based on file type
#
# This is essential for the Resume Parser & Job Matcher backend
# because the AI agent needs clean text to analyze resumes.
#
# -------------------------------
# 🔹 Methods Overview
# -------------------------------
# extract_text_from_pdf(file_path)
#   → Reads every page of a PDF and combines text into a single string
#
# extract_text_from_docx(file_path)
#   → Reads all paragraphs in a Word file and combines text
#
# extract_text_from_file(file_path, file_type)
#   → Chooses correct extraction method based on MIME type
#   → Raises error if file type is unsupported
#
# save_uploaded_file(uploaded_file, temp_dir=None)
#   → Saves uploaded file to a temporary location
#   → Returns (temporary_file_path, content_type)
#
# -------------------------------
# 🔹 Why This File Matters
# -------------------------------
# ✓ Separates file handling logic from API routes
# ✓ Ensures consistent text extraction for AI
# ✓ Supports multiple file types safely
# ✓ Works seamlessly with FastAPI UploadFile
#
# ==============================================================
