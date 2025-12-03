from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import date

# Resume Parsing Models
class Experience(BaseModel):
    title: str
    company: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None

class Education(BaseModel):
    degree: str
    institution: str
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    gpa: Optional[float] = None

class ResumeData(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: List[str]
    experience: List[Experience]
    education: List[Education]
    summary: Optional[str] = None
    raw_text: Optional[str] = None

# Chat Models
class ChatMessage(BaseModel):
    role: str  # user or assistant
    content: str

class JobSearchQuery(BaseModel):
    skills: List[str]
    experience_level: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[str] = None

class JobListing(BaseModel):
    title: str
    company: str
    location: str
    url: str
    description: str
    posted_date: Optional[str] = None
    salary: Optional[str] = None

# API Response Models
class ResumeParseResponse(BaseModel):
    success: bool
    data: ResumeData
    message: Optional[str] = None

class ChatResponse(BaseModel):
    message: str
    job_suggestions: List[JobListing] = []
    requires_input: bool = False

# ============================================================
# 📌 SCHEMAS.PY — WHAT THESE MODELS ARE AND WHY THEY EXIST
# ============================================================
#
# This file defines all data models (schemas) used by the
# Resume Parser & Job Matcher backend.
#
# FastAPI + Pydantic use these models to:
#   ✔ Validate incoming requests
#   ✔ Structure API responses
#   ✔ Keep data consistent between backend & frontend
#   ✔ Auto-generate documentation (Swagger UI)
#
# -------------------------------
# 🔹 Resume Parsing Models
# -------------------------------
# Experience      → One job experience inside the resume
# Education       → One education entry (degree, institution, etc.)
# ResumeData      → Final structured resume after parsing PDF/DOCX
#
# -------------------------------
# 🔹 Chat & Job Search Models
# -------------------------------
# ChatMessage     → Represents user/assistant messages
# JobSearchQuery  → What the user is searching for (skills, location)
# JobListing      → One job suggestion returned by the AI
#
# -------------------------------
# 🔹 API Response Models
# -------------------------------
# ResumeParseResponse → Response for resume upload API
# ChatResponse        → Response for job chatbot API
#
# These models ensure your backend has clean, typed, consistent
# data flow and prevent errors from bad input.
#
# ============================================================


