from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    # API Keys
    gemini_api_key: Optional[str] = os.getenv('GEMINI_API_KEY')
    tavily_api_key: Optional[str] = os.getenv('TAVILY_API_KEY')
    
    # App Settings
    app_name: str = "Resume Parser & Job Agent"
    debug: bool = os.getenv('DEBUG', 'false').lower() == 'true'
    frontend_url: str = os.getenv('FRONTEND_URL', 'http://localhost:3000')
    
    class Config:
        env_file = ".env"

settings = Settings()

# Debug print
print(f"[Config] Gemini API Key: {'Loaded' if settings.gemini_api_key else 'Missing'}")
print(f"[Config] Tavily API Key: {'Loaded' if settings.tavily_api_key else 'Missing'}")