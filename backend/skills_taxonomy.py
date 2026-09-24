"""
Skills and keywords taxonomy for ATS Resume Matcher.
Now powered by SkillNer & SpaCy for dynamic extraction of 13,000+ skills!
"""
import spacy
from spacy.matcher import PhraseMatcher  # type: ignore
from skillNer.skill_extractor_class import SkillExtractor  # type: ignore
from skillNer.general_params import SKILL_DB  # type: ignore
from typing import Dict, List, Set

print("Initializing SkillNer NLP Engine (This takes a few seconds on startup)...")
try:
    nlp = spacy.load("en_core_web_sm")
    skill_extractor = SkillExtractor(nlp, SKILL_DB, PhraseMatcher)
    print("SkillNer NLP Engine loaded successfully!")
except Exception as e:
    print(f"Warning: Failed to load SkillNer/SpaCy model: {e}")
    skill_extractor = None




def canonicalize_skill(skill: str) -> str:
    """Normalize skill name."""
    return skill.strip()

def find_category_for_skill(skill: str) -> str:
    """Find which category a skill belongs to using SkillNer DB."""
    s = skill.lower().strip()
    for skill_info in SKILL_DB.values():
        if skill_info.get('skill_name', '').lower() == s:
            return skill_info.get('skill_type', 'Other Technical Skills')
    return "Other Technical Skills"

def extract_skills_from_text(text: str) -> Dict[str, List[str]]:
    """
    Extract recognized skills from arbitrary text using SkillNer.
    Returns: { category: [matched_skill_name, ...] }
    """
    if not skill_extractor or not text.strip():
        return {}
        
    found_by_cat: Dict[str, Set[str]] = {}
    
    try:
        # Annotate text with NLP
        annotations = skill_extractor.annotate(text)
        results = annotations.get('results', {})
        
        def process_matches(match_list):
            for match in match_list:
                skill_id = match.get('skill_id')
                if skill_id and skill_id in SKILL_DB:
                    skill_info = SKILL_DB[skill_id]
                    skill_name = skill_info.get('skill_name')
                    
                    # SkillNer uses 'Hard Skill', 'Soft Skill', 'Certification'
                    skill_type = skill_info.get('skill_type', 'Technical Skills')
                    if skill_type == 'Hard Skill':
                        skill_type = 'Core Technical Skills'
                        
                    if skill_name:
                        if skill_type not in found_by_cat:
                            found_by_cat[skill_type] = set()
                        found_by_cat[skill_type].add(skill_name)
                        
        process_matches(results.get('full_matches', []))
        process_matches(results.get('ngram_scored', []))
        
    except Exception as e:
        print(f"SkillNer extraction failed: {e}")
        
    return {k: sorted(list(v)) for k, v in found_by_cat.items() if v}

