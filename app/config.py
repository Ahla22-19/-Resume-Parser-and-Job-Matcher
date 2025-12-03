from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Keys
    openai_api_key: Optional[str] = None
    tavily_api_key: Optional[str] = None
    
    # App Settings
    app_name: str = "Resume Parser & Job Agent"
    debug: bool = False
    
    # CORS
    frontend_url: str = "http://localhost:3000"
    
    class Config:
        env_file = ".env"

settings = Settings()

# ============================================
# 📌 CONFIG.PY — WHAT EACH SETTING IS FOR
# ============================================
#
# This file loads all important configuration
# values for the Resume Parser & Job Agent app.
# It reads data automatically from the `.env` file.
#
# Field Breakdown:
#
# openai_api_key       → Used by llm_client.py to call OpenAI
# tavily_api_key       → Used by job_agent.py for Tavily web search
#
# app_name             → General name of the backend application
# debug                → Enables debug mode (True/False)
#
# frontend_url         → URL allowed to access backend (CORS)
#                         Example: React frontend on localhost:3000
#
# Config.env_file      → Tells Pydantic to load values from ".env"
#
# settings = Settings() creates a global settings object
# that can be imported anywhere in the backend for consistency.
#
# ============================================
