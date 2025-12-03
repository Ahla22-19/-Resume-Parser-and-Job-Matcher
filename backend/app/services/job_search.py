from tavily import TavilyClient
from typing import List, Dict, Any
from app.models.schemas import JobListing, ResumeData
from app.config import settings
import random

class JobSearchService:
    def __init__(self):
        self.tavily_api_key = settings.tavily_api_key
        
        if not self.tavily_api_key or self.tavily_api_key == "your_tavily_api_key_here":
            print("[JobSearch] WARNING: Tavily API key not configured")
            self.client = None
        else:
            try:
                self.client = TavilyClient(api_key=self.tavily_api_key)
                print("[JobSearch] Tavily client initialized")
            except Exception as e:
                print(f"[JobSearch] Failed to initialize Tavily: {e}")
                self.client = None
    
    def search_jobs(self, resume_data: ResumeData, query_params: Dict[str, Any] = None) -> List[JobListing]:
        """Search for jobs using Tavily API or return mock data"""
        
        # If no Tavily client, return mock jobs
        if not self.client:
            print("[JobSearch] Using mock job data")
            return self._get_mock_jobs(resume_data, query_params)
        
        try:
            # Generate search query
            search_query = self._generate_search_query(resume_data, query_params)
            
            print(f"[JobSearch] Searching for: {search_query}")
            
            # Perform search
            response = self.client.search(
                query=search_query,
                search_depth="advanced",
                max_results=8,
                include_domains=[
                    "linkedin.com/jobs",
                    "indeed.com",
                    "glassdoor.com",
                    "monster.com",
                    "careerbuilder.com"
                ]
            )
            
            # Process results
            job_listings = self._process_search_results(response['results'], resume_data)
            
            # If no results, use mock data
            if not job_listings:
                print("[JobSearch] No results found, using mock data")
                return self._get_mock_jobs(resume_data, query_params)
            
            return job_listings
            
        except Exception as e:
            print(f"[JobSearch] Tavily API error: {e}")
            return self._get_mock_jobs(resume_data, query_params)
    
    def _generate_search_query(self, resume_data: ResumeData, query_params: Dict[str, Any] = None) -> str:
        """Generate search query from resume"""
        # Base query from skills
        skills = resume_data.skills[:3] if len(resume_data.skills) > 3 else resume_data.skills
        base_query = " ".join(skills)
        
        # Add experience level
        exp_level = self._determine_experience_level(resume_data)
        
        # Add location if in query_params
        location = ""
        if query_params and query_params.get('location'):
            location = f" in {query_params['location']}"
        
        # Add job type if specified
        job_type = ""
        if query_params and query_params.get('job_type'):
            job_type = f" {query_params['job_type']}"
        
        return f"{base_query} {exp_level}{job_type} jobs{location}"
    
    def _determine_experience_level(self, resume_data: ResumeData) -> str:
        """Determine experience level based on work history"""
        total_months = 0
        
        for exp in resume_data.experience:
            if exp.start_date:
                try:
                    # Simple calculation (could be improved)
                    if exp.end_date and exp.end_date.lower() != 'present':
                        start_year = int(exp.start_date[:4]) if len(exp.start_date) >= 4 else 0
                        end_year = int(exp.end_date[:4]) if len(exp.end_date) >= 4 else 0
                        total_months += (end_year - start_year) * 12
                except:
                    pass
        
        total_years = total_months / 12
        
        if total_years < 1:
            return "entry level"
        elif total_years < 3:
            return "junior"
        elif total_years < 7:
            return "mid level"
        else:
            return "senior"
    
    def _process_search_results(self, results: List[Dict], resume_data: ResumeData) -> List[JobListing]:
        """Process and score search results"""
        job_listings = []
        
        for result in results[:5]:  # Limit to 5 results
            try:
                # Calculate match score
                match_score = self._calculate_match_score(result, resume_data)
                
                # Only include if relevant
                if match_score > 0.3:
                    job = JobListing(
                        title=result.get('title', 'Job Title'),
                        company=self._extract_company(result),
                        location=result.get('location', 'Location not specified'),
                        url=result.get('url', '#'),
                        description=result.get('content', 'No description available')[:200] + "...",
                        posted_date=result.get('published_date'),
                        salary=None,
                        match_score=round(match_score, 2)
                    )
                    job_listings.append(job)
            except Exception as e:
                print(f"[JobSearch] Error processing result: {e}")
                continue
        
        # Sort by match score
        return sorted(job_listings, key=lambda x: x.match_score, reverse=True)
    
    def _calculate_match_score(self, result: Dict, resume_data: ResumeData) -> float:
        """Calculate how well job matches resume"""
        score = 0.0
        
        # Check title and description for skill matches
        title = result.get('title', '').lower()
        description = result.get('content', '').lower()
        text_to_check = f"{title} {description}"
        
        # Count skill matches
        matched_skills = 0
        for skill in resume_data.skills:
            if skill.lower() in text_to_check:
                matched_skills += 1
        
        # Calculate score
        if len(resume_data.skills) > 0:
            score = matched_skills / len(resume_data.skills)
        
        return min(score, 1.0)
    
    def _extract_company(self, result: Dict) -> str:
        """Extract company name from result"""
        company = result.get('source_name', '')
        if not company:
            # Try to extract from URL
            url = result.get('url', '')
            if 'linkedin.com' in url:
                parts = url.split('/')
                if len(parts) > 3:
                    company = parts[3].replace('-', ' ').title()
        
        return company if company else "Company not specified"
    
    def _get_mock_jobs(self, resume_data: ResumeData, query_params: Dict[str, Any] = None) -> List[JobListing]:
        """Return mock job listings for testing"""
        mock_jobs = [
            JobListing(
                title="Python Developer",
                company="Tech Solutions Inc.",
                location="Remote",
                url="https://example.com/job1",
                description="Looking for Python developer with FastAPI and React experience. Minimum 2 years experience required.",
                posted_date="2024-01-15",
                salary="$80,000 - $120,000",
                match_score=random.uniform(0.7, 0.9)
            ),
            JobListing(
                title="Full Stack Engineer",
                company="Innovate Co.",
                location="New York, NY",
                url="https://example.com/job2",
                description="Join our team as a Full Stack Engineer working with React, Python, and AWS.",
                posted_date="2024-01-10",
                salary="$90,000 - $130,000",
                match_score=random.uniform(0.6, 0.8)
            ),
            JobListing(
                title="Software Developer",
                company="Digital Systems",
                location="Remote",
                url="https://example.com/job3",
                description="We're hiring a Software Developer with JavaScript and Python skills.",
                posted_date="2024-01-05",
                salary="$75,000 - $110,000",
                match_score=random.uniform(0.5, 0.7)
            ),
            JobListing(
                title="Backend Developer",
                company="DataTech",
                location="Austin, TX",
                url="https://example.com/job4",
                description="Backend developer position focusing on API development with FastAPI.",
                posted_date="2024-01-03",
                salary="$85,000 - $125,000",
                match_score=random.uniform(0.6, 0.8)
            )
        ]
        
        # Sort by match score
        return sorted(mock_jobs, key=lambda x: x.match_score, reverse=True)