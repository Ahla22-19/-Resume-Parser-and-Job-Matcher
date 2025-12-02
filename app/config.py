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