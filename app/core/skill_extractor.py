
import json
import logging
import os
from typing import Dict, List, Set, Any

from fuzzywuzzy import fuzz, process

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SkillExtractor:
    def __init__(self, db_path: str = "data/skills_database.json"):
        """
        Initialize the SkillExtractor with a JSON database of skills.
        """
        # Resolve absolute path relative to project root if needed
        # Assuming run from project root, but let's be safe
        if not os.path.exists(db_path):
             # Try to find it relative to this file
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            potential_path = os.path.join(base_dir, db_path)
            if os.path.exists(potential_path):
                db_path = potential_path
            else:
                logger.error(f"Skills database not found at {db_path} or {potential_path}")
                raise FileNotFoundError(f"Skills database not found at {db_path}")

        logger.info(f"Loading skills database from {db_path}...")
        with open(db_path, 'r') as f:
            self.skills_db = json.load(f)
        
        # Flatten database for easier lookup if needed, but keeping structure is good for categorization
        self.categories = self.skills_db.keys()

    def extract_skills(self, text: str, threshold: int = 90) -> Dict[str, List[str]]:
        """
        Extracts skills from text using fuzzy matching against the database.
        
        Args:
            text (str): The input text (resume or job description).
            threshold (int): The fuzzy matching score threshold (0-100). 
                             Higher is stricter. 90 is recommended to avoid false positives.

        Returns:
            Dict[str, List[str]]: A dictionary where keys are categories (e.g., 'programming_languages')
                                  and values are lists of found unique skills.
        """
        found_skills: Dict[str, Set[str]] = {cat: set() for cat in self.categories}
        
        # Pre-process text simply (lowercasing done by fuzzywuzzy usually, but good practice)
        # However, fuzzywuzzy handles case.
        # We need to be careful. Direct fuzzy matching against the whole text is expensive and inaccurate.
        # Better approach: 
        # 1. Tokenize text or n-grams? 
        # 2. Or iterate through ALL skills and search them in text?
        # Iterating through skills is reasonably fast for ~100-500 skills.
        
        # To make it efficient and accurate:
        # We search if the skill name (or alias) is "in" the text.
        # Partial ratio is good for finding "Python" in "I know Python programming".
        
        normalized_text = text.lower()
        unique_tokens = set(normalized_text.split())

        for category, skills_list in self.skills_db.items():
            for skill_entry in skills_list:
                skill_name = skill_entry["name"]
                variations = [skill_name] + skill_entry.get("aliases", [])
                
                for variation in variations:
                    v_lower = variation.lower()
                    
                    # 1. Exact match (case-insensitive word boundary)
                    import re
                    escaped = re.escape(v_lower)
                    pattern = r'(?:^|[\s,.;\(\)\[\]])' + escaped + r'(?:$|[\s,.;\(\)\[\]])'
                    
                    if re.search(pattern, normalized_text):
                        found_skills[category].add(skill_name)
                        break
                        
                    # 2. Fuzzy match for typo tolerance (only for longer words)
                    if len(v_lower) >= 4:
                        match = process.extractOne(variation, unique_tokens, scorer=fuzz.ratio)
                        if match:
                            best_token, score = match
                            if score >= threshold:
                                logger.info(f"Fuzzy match found: '{best_token}' -> '{skill_name}' (Score: {score})")
                                found_skills[category].add(skill_name)
                                break

        # Convert sets to sorted lists
        return {k: sorted(list(v)) for k, v in found_skills.items()}

if __name__ == "__main__":
    # Self-test
    extractor = SkillExtractor()
    
    sample_resume = """
    I am an experienced software engineer.
    Expertise in Pyton, Java, and ReactJS.
    Familiar with Dockr and AWS.
    Strong communication and termwork skills.
    I also know C++ and C# very well.
    """
    
    print("--- Processing Sample Resume ---")
    skills = extractor.extract_skills(sample_resume)
    
    import json
    print(json.dumps(skills, indent=2))
