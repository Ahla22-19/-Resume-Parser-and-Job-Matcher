from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import os
from contextlib import asynccontextmanager
import uuid

from app.config import settings
from app.models.schemas import (
    ResumeData, ResumeParseResponse, ChatMessage, 
    ChatResponse, JobSearchQuery
)
from app.utils.file_processor import FileProcessor
from app.utils.llm_client import LLMClient
from app.services.chat_agent import ChatAgent

# Global chat agents storage
chat_agents: Dict[str, ChatAgent] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager"""
    # Startup
    print("=" * 50)
    print("Starting Resume Job Agent API")
    print(f"Gemini API: {'Configured' if settings.gemini_api_key else 'Not configured'}")
    print(f"Tavily API: {'Configured' if settings.tavily_api_key else 'Not configured'}")
    print("=" * 50)
    
    yield
    
    # Shutdown
    print("Shutting down...")
    chat_agents.clear()

app = FastAPI(
    title="Resume Parser & Job Hunter API",
    description="API for parsing resumes and finding matching jobs using Gemini AI",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Resume Parser & Job Hunter API",
        "version": "1.0.0",
        "endpoints": {
            "parse_resume": "POST /parse-resume",
            "chat": "POST /chat/{session_id}",
            "create_agent": "POST /create-agent/{session_id}",
            "health": "GET /health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "gemini": "configured" if settings.gemini_api_key else "missing",
            "tavily": "configured" if settings.tavily_api_key else "missing"
        }
    }

@app.post("/parse-resume", response_model=ResumeParseResponse)
async def parse_resume(file: UploadFile = File(...)):
    """
    Parse resume file and extract structured information
    """
    try:
        # Validate file type
        allowed_types = [
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ]
        
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail="File type not supported. Please upload PDF or DOCX."
            )
        
        # Save and process file
        file_path, file_type = FileProcessor.save_uploaded_file(file)
        
        try:
            # Extract text
            print(f"[API] Extracting text from {file.filename}...")
            resume_text = FileProcessor.extract_text_from_file(file_path, file_type)
            print(f"[API] Extracted {len(resume_text)} characters")
            
            # Parse with Gemini
            print("[API] Parsing with Gemini...")
            llm_client = LLMClient()
            parsed_data = llm_client.parse_resume(resume_text)
            
            # Clean up temp file
            os.unlink(file_path)
            
            return ResumeParseResponse(
                success=True,
                data=parsed_data,
                message="Resume parsed successfully"
            )
            
        except Exception as e:
            # Clean up temp file on error
            if os.path.exists(file_path):
                os.unlink(file_path)
            raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.post("/chat/{session_id}", response_model=ChatResponse)
async def chat_with_agent(session_id: str, message: ChatMessage):
    """
    Chat with job hunting agent
    """
    try:
        # Check if session exists
        if session_id not in chat_agents:
            raise HTTPException(
                status_code=404,
                detail="Session not found. Please parse a resume first."
            )
        
        # Get chat agent for session
        agent = chat_agents[session_id]
        
        # Process message
        response_data = agent.process_message(message.content)
        
        return ChatResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@app.post("/create-agent/{session_id}")
async def create_chat_agent(session_id: str, resume_data: ResumeData):
    """
    Create a new chat agent with resume data
    """
    try:
        # Create new chat agent
        agent = ChatAgent(resume_data)
        chat_agents[session_id] = agent
        
        return {
            "success": True,
            "session_id": session_id,
            "message": "Chat agent created successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create agent: {str(e)}")

@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """
    Delete chat session
    """
    if session_id in chat_agents:
        del chat_agents[session_id]
    
    return {"success": True, "message": "Session deleted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True
    )