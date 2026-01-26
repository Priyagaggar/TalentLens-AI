
import pytest
from app.core.ranker import Ranker

@pytest.fixture
def ranker():
    return Ranker()

def test_ranking_score_calculation(ranker):
    # Manually calculating expected score
    # Score = (tfidf * 0.4) + (skills * 0.4) + (exp_normalized * 0.2)
    # tfidf=0.8, skills=0.9, exp=5 (Assume normalized to 0.5 for sake of test or mocked)
    
    # Note: Ranker.rank_candidates takes a list of candidate dicts
    
    candidates = [
        {
            "id": "1",
            "name": "Alice",
            "extracted_text": "text",
            "tfidf_score": 0.8,
            "skill_match_percentage": 90, # 0.9
            "experience_years": 5 # If max_exp is 10, this is 0.5
        }
    ]
    
    # We might need to mock internal normalization if we want precise score checks
    # Or just check relative ranking
    
    ranked = ranker.rank_candidates(candidates)
    
    # Check if 'final_score' is present and reasonable
    assert len(ranked) == 1
    score = ranked[0]['final_score']
    assert 0 <= score <= 100

def test_ranking_order(ranker):
    candidates = [
        {
            "id": "1", 
            "name": "Low", 
            "tfidf_score": 0.1, 
            "skill_match_percentage": 10, 
            "experience_years": 1
        },
        {
            "id": "2", 
            "name": "High", 
            "tfidf_score": 0.9, 
            "skill_match_percentage": 90, 
            "experience_years": 10
        }
    ]
    
    ranked = ranker.rank_candidates(candidates)
    assert ranked[0]['name'] == "High"
    assert ranked[1]['name'] == "Low"
    assert ranked[0]['final_score'] > ranked[1]['final_score']

def test_explanation_generation(ranker):
    cand = {
        "id": "1",
        "name": "Test",
        "tfidf_score": 0.8,
        "skill_match_percentage": 80,
        "experience_years": 5,
        "matched_skills": ["Python"],
        "missing_skills": ["Java"]
    }
    ranked = ranker.rank_candidates([cand])
    explanation = ranked[0]['scoring_explanation']
    
    assert isinstance(explanation, str)
    assert len(explanation) > 0
    # The explanation might contain some key phrases
    # (Ranker delegates to Explainer, so we test if Explainer was called/output present)
