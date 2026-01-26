
import logging
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Ranker:
    def __init__(self, weights: Dict[str, float] = None):
        """
        Initializes the Ranker with custom weights.
        Default Weights:
        - TF-IDF Similarity: 40%
        - Skill Match: 40%
        - Experience: 20%
        """
        if weights is None:
            self.weights = {
                "tfidf": 0.4,
                "skills": 0.4,
                "experience": 0.2
            }
        else:
            self.weights = weights

    def rank_candidates(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Ranks a list of candidates based on their aggregated scores.
        
        Args:
            candidates (List[Dict]): List of candidate dictionaries containing:
                - name (str)
                - tfidf_score (float): 0.0 to 1.0
                - skill_match_percentage (float): 0.0 to 100.0
                - years_of_experience (float): e.g., 5.5
                
        Returns:
            List[Dict]: Sorted list of candidates with 'final_score', 'rank', and 'explanation'.
        """
        ranked_list = []
        
        for candidate in candidates:
            # 1. Normalize Scores to 0-100 scale
            
            # TF-IDF: 0.65 -> 65.0
            norm_tfidf = candidate.get("tfidf_score", 0.0) * 100.0
            
            # Skills: Already 0-100
            norm_skills = candidate.get("skill_match_percentage", 0.0)
            
            # Experience: Cap at 10 years -> 100 points. (Linear scaling)
            # 5 years -> 50 points.
            exp_years = candidate.get("years_of_experience", 0.0)
            norm_exp = min(exp_years, 10.0) * 10.0
            
            # 2. Calculate Weighted Final Score
            final_score = (
                (norm_tfidf * self.weights["tfidf"]) +
                (norm_skills * self.weights["skills"]) +
                (norm_exp * self.weights["experience"])
            )
            
            # 3. Create Explanation
            explanation = (
                f"TF-IDF ({int(norm_tfidf)} * {self.weights['tfidf']}) + "
                f"Skills ({int(norm_skills)} * {self.weights['skills']}) + "
                f"Exp ({int(norm_exp)} * {self.weights['experience']})"
            )
            
            # Create enriched candidate object
            # Copy original to avoid mutating input list
            ranked_candidate = candidate.copy()
            ranked_candidate.update({
                "normalized_scores": {
                    "tfidf": round(norm_tfidf, 1),
                    "skills": round(norm_skills, 1),
                    "experience": round(norm_exp, 1)
                },
                "final_score": round(final_score, 2),
                "scoring_explanation": explanation
            })
            
            ranked_list.append(ranked_candidate)
            
        # 4. Sort by Final Score Descending
        ranked_list.sort(key=lambda x: x["final_score"], reverse=True)
        
        # 5. Add Rank
        for i, cand in enumerate(ranked_list):
            cand["rank"] = i + 1
            
        return ranked_list

if __name__ == "__main__":
    ranker = Ranker()
    
    candidates = [
        {
            "name": "Alice (Perfect Match)",
            "tfidf_score": 0.85,          # 85
            "skill_match_percentage": 90.0, # 90
            "years_of_experience": 8.0     # 80
        },
        {
            "name": "Bob (Experienced but Different Stack)",
            "tfidf_score": 0.40,          # 40
            "skill_match_percentage": 50.0, # 50
            "years_of_experience": 15.0    # 100 (capped)
        },
        {
            "name": "Charlie (Fresher, Good Skills)",
            "tfidf_score": 0.60,          # 60
            "skill_match_percentage": 80.0, # 80
            "years_of_experience": 0.5     # 5
        }
    ]
    
    print("--- Ranking Candidates ---")
    ranked = ranker.rank_candidates(candidates)
    
    import json
    print(json.dumps(ranked, indent=2))
