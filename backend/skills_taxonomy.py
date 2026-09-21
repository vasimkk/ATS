"""
Skills and keywords taxonomy for ATS Resume Matcher.
Includes categorized hard skills, soft skills, toolsets, and synonyms.
"""
import re
from typing import Dict, List, Set, Tuple

# Comprehensive taxonomy categorized by domains
SKILLS_TAXONOMY: Dict[str, List[str]] = {
    "Programming Languages": [
        "python", "javascript", "typescript", "java", "c++", "c#", "golang", "go",
        "rust", "ruby", "php", "swift", "kotlin", "scala", "r", "sql", "bash",
        "shell", "html", "html5", "css", "css3", "sass", "scss", "perl", "dart"
    ],
    "Frameworks & Libraries": [
        "react", "react.js", "reactjs", "angular", "vue", "vue.js", "vuejs",
        "next.js", "nextjs", "nuxt", "nuxt.js", "node.js", "nodejs", "express",
        "express.js", "nestjs", "django", "flask", "fastapi", "spring boot",
        "spring", "asp.net", ".net core", "ruby on rails", "laravel", "tailwind",
        "tailwindcss", "bootstrap", "material-ui", "redux", "mobx", "zustand",
        "graphql", "rest api", "restful api", "grpc", "webpack", "vite", "babel"
    ],
    "Databases & Storage": [
        "postgresql", "postgres", "mysql", "mongodb", "redis", "sqlite", "oracle",
        "microsoft sql server", "mssql", "cassandra", "dynamodb", "elasticsearch",
        "neo4j", "snowflake", "bigquery", "supabase", "firebase", "mariadb"
    ],
    "Cloud & DevOps": [
        "aws", "amazon web services", "azure", "microsoft azure", "gcp",
        "google cloud platform", "docker", "kubernetes", "k8s", "terraform",
        "ansible", "jenkins", "github actions", "gitlab ci", "ci/cd", "continuous integration",
        "continuous deployment", "linux", "ubuntu", "nginx", "apache", "helm",
        "prometheus", "grafana", "serverless", "microservices", "cloudformation"
    ],
    "AI, ML & Data Science": [
        "machine learning", "deep learning", "artificial intelligence", "data science",
        "pytorch", "tensorflow", "scikit-learn", "pandas", "numpy", "scipy",
        "nlp", "natural language processing", "computer vision", "llm", "large language models",
        "generative ai", "langchain", "llamaindex", "rag", "hugging face", "transformers",
        "opencv", "data analysis", "data engineering", "power bi", "tableau", "spark", "hadoop"
    ],
    "Testing & Quality Assurance": [
        "unit testing", "integration testing", "e2e testing", "jest", "pytest",
        "cypress", "selenium", "playwright", "junit", "mocha", "tdd", "test driven development",
        "bdd", "behavior driven development", "postman", "qa", "automation testing"
    ],
    "Methodologies & Architecture": [
        "agile", "scrum", "kanban", "system design", "software architecture",
        "microservices architecture", "clean architecture", "design patterns",
        "object oriented programming", "oop", "sdlc", "mvc", "event-driven architecture"
    ],
    "Tools & Platforms": [
        "git", "github", "gitlab", "bitbucket", "jira", "confluence", "trello",
        "vscode", "visual studio", "intellij", "figma", "postman", "swagger", "openapi"
    ],
    "Soft Skills & Leadership": [
        "leadership", "communication", "team collaboration", "cross-functional collaboration",
        "problem solving", "critical thinking", "project management", "time management",
        "mentorship", "adaptability", "analytical thinking", "stakeholder management",
        "client relations", "presentation skills", "work ethic", "decision making"
    ]
}

# Common abbreviations and canonical mapping
SYNONYM_MAP: Dict[str, str] = {
    "reactjs": "react",
    "react.js": "react",
    "nodejs": "node.js",
    "k8s": "kubernetes",
    "postgres": "postgresql",
    "amazon web services": "aws",
    "google cloud platform": "gcp",
    "microsoft azure": "azure",
    "golang": "go",
    "vuejs": "vue",
    "vue.js": "vue",
    "nextjs": "next.js",
    "nuxtjs": "nuxt",
    "expressjs": "express",
    "tailwind": "tailwindcss",
    "mssql": "microsoft sql server",
    "continuous integration": "ci/cd",
    "continuous deployment": "ci/cd",
    "test driven development": "tdd",
    "natural language processing": "nlp",
    "large language models": "llm",
    "generative ai": "gen ai"
}

# Strong action verbs for ATS impact bullet points
ACTION_VERBS: List[str] = [
    "Architected", "Engineered", "Spearheaded", "Pioneered", "Implemented",
    "Optimized", "Scaled", "Streamlined", "Automated", "Delivered",
    "Accelerated", "Orchestrated", "Overhauled", "Formulated", "Enhanced",
    "Standardized", "Reduced", "Boosted", "Designed", "Consolidated"
]

# Flattened set of all known skill names
ALL_SKILLS: Set[str] = {
    skill.lower() for cat_skills in SKILLS_TAXONOMY.values() for skill in cat_skills
}

def canonicalize_skill(skill: str) -> str:
    """Normalize skill name using synonym map."""
    s = skill.lower().strip()
    return SYNONYM_MAP.get(s, s)

def find_category_for_skill(skill: str) -> str:
    """Find which category a skill belongs to."""
    s = skill.lower().strip()
    for cat, skills in SKILLS_TAXONOMY.items():
        if s in [k.lower() for k in skills] or SYNONYM_MAP.get(s) in [k.lower() for k in skills]:
            return cat
    return "Other Technical Skills"

def extract_skills_from_text(text: str) -> Dict[str, List[str]]:
    """
    Extract recognized skills from arbitrary text, grouped by category.
    Returns: { category: [matched_skill_name, ...] }
    """
    found_by_cat: Dict[str, Set[str]] = {}
    normalized_text = " " + text.lower() + " "
    # Replace punctuation for safe matching, keep dots for .js, .net, and pluses for c++
    clean_text = re.sub(r'[^\w\s\.\+\#\-]', ' ', normalized_text)

    for cat, skills in SKILLS_TAXONOMY.items():
        matched_in_cat = set()
        for skill in skills:
            skill_lower = skill.lower()
            # Handle special short tokens like c++, c#, go, r
            if skill_lower == "c++":
                if re.search(r'(?:\b|[\s])c\+\+(?:[\s\.\,\;]|$)', normalized_text):
                    matched_in_cat.add("C++")
            elif skill_lower == "c#":
                if re.search(r'(?:\b|[\s])c\#(?:[\s\.\,\;]|$)', normalized_text):
                    matched_in_cat.add("C#")
            elif skill_lower in ["r", "c", "go"]:
                # strict word boundaries
                if re.search(r'\b' + re.escape(skill_lower) + r'\b', normalized_text):
                    matched_in_cat.add(skill.capitalize() if skill_lower != "go" else "Go")
            elif "." in skill_lower:
                # e.g., node.js, next.js
                escaped = re.escape(skill_lower)
                if re.search(r'\b' + escaped + r'(?:\b|$)', normalized_text):
                    matched_in_cat.add(skill.title() if ".js" not in skill_lower else skill)
            else:
                pattern = r'\b' + re.escape(skill_lower) + r'\b'
                if re.search(pattern, clean_text):
                    matched_in_cat.add(skill.title() if len(skill) > 3 else skill.upper())
        
        if matched_in_cat:
            found_by_cat[cat] = sorted(list(matched_in_cat))

    return {k: v for k, v in found_by_cat.items() if v}
