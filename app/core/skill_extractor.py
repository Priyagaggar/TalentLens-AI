
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
        
        normalized_text = text.lower() # Normalize text once

        for category, skills_list in self.skills_db.items():
            for skill_entry in skills_list:
                skill_name = skill_entry["name"]
                variations = [skill_name] + skill_entry.get("aliases", [])
                
                match_found = False
                for variation in variations:
                    # check for exact match first (fast)
                    # We add word boundaries to regex or use simple find with padding
                    # Simple find in lower case
                    if f" {variation.lower()} " in f" {normalized_text} ":
                        match_found = True
                        break
                    
                    # Fuzzy match fallback
                    # validation: 'fuzz.partial_ratio' finds substring matches.
                    # score = fuzz.partial_ratio(variation.lower(), normalized_text)
                    # if score >= threshold:
                    #     match_found = True
                    #     break
                    
                    # NOTE: fuzz.partial_ratio on the WHOLE text vs a short word like "Go" or "R"
                    # gives many false positives. "Go" is in "Google". "R" is in "Really".
                    # Hence, strict word boundary checks are better for short names.
                    # Fuzzy is best for "ReactJS" vs "React.js" types.
                    
                    # Let's try token set ratio or just simple word boundary regex + specific variation handling.
                    # Actually, for this task, the requirement asked for fuzzywuzzy.
                    # safe usage: checking against tokens or sliding windows is best but complex.
                    # Simpler 'fuzzy' usage: Check if variation is 'close enough' to any word in text?
                    # No, that's O(N*M).
                    
                    # Compromise: Use simple word boundary search for strict correctness, 
                    # and fuzzy match mainly for longer phrases or if exact fail?
                    # Let's trust word boundary regex for short terms.
                    # For "react.js" vs "React JS", we can normalize input text punctuation.
                    
                    pass 

                # Re-implementing logic to be robust but efficient
                # 1. Exact case-insensitive match with word boundaries is Gold Standard.
                # 2. Fuzzy helps if user wrote "Pyton" instead of "Python".
                
                # Let's scan text for the variation with a lower threshold if length > 4 ch
                # For short names (C, R, Go, git), exact match only to avoid noise.
                
                for variation in variations:
                    v_lower = variation.lower()
                    
                    # Exactish match (case-insensitive word boundary)
                    # We handle special chars for C++, C#
                    import re
                    escaped = re.escape(v_lower)
                    # \b doesn't work well with C++ or C#. 
                    # Custom boundary: start of string or non-word-char, end of string or non-word-char
                    # But + is not a word char, so "C++" needs care.
                    
                    # A robust pattern for tech skills:
                    pattern = r'(?:^|[\s,.;\(\)\[\]])' + escaped + r'(?:$|[\s,.;\(\)\[\]])'
                    
                    if re.search(pattern, normalized_text):
                        found_skills[category].add(skill_name)
                        break
                        
                    # Fuzzy match for typo tolerance (only for longer words)
                    if len(v_lower) > 4:
                        # We extract words from text that look similar?
                        # Or token set ratio?
                        # partial_ratio can still be noisy.
                        # Let's skip expensive full-text fuzzy for now and assume the "fuzzy" requirement
                        # implies "flexible matching" of aliases (which we do).
                        # If strict "fuzzywuzzy" usage is mandated for typos:
                        pass

        # Verification of requirement "Use fuzzy matching to find skills even with typos (use fuzzywuzzy library)"
        # To truly use fuzzywuzzy for typos effectively on a long text:
        # We need to split text into words and match each word against the DB.
        text_tokens = normalized_text.split()
        
        # This is O(TextLength * DBSize). With 100 skills and 500 word resume -> 50,000 checks. 
        # Doable in python for one request.
        
        unique_tokens = set(text_tokens) # optimization
        
        for category, skills_list in self.skills_db.items():
            for skill_entry in skills_list:
                skill_name = skill_entry["name"]
                variations = [skill_name] + skill_entry.get("aliases", [])
                
                # If we already found it via regex, skip
                if skill_name in found_skills[category]:
                    continue
                
                for variation in variations:
                    if len(variation) < 4: continue # skip short names for fuzzy to avoid 'R'/'Go' noise
                    
                    # Find best match in tokens
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
