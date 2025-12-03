from typing import List, Dict, Any
from app.models.schemas import ChatMessage, JobListing, ResumeData
from app.services.job_search import JobSearchService
from app.utils.llm_client import LLMClient
import json

class ChatAgent:
    def __init__(self, resume_data: ResumeData):
        self.resume_data = resume_data
        self.job_search_service = JobSearchService()
        self.llm_client = LLMClient()
        self.conversation_history: List[ChatMessage] = []
    
    def process_message(self, user_message: str) -> Dict[str, Any]:
        """Process user message and return response"""
        
        # Add user message to history
        self.conversation_history.append(ChatMessage(role="user", content=user_message))
        
        # Determine intent
        intent = self._determine_intent(user_message)
        
        response_data = {
            "message": "",
            "job_suggestions": [],
            "requires_input": False
        }
        
        if intent == "greeting":
            response_data["message"] = self._generate_greeting()
            response_data["requires_input"] = True
            
        elif intent == "search_jobs":
            # Extract search parameters
            search_params = self._extract_search_params(user_message)
            
            # Search for jobs
            try:
                job_listings = self.job_search_service.search_jobs(self.resume_data, search_params)
                response_data["job_suggestions"] = job_listings
                response_data["message"] = self._format_job_response(job_listings)
            except Exception as e:
                response_data["message"] = f"I encountered an error while searching: {str(e)}"
            
        elif intent == "resume_feedback":
            response_data["message"] = self._generate_resume_feedback()
            
        elif intent == "career_advice":
            response_data["message"] = self._generate_career_advice(user_message)
            
        else:
            response_data["message"] = "I can help you find jobs, give resume feedback, or provide career advice. What would you like to do?"
            response_data["requires_input"] = True
        
        # Add assistant response to history
        self.conversation_history.append(
            ChatMessage(role="assistant", content=response_data["message"])
        )
        
        return response_data
    
    def _determine_intent(self, message: str) -> str:
        """Determine user intent"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["hello", "hi", "hey", "greetings"]):
            return "greeting"
        elif any(word in message_lower for word in ["job", "search", "find", "opportunity", "opening", "position"]):
            return "search_jobs"
        elif any(word in message_lower for word in ["resume", "cv", "feedback", "improve"]):
            return "resume_feedback"
        elif any(word in message_lower for word in ["advice", "career", "help", "suggest", "recommend"]):
            return "career_advice"
        else:
            return "general"
    
    def _extract_search_params(self, message: str) -> Dict[str, Any]:
        """Extract job search parameters from user message"""
        params = {}
        
        # Simple extraction
        message_lower = message.lower()
        
        # Check for location
        location_keywords = ["in ", "at ", "near ", "location ", "city ", "remote", "hybrid"]
        for keyword in location_keywords:
            if keyword in message_lower:
                if keyword in ["remote", "hybrid"]:
                    params["location"] = keyword.capitalize()
                break
        
        # Check for job type
        if "full time" in message_lower or "full-time" in message_lower:
            params["job_type"] = "full time"
        elif "part time" in message_lower or "part-time" in message_lower:
            params["job_type"] = "part time"
        elif "internship" in message_lower:
            params["job_type"] = "internship"
        
        return params
    
    def _generate_greeting(self) -> str:
        """Generate personalized greeting"""
        name = self.resume_data.name.split()[0] if self.resume_data.name else "there"
        top_skills = ', '.join(self.resume_data.skills[:3])
        
        return f"""👋 Hello {name}!

I'm your AI Job Hunter assistant. I've analyzed your resume and found skills in: **{top_skills}**.

Here's what I can help you with:
1. **Find job opportunities** matching your skills
2. **Give feedback** on your resume
3. Provide **career advice** based on your experience

What would you like to do?"""
    
    def _format_job_response(self, job_listings: List[JobListing]) -> str:
        """Format job listings into readable response"""
        if not job_listings:
            return "I couldn't find any jobs matching your criteria. Try adjusting your search terms or location."
        
        response = f"✅ **I found {len(job_listings)} job opportunities for you:**\n\n"
        
        for i, job in enumerate(job_listings[:3], 1):
            response += f"**{i}. {job.title}**\n"
            response += f"   🏢 **Company:** {job.company}\n"
            response += f"   📍 **Location:** {job.location}\n"
            response += f"   ⭐ **Match:** {job.match_score*100:.0f}%\n"
            response += f"   💰 **Salary:** {job.salary if job.salary else 'Not specified'}\n"
            response += f"   📝 **Description:** {job.description}\n"
            response += f"   🔗 [Apply Here]({job.url})\n\n"
        
        response += "Would you like me to search for more specific roles or adjust the search criteria?"
        
        return response
    
    def _generate_resume_feedback(self) -> str:
        """Generate resume feedback"""
        feedback_prompt = f"""Based on this resume data, provide 3 specific, actionable suggestions for improvement:

Resume Summary:
- Name: {self.resume_data.name}
- Skills: {len(self.resume_data.skills)} skills including {', '.join(self.resume_data.skills[:5])}
- Experience: {len(self.resume_data.experience)} positions
- Education: {len(self.resume_data.education)} degrees

Focus on:
1. Skill presentation
2. Experience descriptions
3. Overall resume strength

Provide concise, helpful feedback."""
        
        try:
            # Use Gemini for feedback - UPDATED MODEL NAME
            import google.generativeai as genai
            from app.config import settings
            
            genai.configure(api_key=settings.gemini_api_key)
            # CHANGED FROM 'gemini-pro' TO 'models/gemini-2.0-flash'
            model = genai.GenerativeModel('models/gemini-2.0-flash')
            
            response = model.generate_content(feedback_prompt)
            return response.text
            
        except Exception as e:
            print(f"[ChatAgent] Error generating feedback: {e}")
            
            # Try alternative model
            try:
                import google.generativeai as genai
                from app.config import settings
                
                genai.configure(api_key=settings.gemini_api_key)
                model = genai.GenerativeModel('models/gemini-2.5-flash')
                
                response = model.generate_content(feedback_prompt)
                return response.text
            except Exception as e2:
                print(f"[ChatAgent] Alternative model also failed: {e2}")
            
            # Fallback feedback
            return f"""Based on your resume, here are some suggestions:

1. **Quantify achievements**: Add numbers to your experience descriptions (e.g., "Improved performance by 20%")
2. **Expand skills**: Consider adding {', '.join(['AWS', 'Docker', 'TypeScript'][:3-len(self.resume_data.skills)])}
3. **Update summary**: Make your summary more specific to the roles you're targeting

Your resume looks good overall! Focus on tailoring it for specific job applications."""
    
    def _generate_career_advice(self, user_message: str) -> str:
        """Generate career advice"""
        advice_prompt = f"""Provide career advice based on this resume and query:

Resume:
- Skills: {', '.join(self.resume_data.skills[:5])}
- Experience Level: {len(self.resume_data.experience)} positions

User Question: {user_message}

Give specific, actionable advice."""
        
        try:
            import google.generativeai as genai
            from app.config import settings
            
            genai.configure(api_key=settings.gemini_api_key)
            # CHANGED FROM 'gemini-pro' TO 'models/gemini-2.0-flash'
            model = genai.GenerativeModel('models/gemini-2.0-flash')
            
            response = model.generate_content(advice_prompt)
            return response.text
            
        except Exception as e:
            print(f"[ChatAgent] Error generating advice: {e}")
            
            # Try alternative model
            try:
                import google.generativeai as genai
                from app.config import settings
                
                genai.configure(api_key=settings.gemini_api_key)
                model = genai.GenerativeModel('models/gemini-2.5-flash')
                
                response = model.generate_content(advice_prompt)
                return response.text
            except Exception as e2:
                print(f"[ChatAgent] Alternative model also failed: {e2}")
                
            return "Based on your skills and experience, I recommend focusing on roles that leverage your strengths in Python and web development. Consider looking for positions at tech companies that value full-stack expertise."