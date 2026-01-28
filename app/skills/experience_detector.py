"""
Experience detector - analyzes work experience, projects, and career trajectory.
"""
import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class WorkExperience:
    """Represents a work experience entry."""
    title: str
    company: str
    duration_months: int
    start_date: Optional[str]
    end_date: Optional[str]
    is_current: bool
    is_internship: bool
    is_freelance: bool
    description: str


@dataclass
class Project:
    """Represents a project entry."""
    name: str
    description: str
    technologies: List[str]
    is_professional: bool  # vs personal/academic


@dataclass
class ExperienceAnalysis:
    """Complete experience analysis result."""
    total_experience_months: int
    relevant_experience_months: int  # Based on JD requirements
    work_experiences: List[WorkExperience]
    projects: List[Project]
    has_career_gaps: bool
    gap_explanation: Optional[str]
    experience_trajectory: str  # 'ascending', 'lateral', 'descending', 'mixed'
    seniority_estimate: str  # 'entry', 'mid', 'senior', 'lead', 'executive'


class ExperienceDetector:
    """
    Detects and analyzes work experience from resume text.
    Handles various formats and edge cases.
    """
    
    # Section headers that indicate work experience
    EXPERIENCE_HEADERS = [
        r'(?:work\s+)?experience',
        r'employment\s+history',
        r'professional\s+experience',
        r'career\s+history',
        r'work\s+history',
    ]
    
    # Section headers that indicate projects
    PROJECT_HEADERS = [
        r'projects?',
        r'personal\s+projects?',
        r'side\s+projects?',
        r'portfolio',
        r'notable\s+projects?',
    ]
    
    # Patterns to detect job titles
    TITLE_PATTERNS = [
        r'(senior|junior|lead|principal|staff|associate)?\s*'
        r'(software|backend|frontend|full[\s-]?stack|web|mobile|devops|data|ml|ai)?\s*'
        r'(engineer|developer|programmer|architect|analyst|scientist|manager|director)',
    ]
    
    # Patterns to detect dates
    DATE_PATTERNS = [
        r'(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|'
        r'jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)'
        r'\s*\.?\s*(\d{4})',
        r'(\d{1,2})/(\d{4})',
        r'(\d{4})\s*[-–]\s*(\d{4}|present|current|now)',
    ]
    
    # Internship indicators
    INTERNSHIP_INDICATORS = ['intern', 'internship', 'trainee', 'apprentice']
    
    # Freelance indicators
    FREELANCE_INDICATORS = ['freelance', 'consultant', 'contractor', 'self-employed', 'independent']
    
    def analyze_experience(self, text: str, required_skills: List[str] = None) -> ExperienceAnalysis:
        """
        Analyze work experience from resume text.
        
        Args:
            text: Resume text
            required_skills: Skills from JD to calculate relevance
            
        Returns:
            Complete experience analysis
        """
        required_skills = required_skills or []
        
        # Extract work experiences
        work_experiences = self._extract_work_experiences(text)
        
        # Extract projects
        projects = self._extract_projects(text)
        
        # Calculate totals
        total_months = sum(exp.duration_months for exp in work_experiences)
        
        # Calculate relevant experience
        relevant_months = self._calculate_relevant_experience(
            work_experiences, projects, required_skills
        )
        
        # Detect career gaps
        has_gaps, gap_explanation = self._detect_career_gaps(work_experiences)
        
        # Analyze trajectory
        trajectory = self._analyze_trajectory(work_experiences)
        
        # Estimate seniority
        seniority = self._estimate_seniority(work_experiences, total_months)
        
        return ExperienceAnalysis(
            total_experience_months=total_months,
            relevant_experience_months=relevant_months,
            work_experiences=work_experiences,
            projects=projects,
            has_career_gaps=has_gaps,
            gap_explanation=gap_explanation,
            experience_trajectory=trajectory,
            seniority_estimate=seniority
        )
    
    def _extract_work_experiences(self, text: str) -> List[WorkExperience]:
        """Extract work experience entries from text."""
        experiences = []
        
        # Try to find the experience section
        exp_section = self._find_section(text, self.EXPERIENCE_HEADERS)
        
        if not exp_section:
            # Fall back to analyzing the whole text
            exp_section = text
        
        # Split into potential entries (by dates or clear separators)
        entries = self._split_into_entries(exp_section)
        
        for entry in entries:
            exp = self._parse_experience_entry(entry)
            if exp:
                experiences.append(exp)
        
        return experiences
    
    def _extract_projects(self, text: str) -> List[Project]:
        """Extract project entries from text."""
        projects = []
        
        # Find project section
        proj_section = self._find_section(text, self.PROJECT_HEADERS)
        
        if not proj_section:
            return projects
        
        # Split and parse projects
        entries = self._split_into_entries(proj_section)
        
        for entry in entries:
            proj = self._parse_project_entry(entry)
            if proj:
                projects.append(proj)
        
        return projects
    
    def _find_section(self, text: str, headers: List[str]) -> Optional[str]:
        """Find a section in the resume by its header."""
        text_lower = text.lower()
        
        for header in headers:
            pattern = rf'\n\s*({header})\s*[:\n]'
            match = re.search(pattern, text_lower)
            
            if match:
                start = match.end()
                # Find the next major section
                next_section = re.search(
                    r'\n\s*(?:education|skills|certif|awards|reference|contact)',
                    text_lower[start:]
                )
                end = start + next_section.start() if next_section else len(text)
                return text[start:end]
        
        return None
    
    def _split_into_entries(self, section: str) -> List[str]:
        """Split a section into individual entries."""
        # Split by double newlines or date patterns
        entries = re.split(r'\n\s*\n', section)
        return [e.strip() for e in entries if e.strip() and len(e.strip()) > 20]
    
    def _parse_experience_entry(self, entry: str) -> Optional[WorkExperience]:
        """Parse a work experience entry."""
        lines = entry.split('\n')
        if not lines:
            return None
        
        # Try to extract title (usually first or second line)
        title = self._extract_title(lines[0]) or "Unknown Position"
        
        # Try to extract company
        company = self._extract_company(entry) or "Unknown Company"
        
        # Try to extract dates
        start_date, end_date, duration = self._extract_dates(entry)
        
        # Check if internship
        is_internship = any(ind in entry.lower() for ind in self.INTERNSHIP_INDICATORS)
        
        # Check if freelance
        is_freelance = any(ind in entry.lower() for ind in self.FREELANCE_INDICATORS)
        
        return WorkExperience(
            title=title,
            company=company,
            duration_months=duration,
            start_date=start_date,
            end_date=end_date,
            is_current=end_date in ['present', 'current', 'now', None] if end_date else True,
            is_internship=is_internship,
            is_freelance=is_freelance,
            description=entry
        )
    
    def _extract_title(self, line: str) -> Optional[str]:
        """Extract job title from a line."""
        for pattern in self.TITLE_PATTERNS:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                return match.group(0).strip().title()
        
        # If no pattern matches, return the cleaned line
        return line.strip()[:100] if len(line.strip()) < 100 else None
    
    def _extract_company(self, entry: str) -> Optional[str]:
        """Extract company name from entry."""
        # Look for "at Company" or "Company - Title" patterns
        patterns = [
            r'(?:at|@)\s+([A-Z][a-zA-Z0-9\s&.]+)',
            r'([A-Z][a-zA-Z0-9\s&.]+)\s*[-|]\s*(?:senior|junior|lead|software)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, entry)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_dates(self, entry: str) -> Tuple[Optional[str], Optional[str], int]:
        """Extract start date, end date, and duration in months."""
        entry_lower = entry.lower()
        
        # Look for year ranges
        year_range = re.search(r'(\d{4})\s*[-–to]+\s*(\d{4}|present|current|now)', entry_lower)
        if year_range:
            start_year = int(year_range.group(1))
            end_str = year_range.group(2)
            
            if end_str in ['present', 'current', 'now']:
                end_year = datetime.now().year
                end_month = datetime.now().month
            else:
                end_year = int(end_str)
                end_month = 12
            
            # Estimate duration (assume mid-year start/end)
            duration = (end_year - start_year) * 12 + (end_month - 6)
            return (str(start_year), end_str, max(1, duration))
        
        # Look for month-year patterns
        month_years = re.findall(
            r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s*(\d{4})',
            entry_lower
        )
        
        if len(month_years) >= 2:
            # Assume first is start, second is end
            months = {'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
                     'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12}
            
            start = f"{month_years[0][0].title()} {month_years[0][1]}"
            end = f"{month_years[1][0].title()} {month_years[1][1]}"
            
            start_month = months[month_years[0][0][:3]]
            start_year = int(month_years[0][1])
            end_month = months[month_years[1][0][:3]]
            end_year = int(month_years[1][1])
            
            duration = (end_year - start_year) * 12 + (end_month - start_month)
            return (start, end, max(1, duration))
        
        return (None, None, 12)  # Default to 1 year if can't parse
    
    def _parse_project_entry(self, entry: str) -> Optional[Project]:
        """Parse a project entry."""
        lines = entry.split('\n')
        if not lines:
            return None
        
        # First line is usually the project name
        name = lines[0].strip()[:100]
        
        # Rest is description
        description = '\n'.join(lines[1:]).strip()
        
        # Extract technologies mentioned
        from .skill_database import SkillDatabase
        db = SkillDatabase()
        
        techs = []
        for alias in db._aliases:
            if re.search(rf'\b{re.escape(alias)}\b', entry, re.IGNORECASE):
                techs.append(db.normalize(alias))
        
        # Determine if professional (look for client/company mentions)
        is_professional = any(word in entry.lower() for word in 
                            ['client', 'company', 'production', 'deployed', 'users'])
        
        return Project(
            name=name,
            description=description,
            technologies=list(set(techs)),
            is_professional=is_professional
        )
    
    def _calculate_relevant_experience(
        self, 
        experiences: List[WorkExperience],
        projects: List[Project],
        required_skills: List[str]
    ) -> int:
        """Calculate months of relevant experience based on required skills."""
        if not required_skills:
            return sum(exp.duration_months for exp in experiences)
        
        relevant_months = 0
        required_lower = [s.lower() for s in required_skills]
        
        for exp in experiences:
            desc_lower = exp.description.lower()
            # Check if any required skill is mentioned
            if any(skill in desc_lower for skill in required_lower):
                relevant_months += exp.duration_months
        
        # Add project experience (weighted less - 50%)
        for proj in projects:
            proj_text = f"{proj.name} {proj.description}".lower()
            if any(skill in proj_text for skill in required_lower):
                relevant_months += 6  # Count each relevant project as 6 months
        
        return relevant_months
    
    def _detect_career_gaps(self, experiences: List[WorkExperience]) -> Tuple[bool, Optional[str]]:
        """Detect significant career gaps."""
        # Simple implementation - would need dates to be more accurate
        # For now, just check if there are gaps mentioned
        return (False, None)
    
    def _analyze_trajectory(self, experiences: List[WorkExperience]) -> str:
        """Analyze career trajectory."""
        if len(experiences) < 2:
            return 'insufficient_data'
        
        # Check for progression in titles
        senior_keywords = ['senior', 'lead', 'principal', 'staff', 'manager', 'director', 'architect']
        
        progression = []
        for exp in experiences:
            title_lower = exp.title.lower()
            has_senior = any(kw in title_lower for kw in senior_keywords)
            progression.append(has_senior)
        
        if all(progression):
            return 'lateral_senior'
        elif progression[-1] and not progression[0]:
            return 'ascending'
        elif progression[0] and not progression[-1]:
            return 'descending'
        else:
            return 'mixed'
    
    def _estimate_seniority(self, experiences: List[WorkExperience], total_months: int) -> str:
        """Estimate seniority level."""
        years = total_months / 12
        
        # Check titles for explicit seniority
        for exp in experiences[:2]:  # Check recent positions
            title_lower = exp.title.lower()
            if any(kw in title_lower for kw in ['director', 'vp', 'vice president', 'cto', 'ceo']):
                return 'executive'
            if any(kw in title_lower for kw in ['lead', 'principal', 'staff', 'manager']):
                return 'lead'
            if 'senior' in title_lower:
                return 'senior'
        
        # Fall back to years of experience
        if years >= 8:
            return 'senior'
        elif years >= 3:
            return 'mid'
        else:
            return 'entry'
