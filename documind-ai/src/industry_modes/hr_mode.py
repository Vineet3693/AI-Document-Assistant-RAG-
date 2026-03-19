"""
HR Mode - Resume screening, job matching, and candidate evaluation
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import re


class HRMode:
    """Specialized processing for HR documents and resume screening"""
    
    def __init__(self):
        self.skill_categories = {
            'technical': ['python', 'java', 'javascript', 'sql', 'aws', 'docker', 'kubernetes', 'react', 'node', 'api'],
            'soft': ['leadership', 'communication', 'teamwork', 'problem-solving', 'analytical', 'strategic'],
            'management': ['project management', 'agile', 'scrum', 'team lead', 'manager', 'director'],
            'domain': ['finance', 'healthcare', 'retail', 'manufacturing', 'education', 'legal']
        }
        
        self.education_patterns = [
            r'\b(Bachelor[\'s]?|B\.?S\.?|B\.?A\.?)\s+(?:in|of)\s+([A-Za-z\s]+)',
            r'\b(Master[\'s]?|M\.?S\.?|M\.?A\.?|MBA)\s+(?:in|of)\s+([A-Za-z\s]+)',
            r'\b(Ph\.?D\.?|Doctorate)\s+(?:in|of)\s+([A-Za-z\s]+)',
            r'\b(?:degree|diploma)\s+(?:in|of)\s+([A-Za-z\s]+)',
        ]
        
        self.experience_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:years?|yrs?|y\.?)\s+(?:of\s+)?(?:experience|exp\.?)',
            r'(?:worked|employed)\s+(?:for|as)\s+(\d+(?:\.\d+)?)\s*(?:years?|yrs?)',
        ]
    
    def parse_resume(self, text: str) -> Dict[str, Any]:
        """Parse resume into structured data"""
        return {
            'name': self._extract_name(text),
            'contact': self._extract_contact(text),
            'summary': self._extract_summary(text),
            'experience': self._extract_experience(text),
            'education': self._extract_education(text),
            'skills': self._extract_skills(text),
            'certifications': self._extract_certifications(text),
            'total_years': self._calculate_total_years(text)
        }
    
    def _extract_name(self, text: str) -> str:
        """Extract candidate name (first line usually)"""
        lines = text.strip().split('\n')
        if lines:
            # Simple heuristic: first non-empty line that's short
            for line in lines[:5]:
                line = line.strip()
                if line and len(line) < 50 and not any(x in line for x in ['@', '.', 'http']):
                    return line
        return "Unknown"
    
    def _extract_contact(self, text: str) -> Dict[str, str]:
        """Extract contact information"""
        contact = {}
        
        # Email
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        if email_match:
            contact['email'] = email_match.group(0)
        
        # Phone
        phone_match = re.search(r'\+?[\d\s\-\(\)]{10,}', text)
        if phone_match:
            contact['phone'] = phone_match.group(0)
        
        # LinkedIn
        linkedin_match = re.search(r'linkedin\.com/in/[\w\-]+', text)
        if linkedin_match:
            contact['linkedin'] = linkedin_match.group(0)
        
        # Location
        location_match = re.search(r'(?:located|based)[:\s]+([A-Za-z\s,]+)', text, re.IGNORECASE)
        if location_match:
            contact['location'] = location_match.group(1).strip()
        
        return contact
    
    def _extract_summary(self, text: str) -> str:
        """Extract professional summary"""
        patterns = [
            r'(?:summary|profile|about)[:\s]+(.+?)(?=\n\s*\n|\b(experience|education|skills)\b)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def _extract_experience(self, text: str) -> List[Dict[str, str]]:
        """Extract work experience"""
        experiences = []
        
        # Look for job entries (simplified)
        job_pattern = r'((?:Senior|Junior|Lead|Principal)?\s*[A-Za-z\s]+(?:Engineer|Developer|Manager|Director|Analyst|Designer|Architect))'
        
        matches = re.finditer(job_pattern, text, re.IGNORECASE)
        for match in matches:
            experiences.append({
                'title': match.group(1).strip(),
                'context': match.group(0)[:200]  # First 200 chars
            })
        
        return experiences[:5]  # Top 5 positions
    
    def _extract_education(self, text: str) -> List[Dict[str, str]]:
        """Extract education history"""
        education = []
        
        for pattern in self.education_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                education.append({
                    'degree': match.group(1),
                    'field': match.group(2).strip() if match.lastindex >= 2 else '',
                    'raw': match.group(0)
                })
        
        return education
    
    def _extract_skills(self, text: str) -> Dict[str, List[str]]:
        """Extract and categorize skills"""
        text_lower = text.lower()
        categorized = {
            'technical': [],
            'soft': [],
            'management': [],
            'domain': []
        }
        
        for category, skills in self.skill_categories.items():
            for skill in skills:
                if skill in text_lower:
                    categorized[category].append(skill)
        
        # Also extract from explicit skills section
        skills_section = re.search(r'skills[:\s]+(.+?)(?=\n\s*\n|education|experience)', text, re.IGNORECASE | re.DOTALL)
        if skills_section:
            # Split by common delimiters
            extracted = re.split(r'[,;|]', skills_section.group(1))
            for skill in extracted:
                skill = skill.strip().lower()
                if skill and len(skill) > 2:
                    # Add to appropriate category if not already there
                    for cat in categorized:
                        if any(s in skill for s in self.skill_categories[cat]) and skill not in categorized[cat]:
                            categorized[cat].append(skill)
        
        return categorized
    
    def _extract_certifications(self, text: str) -> List[str]:
        """Extract certifications"""
        cert_patterns = [
            r'\b(AWS|Azure|GCP)\s+Certified\s+[A-Za-z\s]+',
            r'\b(PMP|CISSP|CFA|CPA|Six Sigma)\b',
            r'\bCertified\s+[A-Za-z\s]+',
        ]
        
        certs = []
        for pattern in cert_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            certs.extend(matches)
        
        return list(set(certs))[:10]
    
    def _calculate_total_years(self, text: str) -> float:
        """Calculate total years of experience"""
        total = 0.0
        
        for pattern in self.experience_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    years = float(match)
                    total = max(total, years)  # Take the maximum found
                except ValueError:
                    pass
        
        return total
    
    def score_candidate(self, resume_text: str, job_description: str, required_skills: List[str]) -> Dict[str, Any]:
        """Score candidate against job requirements"""
        resume_data = self.parse_resume(resume_text)
        
        # Skills match
        all_resume_skills = []
        for category_skills in resume_data['skills'].values():
            all_resume_skills.extend([s.lower() for s in category_skills])
        
        required_lower = [s.lower() for s in required_skills]
        matched_skills = [s for s in required_lower if s in all_resume_skills]
        skills_score = (len(matched_skills) / len(required_skills) * 100) if required_skills else 0
        
        # Experience match
        exp_score = min(100, (resume_data['total_years'] / 3) * 100)  # Assume 3 years is baseline
        
        # Calculate overall score
        overall_score = (skills_score * 0.6) + (exp_score * 0.4)
        
        # Determine recommendation
        if overall_score >= 80:
            recommendation = "STRONG YES"
        elif overall_score >= 60:
            recommendation = "YES"
        elif overall_score >= 40:
            recommendation = "MAYBE"
        else:
            recommendation = "NO"
        
        return {
            'candidate_name': resume_data['name'],
            'skills_match': {
                'score': round(skills_score, 1),
                'matched': matched_skills,
                'missing': [s for s in required_lower if s not in matched_skills]
            },
            'experience_match': {
                'score': round(exp_score, 1),
                'years': resume_data['total_years']
            },
            'overall_score': round(overall_score, 1),
            'recommendation': recommendation,
            'key_strengths': self._identify_strengths(resume_data, required_lower),
            'gaps': self._identify_gaps(resume_data, required_lower),
            'suggested_questions': self._generate_interview_questions(resume_data, required_lower)
        }
    
    def _identify_strengths(self, resume_data: Dict, required_skills: List[str]) -> List[str]:
        """Identify candidate strengths"""
        strengths = []
        
        if resume_data['total_years'] > 5:
            strengths.append(f"Extensive experience ({resume_data['total_years']} years)")
        
        all_skills = []
        for cat_skills in resume_data['skills'].values():
            all_skills.extend(cat_skills)
        
        matched = [s for s in all_skills if s.lower() in required_skills]
        if matched:
            strengths.append(f"Strong match on key skills: {', '.join(matched[:3])}")
        
        if resume_data['education']:
            strengths.append(f"Relevant education: {resume_data['education'][0].get('degree', '')}")
        
        if resume_data['certifications']:
            strengths.append(f"Professional certifications: {', '.join(resume_data['certifications'][:2])}")
        
        return strengths
    
    def _identify_gaps(self, resume_data: Dict, required_skills: List[str]) -> List[str]:
        """Identify skill/experience gaps"""
        gaps = []
        
        all_skills = []
        for cat_skills in resume_data['skills'].values():
            all_skills.extend([s.lower() for s in cat_skills])
        
        missing = [s for s in required_skills if s not in all_skills]
        if missing:
            gaps.append(f"Missing skills: {', '.join(missing[:3])}")
        
        if resume_data['total_years'] < 2:
            gaps.append("Limited professional experience")
        
        return gaps
    
    def _generate_interview_questions(self, resume_data: Dict, required_skills: List[str]) -> List[str]:
        """Generate targeted interview questions"""
        questions = []
        
        # Gap-based questions
        all_skills = []
        for cat_skills in resume_data['skills'].values():
            all_skills.extend([s.lower() for s in cat_skills])
        
        missing = [s for s in required_skills if s not in all_skills][:2]
        for skill in missing:
            questions.append(f"How would you approach learning {skill} if hired?")
        
        # Experience verification
        if resume_data['experience']:
            questions.append(f"Can you describe your most challenging project as a {resume_data['experience'][0]['title']}?")
        
        # Behavioral
        questions.append("Tell me about a time you had to solve a complex technical problem under pressure.")
        
        # Technical
        if required_skills:
            questions.append(f"Walk me through how you've applied {required_skills[0]} in a real project.")
        
        return questions[:5]
    
    def get_prompt_template(self) -> str:
        """Return the HR/resume screening prompt template"""
        return """You are a senior HR professional and talent acquisition specialist.

JOB REQUIREMENTS:
Role: {role}
Required Skills: {required_skills}
Minimum Experience: {min_years} years

JOB DESCRIPTION:
{job_description}

CANDIDATE RESUME:
{resume_text}

Evaluate the candidate objectively based ONLY on skills and experience. Never consider age, gender, race, or nationality.

Provide:
1. Candidate Profile Summary
2. Skills Match Analysis (with table)
3. Strengths and Gaps
4. Scoring (Skills, Experience, Education, Overall)
5. Recommendation (STRONG YES/YES/MAYBE/NO)
6. Suggested Interview Questions

Be fair, unbiased, and focus on qualifications only."""
