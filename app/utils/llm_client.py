from openai import OpenAI
from typing import List, Dict, Any
import json
from app.models.schemas import ResumeData
import os
from app.config import settings

class LLMClient:
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = "gpt-4-1106-preview"  # Supports structured output
    
    def parse_resume(self, resume_text: str) -> ResumeData:
        """Extract structured resume data using LLM"""
        
        system_prompt = """You are an expert resume parser. Extract the following information from the resume text:
        1. Name (full name)
        2. Contact information (email, phone if available)
        3. Skills (technical skills, tools, programming languages, soft skills)
        4. Work Experience (each position with title, company, dates, description)
        5. Education (each degree with institution, field, dates)
        6. Summary/Objective (if present)
        
        Return the data in a structured JSON format."""
        
        user_prompt = f"""Parse this resume text and extract structured information:
        
        {resume_text}
        
        Format the response as a JSON object matching this schema:
        {{
            "name": "string",
            "email": "string or null",
            "phone": "string or null",
            "skills": ["list", "of", "skills"],
            "experience": [
                {{
                    "title": "string",
                    "company": "string",
                    "start_date": "string or null",
                    "end_date": "string or null",
                    "description": "string or null",
                    "location": "string or null"
                }}
            ],
            "education": [
                {{
                    "degree": "string",
                    "institution": "string",
                    "field_of_study": "string or null",
                    "start_date": "string or null",
                    "end_date": "string or null",
                    "gpa": "number or null"
                }}
            ],
            "summary": "string or null",
            "raw_text": "original text"
        }}
        
        Be accurate and thorough. If information is missing, use null."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            parsed_data = json.loads(response.choices[0].message.content)
            parsed_data['raw_text'] = resume_text
            return ResumeData(**parsed_data)
            
        except Exception as e:
            raise Exception(f"Failed to parse resume: {str(e)}")
    
    def generate_job_search_query(self, resume_data: ResumeData, user_query: str = None) -> Dict[str, Any]:
        """Generate optimized job search query based on resume"""
        
        prompt = f"""Based on this resume data, create an optimized job search query.

Resume Data:
- Name: {resume_data.name}
- Skills: {', '.join(resume_data.skills[:10])}
- Experience: {len(resume_data.experience)} positions
- Education: {len(resume_data.education)} degrees

User Query: {user_query if user_query else 'Find relevant job opportunities'}

Generate search parameters including:
1. Search keywords (combining skills and experience)
2. Suggested job titles
3. Experience level
4. Location preferences (if any in resume)

Return as JSON: {{"keywords": ["list"], "job_titles": ["list"], "experience_level": "string", "location": "string or null"}}"""
        
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        return json.loads(response.choices[0].message.content)
    
    # ==============================================================
# 📌 LLM_CLIENT.PY — WHAT THIS FILE DOES & WHY
# ==============================================================
#
# LLMClient class handles all interactions with the OpenAI LLM
# for the Resume Parser & Job Matcher backend.
#
# -------------------------------
# 🔹 Methods Overview
# -------------------------------
#
# __init__()
#   → Initializes OpenAI client with API key
#   → Sets GPT model for structured outputs
#
# parse_resume(resume_text)
#   → Sends resume text to GPT
#   → Extracts structured data: ResumeData (name, skills, experience, education, summary, etc.)
#   → Returns a typed Pydantic object
#
# generate_job_search_query(resume_data, user_query)
#   → Generates optimized job search parameters based on resume
#   → Returns JSON with keywords, suggested job titles, experience level, and location
#
# -------------------------------
# 🔹 Why This File Matters
# -------------------------------
# ✓ Converts unstructured resume text into structured data automatically
# ✓ Uses AI to optimize job search queries
# ✓ Centralizes all OpenAI logic in one clean class
# ✓ Ensures consistent, typed responses for the backend
#
# ==============================================================
