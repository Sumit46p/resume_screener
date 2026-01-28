"""
Skill normalization database with aliases, variations, and categories.
"""
from typing import Dict, Set, Optional
import re


# Skill aliases: maps variations to canonical names
SKILL_ALIASES: Dict[str, str] = {
    # JavaScript variations
    'js': 'JavaScript',
    'javascript': 'JavaScript',
    'es6': 'JavaScript',
    'es2015': 'JavaScript',
    'ecmascript': 'JavaScript',
    
    # TypeScript variations
    'ts': 'TypeScript',
    'typescript': 'TypeScript',
    
    # Python variations
    'py': 'Python',
    'python': 'Python',
    'python3': 'Python',
    'python2': 'Python',
    
    # React variations
    'react': 'React',
    'reactjs': 'React',
    'react.js': 'React',
    
    # Node.js variations
    'node': 'Node.js',
    'nodejs': 'Node.js',
    'node.js': 'Node.js',
    
    # Database variations
    'postgres': 'PostgreSQL',
    'postgresql': 'PostgreSQL',
    'mysql': 'MySQL',
    'mongo': 'MongoDB',
    'mongodb': 'MongoDB',
    'sql server': 'SQL Server',
    'mssql': 'SQL Server',
    
    # AWS variations
    'aws': 'AWS',
    'amazon web services': 'AWS',
    
    # Azure variations
    'azure': 'Azure',
    'microsoft azure': 'Azure',
    
    # GCP variations
    'gcp': 'Google Cloud',
    'google cloud': 'Google Cloud',
    'google cloud platform': 'Google Cloud',
    
    # Docker variations
    'docker': 'Docker',
    'containerization': 'Docker',
    
    # Kubernetes variations
    'k8s': 'Kubernetes',
    'kubernetes': 'Kubernetes',
    
    # C# variations
    'c#': 'C#',
    'csharp': 'C#',
    'c sharp': 'C#',
    
    # C++ variations
    'c++': 'C++',
    'cpp': 'C++',
    
    # .NET variations
    '.net': '.NET',
    'dotnet': '.NET',
    'dot net': '.NET',
    
    # Machine Learning variations
    'ml': 'Machine Learning',
    'machine learning': 'Machine Learning',
    
    # Artificial Intelligence variations
    'ai': 'Artificial Intelligence',
    'artificial intelligence': 'Artificial Intelligence',
    
    # Deep Learning variations
    'dl': 'Deep Learning',
    'deep learning': 'Deep Learning',
    
    # Natural Language Processing variations
    'nlp': 'NLP',
    'natural language processing': 'NLP',
    
    # TensorFlow variations
    'tensorflow': 'TensorFlow',
    'tf': 'TensorFlow',
    
    # PyTorch variations
    'pytorch': 'PyTorch',
    'torch': 'PyTorch',
    
    # Git variations
    'git': 'Git',
    'github': 'GitHub',
    'gitlab': 'GitLab',
    'bitbucket': 'Bitbucket',
    
    # CI/CD variations
    'ci/cd': 'CI/CD',
    'cicd': 'CI/CD',
    'continuous integration': 'CI/CD',
    'jenkins': 'Jenkins',
    
    # Agile variations
    'agile': 'Agile',
    'scrum': 'Scrum',
    'kanban': 'Kanban',
    
    # Frontend frameworks
    'angular': 'Angular',
    'angularjs': 'Angular',
    'vue': 'Vue.js',
    'vuejs': 'Vue.js',
    'vue.js': 'Vue.js',
    'svelte': 'Svelte',
    'nextjs': 'Next.js',
    'next.js': 'Next.js',
    
    # Backend frameworks
    'django': 'Django',
    'flask': 'Flask',
    'fastapi': 'FastAPI',
    'express': 'Express.js',
    'expressjs': 'Express.js',
    'spring': 'Spring',
    'spring boot': 'Spring Boot',
    'springboot': 'Spring Boot',
    
    # Mobile
    'react native': 'React Native',
    'flutter': 'Flutter',
    'swift': 'Swift',
    'kotlin': 'Kotlin',
    'ios': 'iOS Development',
    'android': 'Android Development',
    
    # Data Science
    'pandas': 'Pandas',
    'numpy': 'NumPy',
    'scipy': 'SciPy',
    'scikit-learn': 'Scikit-learn',
    'sklearn': 'Scikit-learn',
    'matplotlib': 'Matplotlib',
    'seaborn': 'Seaborn',
    
    # Big Data
    'spark': 'Apache Spark',
    'apache spark': 'Apache Spark',
    'hadoop': 'Hadoop',
    'kafka': 'Apache Kafka',
    'apache kafka': 'Apache Kafka',
    
    # Testing
    'jest': 'Jest',
    'mocha': 'Mocha',
    'pytest': 'pytest',
    'unittest': 'unittest',
    'selenium': 'Selenium',
    'cypress': 'Cypress',
    
    # APIs
    'rest': 'REST API',
    'restful': 'REST API',
    'rest api': 'REST API',
    'graphql': 'GraphQL',
    'grpc': 'gRPC',
}

# Skill categories: core skills vs tools vs soft skills
SKILL_CATEGORIES: Dict[str, Set[str]] = {
    'programming_languages': {
        'JavaScript', 'TypeScript', 'Python', 'Java', 'C#', 'C++', 'C',
        'Go', 'Rust', 'Ruby', 'PHP', 'Swift', 'Kotlin', 'Scala', 'R',
        'MATLAB', 'Perl', 'Haskell', 'Elixir', 'Clojure'
    },
    'frontend': {
        'React', 'Angular', 'Vue.js', 'Svelte', 'Next.js', 'HTML', 'CSS',
        'Sass', 'Less', 'Tailwind CSS', 'Bootstrap', 'Material UI',
        'Redux', 'MobX', 'Webpack', 'Vite', 'jQuery'
    },
    'backend': {
        'Node.js', 'Django', 'Flask', 'FastAPI', 'Express.js', 'Spring',
        'Spring Boot', '.NET', 'Ruby on Rails', 'Laravel', 'ASP.NET'
    },
    'databases': {
        'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Elasticsearch',
        'SQL Server', 'Oracle', 'SQLite', 'Cassandra', 'DynamoDB',
        'Firebase', 'Neo4j'
    },
    'cloud': {
        'AWS', 'Azure', 'Google Cloud', 'Heroku', 'DigitalOcean',
        'Vercel', 'Netlify', 'Cloudflare'
    },
    'devops': {
        'Docker', 'Kubernetes', 'CI/CD', 'Jenkins', 'GitHub Actions',
        'GitLab CI', 'Terraform', 'Ansible', 'Linux', 'Nginx', 'Apache'
    },
    'data_science': {
        'Machine Learning', 'Deep Learning', 'NLP', 'TensorFlow',
        'PyTorch', 'Keras', 'Scikit-learn', 'Pandas', 'NumPy',
        'Data Analysis', 'Statistics', 'Computer Vision'
    },
    'mobile': {
        'React Native', 'Flutter', 'iOS Development', 'Android Development',
        'Swift', 'Kotlin', 'Xamarin'
    },
    'tools': {
        'Git', 'GitHub', 'GitLab', 'Bitbucket', 'Jira', 'Confluence',
        'Slack', 'VS Code', 'IntelliJ', 'Postman', 'Figma'
    },
    'soft_skills': {
        'Leadership', 'Communication', 'Teamwork', 'Problem Solving',
        'Critical Thinking', 'Time Management', 'Agile', 'Scrum',
        'Project Management', 'Mentoring'
    },
    'testing': {
        'Jest', 'Mocha', 'pytest', 'Selenium', 'Cypress', 'JUnit',
        'TestNG', 'Unit Testing', 'Integration Testing', 'E2E Testing',
        'TDD', 'BDD'
    }
}


class SkillDatabase:
    """Database for skill normalization and categorization."""
    
    def __init__(self):
        self._aliases = {k.lower(): v for k, v in SKILL_ALIASES.items()}
        self._categories = SKILL_CATEGORIES
        self._all_skills = self._build_skill_set()
    
    def _build_skill_set(self) -> Set[str]:
        """Build a set of all known skills."""
        skills = set()
        for category_skills in self._categories.values():
            skills.update(category_skills)
        skills.update(self._aliases.values())
        return skills
    
    def normalize(self, skill: str) -> str:
        """
        Normalize a skill name to its canonical form.
        
        Args:
            skill: Raw skill name
            
        Returns:
            Normalized skill name
        """
        skill_lower = skill.lower().strip()
        
        # Check aliases first
        if skill_lower in self._aliases:
            return self._aliases[skill_lower]
        
        # Check if it's already a known skill (case-insensitive)
        for known_skill in self._all_skills:
            if skill_lower == known_skill.lower():
                return known_skill
        
        # Return with proper title case if not found
        return skill.strip().title()
    
    def get_category(self, skill: str) -> Optional[str]:
        """
        Get the category of a skill.
        
        Args:
            skill: Skill name (will be normalized)
            
        Returns:
            Category name or None if not categorized
        """
        normalized = self.normalize(skill)
        
        for category, skills in self._categories.items():
            if normalized in skills:
                return category
        
        return None
    
    def is_core_skill(self, skill: str) -> bool:
        """Check if a skill is a core/programming skill."""
        category = self.get_category(skill)
        return category in {'programming_languages', 'frontend', 'backend', 
                          'databases', 'data_science'}
    
    def is_tool(self, skill: str) -> bool:
        """Check if a skill is a tool."""
        category = self.get_category(skill)
        return category in {'tools', 'devops', 'testing'}
    
    def get_related_skills(self, skill: str) -> Set[str]:
        """Get skills in the same category."""
        category = self.get_category(skill)
        if category:
            return self._categories[category].copy()
        return set()
