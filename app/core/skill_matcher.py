
import logging
from typing import List, Dict, Any, Set

from fuzzywuzzy import fuzz

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SkillMatcher:
    def __init__(self, similarity_threshold: int = 70):
        """
        Initializes the SkillMatcher.
        
        Args:
            similarity_threshold (int): Minimum score (0-100) to consider a soft/fuzzy match.
        """
        self.threshold = similarity_threshold

    def match_skills(self, resume_skills: List[str], jd_skills: List[str]) -> Dict[str, Any]:
        """
        Compares resume skills against job description skills.
        
        Weighting:
        - Exact Match: 1.0 points
        - Partial/Similar Match: 0.7 points
        
        Args:
            resume_skills (List[str]): Skills extracted from the resume.
            jd_skills (List[str]): Skills required by the Job Description.
            
        Returns:
            Dict containing match statistics, lists of matched/missing/extra skills, and the weighted score.
        """
        if not jd_skills:
            # Avoid division by zero
            return {
                "match_percentage": 0.0,
                "matched_skills": [],
                "partial_matches": [],
                "missing_skills": [],
                "extra_skills": resume_skills
            }

        # Normalize inputs for easier comparison
        # Use set for faster lookups, but keep case variations for display if needed?
        # Let's simple-normalize to lowercase for checking
        resume_skills_lower = [s.lower() for s in resume_skills]
        jd_skills_lower = [s.lower() for s in jd_skills]
        
        # Track used resume skills to identify 'extra' ones later
        used_resume_indices = set()
        
        matched_skills = []
        partial_matches = []
        missing_skills = []
        
        total_score = 0.0
        
        for jd_skill in jd_skills:
            jd_skill_norm = jd_skill.lower()
            
            # 1. Exact Match
            if jd_skill_norm in resume_skills_lower:
                matched_skills.append(jd_skill)
                # Find index to mark as used
                idx = resume_skills_lower.index(jd_skill_norm)
                used_resume_indices.add(idx)
                total_score += 1.0
                continue
            
            # 2. Fuzzy Match (Partial)
            # Check against all unused resume skills? Or all resume skills?
            # Usually better to check all, but prioritize exact.
            # We iterate to find the best match
            best_match_score = 0
            best_match_idx = -1
            best_match_name = ""
            
            for idx, res_skill in enumerate(resume_skills):
                # Calculate ratio
                score = fuzz.ratio(jd_skill_norm, res_skill.lower())
                if score > best_match_score:
                    best_match_score = score
                    best_match_idx = idx
                    best_match_name = res_skill

            if best_match_score >= self.threshold:
                partial_matches.append({
                    "jd_skill": jd_skill,
                    "resume_skill": best_match_name,
                    "score": best_match_score
                })
                used_resume_indices.add(best_match_idx)
                total_score += 0.7  # Partial weight
            else:
                missing_skills.append(jd_skill)

        # Calculate Percentage
        # Max score possible is len(jd_skills) * 1.0
        # Percentage = (total_score / len(jd_skills)) * 100
        match_percentage = (total_score / len(jd_skills)) * 100.0
        
        # Identify Extra Skills
        extra_skills = [
            resume_skills[i] for i in range(len(resume_skills)) 
            if i not in used_resume_indices
        ]

        return {
            "match_percentage": round(match_percentage, 2),
            "matched_skills": matched_skills,
            "partial_matches": partial_matches,
            "missing_skills": missing_skills,
            "extra_skills": extra_skills
        }

if __name__ == "__main__":
    matcher = SkillMatcher()
    
    jd = ["Python", "React", "AWS", "Docker", "Communication"]
    resume = ["Python", "ReactJS", "aws", "Photoshop", "Teamwork"]
    
    # Expected:
    # Python -> Exact (1.0)
    # React -> ReactJS (Partial ~0.7)
    # AWS -> aws (Exact in pure logical sense, but if we strict lower match -> Exact)
    # Docker -> Missing
    # Communication -> Missing
    # Extra -> Photoshop, Teamwork
    
    print("--- Matching Skills ---")
    result = matcher.match_skills(resume, jd)
    
    import json
    print(json.dumps(result, indent=2))
