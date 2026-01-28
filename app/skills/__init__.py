"""
Skills extraction, normalization, and categorization module.
"""
from .skill_database import SkillDatabase, SKILL_ALIASES, SKILL_CATEGORIES
from .skill_extractor import SkillExtractor
from .experience_detector import ExperienceDetector

__all__ = [
    'SkillDatabase',
    'SKILL_ALIASES',
    'SKILL_CATEGORIES',
    'SkillExtractor',
    'ExperienceDetector'
]
