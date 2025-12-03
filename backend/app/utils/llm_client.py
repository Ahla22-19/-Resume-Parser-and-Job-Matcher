import google.generativeai as genai
import json
from typing import Dict, Any, List
from app.models.schemas import ResumeData
from app.config import settings
import re

class LLMClient:
    def __init__(self):
        self.api_key = settings.gemini_api_key
        
        if not self.api_key:
            raise ValueError("Gemini API key is not configured")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Available models from your list
        # Use gemini-2.0-flash (fast and reliable)
        self.model_name = "models/gemini-2.0-flash"
        
        # Set up the model
        generation_config = {
            "temperature": 0.1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 2000,
        }
        
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
        
        try:
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            print(f"[LLMClient] Initialized with {self.model_name}")
            
            # Test the model
            test_response = self.model.generate_content("test")
            print("[LLMClient] Model test successful")
            
        except Exception as e:
            print(f"[LLMClient] Failed to initialize {self.model_name}: {e}")
            
            # Fallback to gemini-2.5-flash
            try:
                self.model_name = "models/gemini-2.5-flash"
                self.model = genai.GenerativeModel(
                    model_name=self.model_name,
                    generation_config=generation_config,
                    safety_settings=safety_settings
                )
                print(f"[LLMClient] Fallback to {self.model_name}")
            except Exception as e2:
                print(f"[LLMClient] All models failed: {e2}")
                raise ValueError("Could not initialize any Gemini model")
    
    def parse_resume(self, resume_text: str) -> ResumeData:
        """Extract structured resume data using Gemini"""
        
        system_prompt = """You are an expert resume parser. Extract structured information from resume text.
        Return ONLY a valid JSON object matching the schema below. No explanations, no markdown formatting."""
        
        json_schema = {
            "name": "string",
            "email": "string or null",
            "phone": "string or null",
            "skills": ["list", "of", "strings"],
            "experience": [
                {
                    "title": "string",
                    "company": "string",
                    "start_date": "string or null",
                    "end_date": "string or null",
                    "description": "string or null",
                    "location": "string or null"
                }
            ],
            "education": [
                {
                    "degree": "string",
                    "institution": "string",
                    "field_of_study": "string or null",
                    "start_date": "string or null",
                    "end_date": "string or null",
                    "gpa": "number or null"
                }
            ],
            "summary": "string or null"
        }
        
        user_prompt = f"""Parse this resume text and extract information:
        
        {resume_text[:3000]}
        
        Return ONLY a JSON object matching this exact schema:
        {json.dumps(json_schema, indent=2)}
        
        Important:
        1. If information is missing, use null
        2. Dates in YYYY-MM format when possible
        3. Extract ALL skills mentioned
        4. Be accurate and thorough
        5. Return ONLY the JSON, no other text"""
        
        try:
            print(f"[LLMClient] Parsing resume with {self.model_name}...")
            
            # Combine prompts
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            response = self.model.generate_content(full_prompt)
            response_text = response.text
            
            # Extract JSON from response
            json_str = self._extract_json(response_text)
            
            if not json_str:
                raise ValueError("Could not extract JSON from response")
            
            parsed_data = json.loads(json_str)
            parsed_data['raw_text'] = resume_text[:1000]
            
            print(f"[LLMClient] Successfully parsed resume")
            return ResumeData(**parsed_data)
            
        except Exception as e:
            print(f"[LLMClient] Error parsing resume: {str(e)}")
            raise Exception(f"Failed to parse resume: {str(e)}")
    
    def _extract_json(self, text: str) -> str:
        """Extract JSON from Gemini response"""
        text = text.strip()
        
        # Remove markdown code blocks
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        
        # Find JSON object
        try:
            # Look for first { and last }
            start = text.find('{')
            end = text.rfind('}') + 1
            
            if start != -1 and end != 0:
                json_str = text[start:end]
                # Validate it's JSON
                json.loads(json_str)
                return json_str
        except json.JSONDecodeError:
            pass
        
        # Try the entire text
        try:
            json.loads(text)
            return text
        except json.JSONDecodeError:
            return ""
    
    def generate_job_search_query(self, resume_data: ResumeData, user_query: str = None) -> Dict[str, Any]:
        """Generate optimized job search query based on resume"""
        
        prompt = f"""Based on this resume, create job search parameters:

Skills: {', '.join(resume_data.skills[:10])}
Experience: {len(resume_data.experience)} positions
User Query: {user_query if user_query else 'Find relevant jobs'}

Generate:
1. Search keywords
2. Job titles
3. Experience level (Entry, Junior, Mid, Senior)
4. Location (if mentioned in resume)

Return ONLY JSON with this format:
{{
    "keywords": ["keyword1", "keyword2"],
    "job_titles": ["title1", "title2"],
    "experience_level": "string",
    "location": "string or null"
}}"""
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            json_str = self._extract_json(response_text)
            if json_str:
                return json.loads(json_str)
            else:
                raise ValueError("Could not extract JSON")
                
        except Exception as e:
            print(f"[LLMClient] Error generating job query: {str(e)}")
            return {
                "keywords": resume_data.skills[:5],
                "job_titles": ["Software Engineer", "Developer", "Full Stack Developer"],
                "experience_level": "Mid Level",
                "location": None
            }