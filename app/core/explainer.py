
from typing import Dict, Any, List

class RankExplainer:
    def generate_explanation(self, candidate_data: Dict[str, Any]) -> str:
        """
        Generates a human-readable explanation for a candidate's score.
        """
        name = candidate_data.get("name", "Candidate")
        final_score = candidate_data.get("final_score", 0.0)
        tfidf_score = candidate_data.get("tfidf_score", 0.0)
        exp_years = candidate_data.get("years_of_experience", 0.0)
        
        # Determine Category
        if final_score >= 80:
            category = "High"
            verdict = "Strong Match"
        elif final_score >= 50:
            category = "Medium"
            verdict = "Potential Match"
        else:
            category = "Low"
            verdict = "Weak Match"
            
        # Skill Breakdown
        matched_skills = candidate_data.get("matched_skills", [])
        missing_skills = candidate_data.get("missing_skills", [])
        
        # Construct Explanation
        lines = []
        lines.append(f"{name} ranks as a **{verdict}** with a score of {round(final_score, 1)}/100.")
        
        # Reasons
        if category == "High":
             lines.append(f"✓ Strong skill alignment ({len(matched_skills)} matches: {', '.join(matched_skills[:5])}...)")
        elif category == "Medium":
             lines.append(f"✓ Good skill overlap ({len(matched_skills)} matches)")
        else:
             lines.append(f"✗ Limited skill match ({len(matched_skills)} matches)")
             
        # Experience
        lines.append(f"✓ {exp_years} years of relevant experience") # Or logic to say 'Limited experience' if 0
        
        # Content Similarity
        sim_pct = round(tfidf_score * 100)
        lines.append(f"✓ {sim_pct}% content similarity with Job Description")
        
        # Gaps
        if missing_skills:
            lines.append(f"⚠ Missing Skills: {', '.join(missing_skills[:5])}")
            if len(missing_skills) > 5:
                lines[-1] += f" (+{len(missing_skills)-5} more)"
                
        # Bonus (Extra skills if available in data, usually not passed to Ranker but could be)
        # Assuming Ranker logic passes 'extra_skills' if needed. 
        # Since input spec for explainer mentioned 'candidate_data' from ranker, and ranker didn't keep 'extra_skills' in 'rank_candidates' return dict... 
        # I'll stick to what I have.
        
        return "\n".join(lines)
