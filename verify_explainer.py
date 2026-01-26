
from app.core.explainer import RankExplainer

def verify_explainer():
    explainer = RankExplainer()
    
    # 1. High Candidate
    high_data = {
        "name": "Jane Top",
        "final_score": 88.5,
        "tfidf_score": 0.82,
        "years_of_experience": 6.5,
        "matched_skills": ["Python", "FastAPI", "Docker", "AWS", "PostgreSQL", "React"],
        "missing_skills": ["Kubernetes"]
    }
    print("--- High Score Explanation ---")
    print(explainer.generate_explanation(high_data))
    print("\n")
    
    # 2. Medium Candidate
    med_data = {
        "name": "Joe Avg",
        "final_score": 65.0,
        "tfidf_score": 0.60,
        "years_of_experience": 2.0,
        "matched_skills": ["Python", "Flask"],
        "missing_skills": ["FastAPI", "Docker", "AWS"]
    }
    print("--- Medium Score Explanation ---")
    print(explainer.generate_explanation(med_data))
    print("\n")
    
    # 3. Low Candidate
    low_data = {
        "name": "Newbie",
        "final_score": 30.0,
        "tfidf_score": 0.20,
        "years_of_experience": 0.0,
        "matched_skills": [],
        "missing_skills": ["Python", "Java", "C++"]
    }
    print("--- Low Score Explanation ---")
    print(explainer.generate_explanation(low_data))
    print("\n")

if __name__ == "__main__":
    verify_explainer()
