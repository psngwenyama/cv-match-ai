import json
import re
import time
import random
from datetime import datetime, timedelta
import openai
from openai import OpenAI
import google.generativeai as genai
from django.conf import settings
from django.core.cache import cache
from .prompts import (
    JOB_ANALYSIS_PROMPT,
    CV_GENERATION_PROMPT,
    SKILL_EXTRACTION_PROMPT,
    CONTENT_IMPROVEMENT_PROMPT
)

class CVGenerationService:
    def __init__(self, provider=None):
        """Initialize AI service with specified provider (gemini or openai)"""
        self.provider = provider or settings.AI_PROVIDER
        self.model_name = settings.AI_MODEL
        
        # Track quota status
        self.quota_exceeded_until = None
        self.quota_cooldown = 60  # Default cooldown in seconds
        
        print(f"\n🔧 Initializing {self.provider} with model: {self.model_name}")
        
        # Configure the selected provider
        if self.provider == 'gemini':
            try:
                genai.configure(api_key=settings.GOOGLE_API_KEY)
                
                # Map common model names to available ones
                model_mapping = {
                    'gemini-pro': 'gemini-2.5-flash',
                    'gemini-1.5-pro': 'gemini-2.5-pro',
                    'gemini-1.5-flash': 'gemini-2.5-flash',
                    'gemini-2.0-flash': 'gemini-2.5-flash',
                    'gemini-2.0-flash-lite': 'gemini-2.0-flash-lite',
                    'gpt-4': 'gemini-2.5-pro',
                    'gpt-3.5-turbo': 'gemini-2.5-flash',
                }
                
                # Use mapped model name if needed
                if self.model_name in model_mapping:
                    self.model_name = model_mapping[self.model_name]
                    print(f"📝 Mapped to available model: {self.model_name}")
                
                # List available models for debugging
                print("📋 Available Gemini models:")
                try:
                    for m in genai.list_models():
                        if 'generateContent' in m.supported_generation_methods:
                            print(f"  - {m.name}")
                except Exception as e:
                    print(f"  Could not list models: {e}")
                
                # Ensure we're using a valid model
                valid_models = [
                    'gemini-2.0-flash',
                    'gemini-2.5-pro',
                    'gemini-2.5-flash',
                    'gemini-2.0-flash-lite',
                    'models/gemini-2.0-flash',
                    'models/gemini-2.5-pro',
                ]
                
                # Check if model name needs 'models/' prefix
                if self.model_name not in valid_models and f"models/{self.model_name}" in valid_models:
                    self.model_name = f"models/{self.model_name}"
                
                # Default to flash if still invalid
                if self.model_name not in valid_models:
                    print(f"⚠️ Model {self.model_name} not in valid list, defaulting to gemini-2.0-flash")
                    self.model_name = 'gemini-2.0-flash'
                
                self.model = genai.GenerativeModel(self.model_name)
                print(f"✅ Gemini initialized successfully with model: {self.model_name}")
                
            except Exception as e:
                print(f"❌ Gemini initialization error: {e}")
                raise
        
        elif self.provider == 'openai':
            try:
                self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
                # Test connection by listing models
                self.client.models.list()
                print(f"✅ OpenAI initialized successfully with model: {self.model_name}")
            except Exception as e:
                print(f"❌ OpenAI initialization error: {e}")
                raise

    def _check_quota(self):
        """Check if we're currently in a quota cooldown period"""
        if self.quota_exceeded_until and datetime.now() < self.quota_exceeded_until:
            wait_seconds = (self.quota_exceeded_until - datetime.now()).total_seconds()
            print(f"⏳ In quota cooldown. Need to wait {wait_seconds:.1f} seconds...")
            return False
        return True

    def _handle_quota_error(self, error_message):
        """Extract retry delay from error message and set quota cooldown"""
        try:
            # Try to extract retry delay from error message
            delay_match = re.search(r'retry in (\d+\.?\d*)s', error_message.lower())
            if delay_match:
                delay = float(delay_match.group(1))
                self.quota_exceeded_until = datetime.now() + timedelta(seconds=delay + 5)  # Add buffer
                self.quota_cooldown = delay + 5
                print(f"⏳ Quota exceeded. Will retry after {delay} seconds")
            else:
                # Default to 60 seconds if can't parse
                self.quota_exceeded_until = datetime.now() + timedelta(seconds=60)
                self.quota_cooldown = 60
                print("⏳ Quota exceeded. Will retry after 60 seconds")
        except Exception as e:
            print(f"Error parsing quota delay: {e}")
            self.quota_exceeded_until = datetime.now() + timedelta(seconds=60)
            self.quota_cooldown = 60

    def analyze_job_description(self, job_description, max_retries=3):
        """Extract key information from job description with retry logic"""
        
        # Check if we're in quota cooldown
        if not self._check_quota():
            print("⚠️ Using fallback analysis due to quota limits")
            return self.fallback_analysis(job_description)
        
        for attempt in range(max_retries):
            try:
                print(f"\n🔍 Analyzing job description with {self.provider} (attempt {attempt + 1}/{max_retries})...")
                print(f"Job description length: {len(job_description)} characters")
                
                prompt = JOB_ANALYSIS_PROMPT.format(job_description=job_description)
                
                if self.provider == 'gemini':
                    print("📞 Calling Gemini API...")
                    response = self.model.generate_content(prompt)
                    
                    if not response:
                        raise ValueError("No response from Gemini")
                    
                    if not hasattr(response, 'text') or not response.text:
                        raise ValueError("Empty response text from Gemini")
                    
                    analysis_text = response.text
                    print(f"✅ Received response from Gemini ({len(analysis_text)} chars)")
                    
                elif self.provider == 'openai':
                    print("📞 Calling OpenAI API...")
                    response = self.client.chat.completions.create(
                        model=self.model_name or 'gpt-3.5-turbo',
                        messages=[
                            {"role": "system", "content": "You are an expert HR and recruitment specialist. Always return valid JSON."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.3,
                        max_tokens=1500
                    )
                    
                    if not response.choices or not response.choices[0].message.content:
                        raise ValueError("Empty response from OpenAI")
                    
                    analysis_text = response.choices[0].message.content
                    print(f"✅ Received response from OpenAI ({len(analysis_text)} chars)")
                
                # Clean the response text (remove markdown code blocks if present)
                analysis_text = re.sub(r'```json\s*', '', analysis_text)
                analysis_text = re.sub(r'```\s*', '', analysis_text)
                analysis_text = analysis_text.strip()
                
                if not analysis_text:
                    raise ValueError("Empty response after cleaning")
                
                print(f"📝 Response preview: {analysis_text[:200]}...")
                
                # Parse the response - try to extract JSON
                try:
                    # Try to find JSON in the response
                    json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
                    if json_match:
                        analysis = json.loads(json_match.group())
                        print("✅ Successfully parsed JSON from response")
                    else:
                        # If no JSON found, create a structured response from the text
                        print("⚠️ No JSON found, creating structured response from text")
                        analysis = {
                            'raw_analysis': analysis_text[:500],  # Truncate for storage
                            'key_skills': self._extract_skills_from_text(analysis_text),
                            'job_title': self._extract_job_title(analysis_text),
                            'experience_level': self._extract_experience_level(analysis_text),
                            'key_responsibilities': [],
                            'required_qualifications': []
                        }
                except json.JSONDecodeError as e:
                    print(f"❌ JSON parsing error: {e}")
                    # If JSON parsing fails, create a structured response
                    analysis = {
                        'raw_analysis': analysis_text[:500],  # Truncate for storage
                        'key_skills': self._extract_skills_from_text(analysis_text),
                        'job_title': self._extract_job_title(analysis_text),
                        'experience_level': self._extract_experience_level(analysis_text),
                        'key_responsibilities': [],
                        'required_qualifications': []
                    }
                
                # Ensure we have all required fields
                if 'key_skills' not in analysis:
                    analysis['key_skills'] = self._extract_skills_from_text(analysis_text)
                if 'job_title' not in analysis:
                    analysis['job_title'] = self._extract_job_title(analysis_text)
                if 'experience_level' not in analysis:
                    analysis['experience_level'] = self._extract_experience_level(analysis_text)
                if 'key_responsibilities' not in analysis:
                    analysis['key_responsibilities'] = []
                if 'required_qualifications' not in analysis:
                    analysis['required_qualifications'] = []
                
                print(f"✅ Analysis complete: Found {len(analysis.get('key_skills', []))} skills")
                return analysis
                
            except Exception as e:
                error_str = str(e)
                print(f"❌ AI Analysis Error ({self.provider}): {error_str}")
                
                # Check for quota exceeded error (429)
                if '429' in error_str or 'quota' in error_str.lower() or 'resource_exhausted' in error_str.lower() or 'rate limit' in error_str.lower():
                    self._handle_quota_error(error_str)
                    
                    if attempt < max_retries - 1:
                        # Exponential backoff with jitter 
                        wait_time = (2 ** attempt) + random.uniform(0, 1)
                        print(f"⏳ Rate limited. Waiting {wait_time:.2f} seconds before retry...")
                        time.sleep(wait_time)
                        continue
                    else:
                        print("⚠️ Max retries reached. Using fallback analysis.")
                        return self.fallback_analysis(job_description)
                else:
                    # Non-quota error, don't retry
                    import traceback
                    traceback.print_exc()
                    return self.fallback_analysis(job_description)
        
        return self.fallback_analysis(job_description)

    def generate_cv(self, profile, job_description, max_retries=3):
        """Generate tailored CV content based on job description with retry logic"""
        
        # Check if we're in quota cooldown
        if not self._check_quota():
            print("⚠️ Using fallback CV generation due to quota limits")
            return self.fallback_cv_generation(profile, job_description)
        
        for attempt in range(max_retries):
            try:
                print(f"\n📄 Generating CV with {self.provider} (attempt {attempt + 1}/{max_retries})...")
                
                # Prepare profile data
                profile_data = self._prepare_profile_data(profile)
                print(f"📊 Profile prepared with:")
                print(f"  - Work experiences: {len(profile_data.get('work_experience', []))}")
                print(f"  - Education: {len(profile_data.get('education', []))}")
                print(f"  - Skills: {len(profile_data.get('skills', []))}")
                print(f"  - Projects: {len(profile_data.get('projects', []))}")
                print(f"  - Certifications: {len(profile_data.get('certifications', []))}")
                
                # First, analyze the job to understand requirements
                job_analysis = self.analyze_job_description(job_description)
                print(f"📋 Job analysis complete")
                
                # Create a detailed prompt that emphasizes tailoring
                prompt = f"""
You are an expert CV writer. Your task is to create a HIGHLY TAILORED CV for a specific job.

JOB DESCRIPTION ANALYSIS:
{json.dumps(job_analysis, indent=2)}

CANDIDATE PROFILE:
{json.dumps(profile_data, indent=2)}

INSTRUCTIONS:
1. Analyze the job requirements and identify which parts of the candidate's profile are most relevant
2. For each work experience, rewrite the bullet points to emphasize achievements that match the job requirements
3. If the candidate has achievements with numbers, make sure to include them
4. Reorder experiences to put the most relevant ones first (most relevant doesn't mean most recent)
5. The summary should specifically mention why this candidate is perfect for THIS role
6. ONLY use information from the candidate's profile - DO NOT invent anything
7. If certain experiences are completely irrelevant, you can shorten them or omit them entirely
8. Use keywords from the job description naturally throughout the CV
9. For skills, prioritize those mentioned in the job description
10. Make the CV compelling and show clear alignment between the candidate and the job

Return the CV as a JSON object with this structure:
{{
    "summary": "A compelling, tailored summary (3-4 sentences) that directly addresses this specific job",
    "work_experience": [
        {{
            "title": "Job Title",
            "company": "Company Name",
            "location": "Location",
            "start_date": "YYYY-MM",
            "end_date": "YYYY-MM or Present",
            "description": "Bullet points with • symbol, tailored to the job. Each bullet should start with a strong action verb."
        }}
    ],
    "education": [
        {{
            "degree": "Degree Name",
            "institution": "Institution Name",
            "location": "Location",
            "start_date": "YYYY-MM",
            "end_date": "YYYY-MM or Present",
            "description": "Relevant coursework or achievements (optional)",
            "gpa": "GPA if impressive"
        }}
    ],
    "skills": ["Skill1", "Skill2", "Skill3", ...],
    "projects": [
        {{
            "name": "Project Name",
            "description": "Project description highlighting relevance to the job",
            "technologies": ["Tech1", "Tech2"]
        }}
    ],
    "certifications": [
        {{
            "name": "Certification Name",
            "issuer": "Issuing Organization"
        }}
    ],
    "matched_skills": ["Skills from profile that match the job requirements"],
    "missing_skills": ["Job requirements not found in profile"]
}}

IMPORTANT: The CV must be DIFFERENT from the original profile. It should be specifically tailored to THIS job.
"""
                
                print("📞 Calling AI for CV generation...")
                
                if self.provider == 'gemini':
                    response = self.model.generate_content(prompt)
                    if not response or not response.text:
                        raise ValueError("Empty response from Gemini")
                    response_text = response.text
                    print(f"✅ Received response from Gemini ({len(response_text)} chars)")
                    
                elif self.provider == 'openai':
                    response = self.client.chat.completions.create(
                        model=self.model_name or 'gpt-4',
                        messages=[
                            {"role": "system", "content": "You are an expert CV writer. You MUST tailor the CV to the specific job description. Return valid JSON only."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7,
                        max_tokens=3000
                    )
                    if not response.choices or not response.choices[0].message.content:
                        raise ValueError("Empty response from OpenAI")
                    response_text = response.choices[0].message.content
                    print(f"✅ Received response from OpenAI ({len(response_text)} chars)")
                
                # Clean the response text
                response_text = re.sub(r'```json\s*', '', response_text)
                response_text = re.sub(r'```\s*', '', response_text)
                response_text = response_text.strip()
                
                if not response_text:
                    raise ValueError("Empty response after cleaning")
                
                print(f"📝 Response preview: {response_text[:200]}...")
                
                # Parse the JSON response
                try:
                    # Try to find JSON in the response
                    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                    if json_match:
                        cv_content = json.loads(json_match.group())
                        print("✅ Successfully parsed JSON from response")
                    else:
                        # Try parsing the whole response
                        cv_content = json.loads(response_text)
                        print("✅ Successfully parsed entire response as JSON")
                    
                    # Ensure we have all required fields
                    if 'summary' not in cv_content:
                        cv_content['summary'] = self._generate_tailored_summary(profile_data, job_analysis)
                    
                    if 'work_experience' not in cv_content:
                        cv_content['work_experience'] = profile_data.get('work_experience', [])
                    
                    if 'education' not in cv_content:
                        cv_content['education'] = profile_data.get('education', [])
                    
                    if 'skills' not in cv_content:
                        cv_content['skills'] = [s['name'] for s in profile_data.get('skills', [])]
                    
                    if 'projects' not in cv_content:
                        cv_content['projects'] = profile_data.get('projects', [])
                    
                    if 'certifications' not in cv_content:
                        cv_content['certifications'] = profile_data.get('certifications', [])
                    
                    # Calculate matched and missing skills
                    job_skills = job_analysis.get('key_skills', [])
                    profile_skills = [s['name'] for s in profile_data.get('skills', [])]
                    
                    matched_skills, missing_skills = self._calculate_skill_matches_from_lists(job_skills, profile_skills)
                    
                    cv_content['matched_skills'] = matched_skills
                    cv_content['missing_skills'] = missing_skills
                    
                    # Calculate match score
                    match_score = self._calculate_match_score_from_lists(matched_skills, missing_skills)
                    print(f"📊 Match score: {match_score}%")
                    
                except json.JSONDecodeError as e:
                    print(f"❌ JSON parsing error: {e}")
                    print(f"Raw response (first 500 chars): {response_text[:500]}")
                    
                    # Fallback: create a basic tailored structure
                    cv_content = self._create_fallback_cv(profile_data, job_analysis)
                    matched_skills, missing_skills = self._calculate_skill_matches_from_lists(
                        job_analysis.get('key_skills', []),
                        [s['name'] for s in profile_data.get('skills', [])]
                    )
                    cv_content['matched_skills'] = matched_skills
                    cv_content['missing_skills'] = missing_skills
                    match_score = self._calculate_match_score_from_lists(matched_skills, missing_skills)
                
                return cv_content, {
                    'match_score': match_score,
                    'matched_skills': cv_content.get('matched_skills', []),
                    'missing_skills': cv_content.get('missing_skills', []),
                    'job_analysis': job_analysis
                }
                
            except Exception as e:
                error_str = str(e)
                print(f"❌ CV Generation Error ({self.provider}): {error_str}")
                
                # Check for quota exceeded error (429)
                if '429' in error_str or 'quota' in error_str.lower() or 'resource_exhausted' in error_str.lower() or 'rate limit' in error_str.lower():
                    self._handle_quota_error(error_str)
                    
                    if attempt < max_retries - 1:
                        # Exponential backoff with jitter 
                        wait_time = (2 ** attempt) + random.uniform(0, 1)
                        print(f"⏳ Rate limited. Waiting {wait_time:.2f} seconds before retry...")
                        time.sleep(wait_time)
                        continue
                    else:
                        print("⚠️ Max retries reached. Using fallback CV generation.")
                        return self.fallback_cv_generation(profile, job_description)
                else:
                    # Non-quota error
                    import traceback
                    traceback.print_exc()
                    return self.fallback_cv_generation(profile, job_description)
        
        return self.fallback_cv_generation(profile, job_description)

    def extract_skills(self, text):
        """Extract skills from text"""
        try:
            prompt = SKILL_EXTRACTION_PROMPT.format(text=text)
            
            if self.provider == 'gemini':
                response = self.model.generate_content(prompt)
                if not response or not response.text:
                    return self._extract_skills_from_text(text)
                skills_text = response.text
                
            elif self.provider == 'openai':
                response = self.client.chat.completions.create(
                    model=self.model_name or 'gpt-3.5-turbo',
                    messages=[
                        {"role": "system", "content": "You are a skill extraction specialist. Return valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2,
                    max_tokens=500
                )
                if not response.choices or not response.choices[0].message.content:
                    return self._extract_skills_from_text(text)
                skills_text = response.choices[0].message.content
            
            # Clean the response
            skills_text = re.sub(r'```json\s*', '', skills_text)
            skills_text = re.sub(r'```\s*', '', skills_text)
            skills_text = skills_text.strip()
            
            # Try to parse JSON
            try:
                json_match = re.search(r'\{.*\}', skills_text, re.DOTALL)
                if json_match:
                    skills_data = json.loads(json_match.group())
                    return skills_data.get('skills', [])
            except:
                pass
            
            return self._extract_skills_from_text(text)
            
        except Exception as e:
            print(f"Skill Extraction Error: {e}")
            return self._extract_skills_from_text(text)

    def improve_content(self, text, context):
        """Improve and optimize content"""
        try:
            prompt = CONTENT_IMPROVEMENT_PROMPT.format(text=text, context=context)
            
            if self.provider == 'gemini':
                response = self.model.generate_content(prompt)
                if not response or not response.text:
                    return text
                return response.text
                
            elif self.provider == 'openai':
                response = self.client.chat.completions.create(
                    model=self.model_name or 'gpt-3.5-turbo',
                    messages=[
                        {"role": "system", "content": "You are a professional editor and writer."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.4,
                    max_tokens=1000
                )
                if not response.choices or not response.choices[0].message.content:
                    return text
                return response.choices[0].message.content
            
        except Exception as e:
            print(f"Content Improvement Error: {e}")
            return text

    def _prepare_profile_data(self, profile):
        """Prepare profile data for AI"""
        return {
            'personal': {
                'fullName': f"{profile.user.first_name} {profile.user.last_name}".strip() or profile.user.username,
                'title': getattr(profile, 'title', ''),
                'summary': getattr(profile, 'summary', ''),
                'email': profile.user.email,
                'phone': getattr(profile, 'phone', ''),
                'location': getattr(profile, 'location', '')
            },
            'work_experience': [
                {
                    'title': exp.title,
                    'company': exp.company,
                    'location': exp.location,
                    'start_date': exp.start_date.strftime('%Y-%m') if exp.start_date else '',
                    'end_date': exp.end_date.strftime('%Y-%m') if exp.end_date else ('Present' if exp.current else ''),
                    'current': exp.current,
                    'description': exp.description,
                    'achievements': exp.achievements,
                    'technologies': exp.technologies
                }
                for exp in profile.work_experiences.all()
            ],
            'education': [
                {
                    'degree': edu.degree,
                    'institution': edu.institution,
                    'location': edu.location,
                    'start_date': edu.start_date.strftime('%Y-%m') if edu.start_date else '',
                    'end_date': edu.end_date.strftime('%Y-%m') if edu.end_date else ('Present' if edu.current else ''),
                    'current': edu.current,
                    'description': edu.description,
                    'gpa': edu.gpa,
                    'achievements': edu.achievements
                }
                for edu in profile.education.all()
            ],
            'skills': [
                {
                    'name': skill.name,
                    'level': skill.level,
                    'years_experience': skill.years_experience
                }
                for skill in profile.skills.all()
            ],
            'projects': [
                {
                    'name': proj.name,
                    'description': proj.description,
                    'technologies': proj.technologies,
                    'url': proj.url,
                    'highlights': proj.highlights
                }
                for proj in profile.projects.all()
            ],
            'certifications': [
                {
                    'name': cert.name,
                    'issuer': cert.issuer,
                    'date_obtained': cert.date_obtained.strftime('%Y-%m') if cert.date_obtained else ''
                }
                for cert in profile.certifications.all()
            ],
            'languages': [
                {
                    'name': lang.name,
                    'proficiency': lang.proficiency
                }
                for lang in profile.languages.all()
            ]
        }

    def _calculate_match_score(self, profile, job_description):
        """Calculate match score between profile and job"""
        try:
            # Extract skills from job description
            job_skills = self.extract_skills(job_description)
            profile_skills = [skill.name for skill in profile.skills.all()]
            
            if not job_skills:
                return 50
            
            matched = set([s.lower() for s in job_skills]) & set([s.lower() for s in profile_skills])
            score = int((len(matched) / len(job_skills)) * 100)
            return min(score, 100)
        except:
            return 50

    def _calculate_match_score_from_lists(self, matched_skills, missing_skills):
        """Calculate match score from matched and missing skills lists"""
        total = len(matched_skills) + len(missing_skills)
        if total == 0:
            return 50
        return int((len(matched_skills) / total) * 100)

    def _calculate_skill_matches_from_lists(self, job_skills, profile_skills):
        """Calculate matched and missing skills from lists"""
        if not job_skills:
            return [], []
        
        # Normalize to lowercase for comparison
        job_skills_lower = [s.lower() for s in job_skills]
        profile_skills_lower = [s.lower() for s in profile_skills]
        
        matched = []
        missing = []
        
        for job_skill in job_skills:
            if job_skill.lower() in profile_skills_lower:
                # Find the original case version from profile
                idx = profile_skills_lower.index(job_skill.lower())
                matched.append(profile_skills[idx])
            else:
                missing.append(job_skill)
        
        return matched, missing

    def _generate_tailored_summary(self, profile_data, job_analysis):
        """Generate a tailored summary based on job analysis"""
        name = profile_data.get('personal', {}).get('fullName', 'The candidate')
        job_title = job_analysis.get('job_title', 'the position')
        
        # Get top skills
        skills = profile_data.get('skills', [])
        skill_names = [s['name'] for s in skills[:3]]
        skills_text = ', '.join(skill_names) if skill_names else 'professional experience'
        
        # Get experience
        exp_count = len(profile_data.get('work_experience', []))
        exp_text = f"{exp_count} years" if exp_count > 0 else "experience"
        
        return f"{name} is a dedicated professional with {exp_text} in {skills_text}. Passionate about contributing to the {job_title} role by leveraging expertise in delivering high-quality results and driving innovation. Committed to continuous learning and professional growth."

    def _create_fallback_cv(self, profile_data, job_analysis):
        """Create a fallback CV structure when AI fails"""
        return {
            'summary': self._generate_tailored_summary(profile_data, job_analysis),
            'work_experience': profile_data.get('work_experience', []),
            'education': profile_data.get('education', []),
            'skills': [s['name'] for s in profile_data.get('skills', [])],
            'projects': profile_data.get('projects', []),
            'certifications': profile_data.get('certifications', []),
            'languages': profile_data.get('languages', [])
        }

    def _extract_skills_from_text(self, text):
        """Extract potential skills from text using pattern matching"""
        # Common technical skills patterns
        common_skills = [
            'python', 'javascript', 'java', 'c++', 'c#', 'react', 'angular', 'vue',
            'django', 'flask', 'spring', 'node', 'express', 'sql', 'mongodb',
            'postgresql', 'mysql', 'aws', 'azure', 'docker', 'kubernetes',
            'git', 'rest', 'api', 'html', 'css', 'typescript', 'php', 'ruby',
            'swift', 'kotlin', 'flutter', 'react native', 'machine learning',
            'data science', 'analytics', 'project management', 'agile', 'scrum',
            'leadership', 'communication', 'teamwork', 'problem solving',
            'critical thinking', 'time management', 'organization', 'excel',
            'powerpoint', 'word', 'office', 'photoshop', 'illustrator', 'figma',
            'sketch', 'adobe xd', 'ui/ux', 'user research', 'wireframing',
            'prototyping', 'testing', 'qa', 'selenium', 'jenkins', 'ci/cd',
            'terraform', 'ansible', 'puppet', 'chef', 'linux', 'unix', 'windows',
            'bash', 'powershell', 'networking', 'security', 'cybersecurity'
        ]
        
        found_skills = []
        text_lower = text.lower()
        
        for skill in common_skills:
            if skill in text_lower:
                # Capitalize appropriately
                if skill in ['c++', 'c#', 'react native', 'machine learning', 'data science', 'ci/cd', 'ui/ux']:
                    found_skills.append(skill.title())
                else:
                    found_skills.append(skill.upper() if skill in ['aws', 'api', 'sql', 'git', 'qa', 'ci/cd'] else skill.title())
        
        # Remove duplicates while preserving order
        seen = set()
        unique_skills = []
        for skill in found_skills:
            if skill.lower() not in seen:
                seen.add(skill.lower())
                unique_skills.append(skill)
        
        return unique_skills[:15]  # Return top 15 skills

    def _extract_job_title(self, text):
        """Extract potential job title from text"""
        # Look for common job title patterns
        patterns = [
            r'(?:Job Title|Position|Role)[:\s]+([^\n,.]+)',
            r'^([A-Z][a-z]+ (?:Developer|Engineer|Manager|Director|Lead|Architect|Designer|Analyst|Specialist|Consultant))',
            r'(Senior|Junior|Lead|Principal|Staff)?\s*(?:Software|Frontend|Backend|Full[-\s]?Stack|DevOps|Data|Cloud|UI|UX|Product|Project|QA|Test|Security|Network|System|Platform|Site Reliability|Machine Learning|AI|ML|NLP|Computer Vision)\s*(?:Developer|Engineer|Architect|Designer|Manager|Specialist|Scientist|Analyst)',
            r'([A-Z][a-z]+ (?:Engineer|Developer|Designer|Manager))'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                # Clean up extra spaces
                title = re.sub(r'\s+', ' ', title)
                return title
        
        return "Software Developer"

    def _extract_experience_level(self, text):
        """Extract experience level from text"""
        text_lower = text.lower()
        
        if 'senior' in text_lower or 'lead' in text_lower or 'principal' in text_lower or 'sr.' in text_lower or 'staff' in text_lower:
            return 'Senior'
        elif 'junior' in text_lower or 'entry' in text_lower or 'graduate' in text_lower or 'jr.' in text_lower or 'associate' in text_lower:
            return 'Junior'
        elif 'mid' in text_lower or 'intermediate' in text_lower or 'mid-level' in text_lower:
            return 'Mid-Level'
        
        # Try to extract years of experience
        years_match = re.search(r'(\d+)[\+]?\s*(?:years?|yrs?)', text_lower)
        if years_match:
            years = int(years_match.group(1))
            if years >= 5:
                return 'Senior'
            elif years >= 2:
                return 'Mid-Level'
            else:
                return 'Junior'
        
        return 'Not Specified'

    def fallback_analysis(self, job_description):
        """Fallback analysis when AI fails"""
        print(f"⚠️ Using fallback analysis for {self.provider}")
        return {
            'job_title': self._extract_job_title(job_description),
            'key_skills': self._extract_skills_from_text(job_description),
            'required_experience': self._extract_experience_level(job_description),
            'key_responsibilities': [],
            'required_qualifications': [],
            'preferred_qualifications': [],
            'industry_keywords': [],
            'experience_level': self._extract_experience_level(job_description),
            'education_required': 'Not specified',
            'raw_analysis': f'AI service ({self.provider}) unavailable due to quota limits. Using basic analysis.',
            'match_score': 50,
            'matched_skills': [],
            'missing_skills': []
        }

    def fallback_cv_generation(self, profile, job_description):
        """Fallback CV generation when AI fails"""
        print(f"⚠️ Using fallback CV generation for {self.provider}")
        
        # Get profile data
        profile_data = self._prepare_profile_data(profile)
        
        # Calculate basic match score
        job_skills = self._extract_skills_from_text(job_description)
        profile_skills = [skill.name for skill in profile.skills.all()]
        
        matched = set([s.lower() for s in job_skills]) & set([s.lower() for s in profile_skills])
        match_score = int((len(matched) / len(job_skills)) * 100) if job_skills else 50
        
        # Return basic CV structure
        cv_content = {
            'summary': getattr(profile, 'summary', f'Professional with experience seeking to contribute to the role.'),
            'work_experience': [
                {
                    'title': exp.title,
                    'company': exp.company,
                    'location': exp.location,
                    'start_date': exp.start_date.strftime('%Y-%m') if exp.start_date else '',
                    'end_date': exp.end_date.strftime('%Y-%m') if exp.end_date else ('Present' if exp.current else ''),
                    'description': exp.description[:300] + '...' if len(exp.description) > 300 else exp.description
                }
                for exp in profile.work_experiences.all()
            ],
            'education': [
                {
                    'degree': edu.degree,
                    'institution': edu.institution,
                    'location': edu.location,
                    'start_date': edu.start_date.strftime('%Y-%m') if edu.start_date else '',
                    'end_date': edu.end_date.strftime('%Y-%m') if edu.end_date else ('Present' if edu.current else ''),
                    'description': edu.description,
                    'gpa': edu.gpa
                }
                for edu in profile.education.all()
            ],
            'skills': [skill.name for skill in profile.skills.all()],
            'projects': [
                {
                    'name': proj.name,
                    'description': proj.description[:100] + '...' if len(proj.description) > 100 else proj.description,
                    'technologies': proj.technologies
                }
                for proj in profile.projects.all()
            ],
            'certifications': [
                {
                    'name': cert.name,
                    'issuer': cert.issuer
                }
                for cert in profile.certifications.all()
            ],
            'languages': [
                {
                    'name': lang.name,
                    'proficiency': lang.proficiency
                }
                for lang in profile.languages.all()
            ],
            'matched_skills': list(matched),
            'missing_skills': [s for s in job_skills if s.lower() not in [ps.lower() for ps in profile_skills]]
        }
        
        analysis = {
            'match_score': match_score,
            'matched_skills': list(matched),
            'missing_skills': [s for s in job_skills if s.lower() not in [ps.lower() for ps in profile_skills]],
            'note': f'AI service ({self.provider}) unavailable due to quota limits. Generated basic CV structure.'
        }
        
        return cv_content, analysis