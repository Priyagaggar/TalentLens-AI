
from app.core.reporter import ComparisonReporter

def verify_reporter():
    reporter = ComparisonReporter()
    
    # Mock Candidates
    candidates = [
        {
            "name": "Alice Python",
            "final_score": 92.0,
            "years_of_experience": 8,
            "skill_match_percentage": 95,
            "matched_skills": ["Python", "Django", "AWS", "Docker", "Redis"]
        },
        {
            "name": "Bob Java",
            "final_score": 75.0,
            "years_of_experience": 5,
            "skill_match_percentage": 60,
            "matched_skills": ["Java", "Spring", "AWS"]
        },
        {
            "name": "Clara Junior",
            "final_score": 45.0,
            "years_of_experience": 1,
            "skill_match_percentage": 30,
            "matched_skills": ["Python"]
        }
    ]
    
    report = reporter.generate_report(candidates, top_n=3)
    
    print("--- Visualization Data ---")
    print(report["visualization_data"])
    
    print("\n--- Markdown Report ---")
    print(report["markdown_report"])
    
    # Simple Assertions
    assert "Alice Python" in report["markdown_report"]
    assert "Skill Matrix" in report["markdown_report"]
    assert len(report["visualization_data"]["names"]) == 3

if __name__ == "__main__":
    verify_reporter()
