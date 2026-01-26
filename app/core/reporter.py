
from typing import List, Dict, Any

class ComparisonReporter:
    def generate_report(self, candidates: List[Dict[str, Any]], top_n: int = 5) -> Dict[str, Any]:
        """
        Generates a comparison report for the top N candidates.
        Returns a dict with 'markdown_report' and 'visualization_data'.
        """
        # Ensure only top N
        top_candidates = candidates[:top_n]
        if not top_candidates:
            return {"markdown_report": "No candidates to report on.", "visualization_data": {}}

        md_output = []
        md_output.append(f"# Candidate Comparison Report (Top {len(top_candidates)})")
        md_output.append("")
        
        # 1. Summary Section
        md_output.append("## Executive Summary")
        best = top_candidates[0]
        md_output.append(f"**Top Recommendation:** {best.get('name', 'Unknown')}")
        md_output.append(f"- **Score:** {round(best.get('final_score', 0), 1)}/100")
        md_output.append(f"- **Experience:** {best.get('years_of_experience', 0)} years")
        md_output.append("- **Key Strengths:** " + ", ".join(best.get("matched_skills", [])[:5]))
        md_output.append("")

        # 2. Comparison Table (Scores & Exp)
        md_output.append("## Head-to-Head Comparison")
        md_output.append("| Candidate | Score | Experience | Skill Match % |")
        md_output.append("| :--- | :---: | :---: | :---: |")
        for cand in top_candidates:
            name = cand.get("name", "Unknown")
            score = round(cand.get("final_score", 0), 1)
            exp = cand.get("years_of_experience", 0)
            skill_pct = round(cand.get("skill_match_percentage", 0), 1)
            md_output.append(f"| {name} | {score} | {exp} yr | {skill_pct}% |")
        md_output.append("")

        # 3. Skill Matrix (Dynamic Grid)
        # Collect top frequent matched skills across these candidates to form columns
        all_skills = set()
        for c in top_candidates:
            all_skills.update(c.get("matched_skills", []))
        
        # Sort and pick top 10 most relevant (or just all if small) for the matrix
        # For simplicity, let's take the union of all matched skills, sorted alphanumerically, limited to top 8 to fit in table
        sorted_skills = sorted(list(all_skills))[:8] 
        
        if sorted_skills:
            md_output.append("## Skill Matrix")
            header = "| Candidate | " + " | ".join(sorted_skills) + " |"
            md_output.append(header)
            md_output.append("| :--- | " + " | ".join([":---:" for _ in sorted_skills]) + " |")
            
            for cand in top_candidates:
                row = [cand.get("name", "Unknown")]
                c_skills = set(cand.get("matched_skills", []))
                for skill in sorted_skills:
                    row.append("✓" if skill in c_skills else "-")
                md_output.append("| " + " | ".join(row) + " |")
            md_output.append("")
            
        # 4. JSON Data for Visualization
        viz_data = {
            "names": [c.get("name", "Unknown") for c in top_candidates],
            "scores": [round(c.get("final_score", 0), 1) for c in top_candidates],
            "experience": [c.get("years_of_experience", 0) for c in top_candidates],
            "skill_match": [round(c.get("skill_match_percentage", 0), 1) for c in top_candidates]
        }
        
        return {
            "markdown_report": "\n".join(md_output),
            "visualization_data": viz_data
        }
