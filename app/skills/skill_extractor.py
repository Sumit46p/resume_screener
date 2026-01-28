"""
Contextual skill extractor - goes beyond simple keyword matching.
"""
import re
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass
from .skill_database import SkillDatabase


@dataclass
class ExtractedSkill:
    """A skill extracted from resume with context."""
    name: str
    normalized_name: str
    category: str
    experience_level: str  # 'mentioned', 'used', 'proficient', 'expert'
    context: str  # The sentence/phrase where it was found
    years: float  # Estimated years if detectable


class SkillExtractor:
    """
    Extract skills from resume text with contextual understanding.
    Not just keyword matching - understands experience level from context.
    """
    
    # Experience level patterns
    EXPERT_PATTERNS = [
        r'(?:expert|advanced|senior|lead|architect)\s+(?:in|with|level)?\s*{skill}',
        r'{skill}\s+(?:expert|architect|lead)',
        r'(?:deep|extensive|strong)\s+(?:experience|expertise|knowledge)\s+(?:in|with)\s+{skill}',
        r'(?:\d+\+?\s*years?|[5-9]\d*\s*years?)\s+(?:of\s+)?(?:experience\s+)?(?:in|with)\s+{skill}',
    ]
    
    PROFICIENT_PATTERNS = [
        r'(?:proficient|experienced|skilled)\s+(?:in|with)\s+{skill}',
        r'{skill}\s+(?:developer|engineer|specialist)',
        r'(?:worked|working)\s+(?:extensively\s+)?(?:with|on)\s+{skill}',
        r'(?:[2-4]\s*years?)\s+(?:of\s+)?(?:experience\s+)?(?:in|with)\s+{skill}',
        r'(?:built|developed|created|implemented)\s+.*{skill}',
    ]
    
    USED_PATTERNS = [
        r'(?:used|using|worked\s+with)\s+{skill}',
        r'{skill}\s+(?:for|in)\s+',
        r'(?:experience|knowledge)\s+(?:in|with|of)\s+{skill}',
        r'(?:familiar|comfortable)\s+(?:with)\s+{skill}',
    ]
    
    MENTIONED_PATTERNS = [
        r'\b{skill}\b',
    ]
    
    def __init__(self):
        self.db = SkillDatabase()
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Pre-compile regex patterns for efficiency."""
        # Build a mega-pattern to find potential skills
        all_skills = []
        for alias in self.db._aliases.keys():
            all_skills.append(re.escape(alias))
        for skill in self.db._all_skills:
            all_skills.append(re.escape(skill.lower()))
        
        # Sort by length (longest first) to match longer skills first
        all_skills = sorted(set(all_skills), key=len, reverse=True)
        self._skill_pattern = re.compile(
            r'\b(' + '|'.join(all_skills) + r')\b',
            re.IGNORECASE
        )
    
    def extract_skills(self, text: str) -> List[ExtractedSkill]:
        """
        Extract all skills from text with context awareness.
        
        Args:
            text: Resume text
            
        Returns:
            List of extracted skills with metadata
        """
        skills = []
        seen_skills = set()  # Track normalized names to avoid duplicates
        
        # Split text into sentences for context
        sentences = self._split_sentences(text)
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            # Find all skill mentions in this sentence
            matches = self._skill_pattern.findall(sentence_lower)
            
            for match in matches:
                normalized = self.db.normalize(match)
                
                # Skip if we've already seen this skill
                if normalized.lower() in seen_skills:
                    continue
                seen_skills.add(normalized.lower())
                
                # Determine experience level from context
                level, years = self._detect_experience_level(sentence, match)
                
                # Get category
                category = self.db.get_category(normalized) or 'other'
                
                skills.append(ExtractedSkill(
                    name=match,
                    normalized_name=normalized,
                    category=category,
                    experience_level=level,
                    context=sentence.strip(),
                    years=years
                ))
        
        return skills
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting
        sentences = re.split(r'[.!?\n]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _detect_experience_level(self, context: str, skill: str) -> Tuple[str, float]:
        """
        Detect experience level from context.
        
        Returns:
            Tuple of (level, estimated_years)
        """
        context_lower = context.lower()
        skill_pattern = re.escape(skill.lower())
        
        # Check expert patterns
        for pattern in self.EXPERT_PATTERNS:
            if re.search(pattern.format(skill=skill_pattern), context_lower):
                years = self._extract_years(context)
                return ('expert', years if years > 0 else 5.0)
        
        # Check proficient patterns
        for pattern in self.PROFICIENT_PATTERNS:
            if re.search(pattern.format(skill=skill_pattern), context_lower):
                years = self._extract_years(context)
                return ('proficient', years if years > 0 else 3.0)
        
        # Check used patterns
        for pattern in self.USED_PATTERNS:
            if re.search(pattern.format(skill=skill_pattern), context_lower):
                years = self._extract_years(context)
                return ('used', years if years > 0 else 1.0)
        
        # Default to mentioned
        return ('mentioned', 0.0)
    
    def _extract_years(self, context: str) -> float:
        """Extract years of experience from context."""
        # Pattern: "X years" or "X+ years"
        years_match = re.search(r'(\d+)\+?\s*years?', context.lower())
        if years_match:
            return float(years_match.group(1))
        return 0.0
    
    def get_skill_summary(self, skills: List[ExtractedSkill]) -> Dict:
        """
        Get a summary of extracted skills by category and level.
        """
        summary = {
            'total_skills': len(skills),
            'by_category': {},
            'by_level': {
                'expert': [],
                'proficient': [],
                'used': [],
                'mentioned': []
            },
            'core_skills': [],
            'tools': []
        }
        
        for skill in skills:
            # By category
            if skill.category not in summary['by_category']:
                summary['by_category'][skill.category] = []
            summary['by_category'][skill.category].append(skill.normalized_name)
            
            # By level
            summary['by_level'][skill.experience_level].append(skill.normalized_name)
            
            # Core vs tools
            if self.db.is_core_skill(skill.normalized_name):
                summary['core_skills'].append(skill.normalized_name)
            elif self.db.is_tool(skill.normalized_name):
                summary['tools'].append(skill.normalized_name)
        
        return summary
