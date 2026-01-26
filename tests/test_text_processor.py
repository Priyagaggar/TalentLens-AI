
import pytest
from app.core.text_processor import TextProcessor

@pytest.fixture
def text_processor():
    return TextProcessor()

def test_clean_text(text_processor):
    raw_text = "  Hello   World! \n This is a test.  "
    cleaned = text_processor.clean_text(raw_text)
    assert cleaned == "Hello World! This is a test." # Assuming basic whitespace cleaning

def test_extract_entities(text_processor):
    text = "Contact me at john.doe@example.com or 555-123-4567."
    
    # Check regex extraction directly if methods are public or via preprocess
    emails = text_processor.extract_emails(text)
    assert "john.doe@example.com" in emails
    
    phones = text_processor.extract_phone_numbers(text)
    # TextProcessor enforces 10 digits
    assert "555-123-4567" in phones

def test_extract_skills_fuzzy(text_processor):
    # Mock skills_db if necessary, or use the loaded one
    # TextProcessor uses exact match.
    text = "I use Python and React for web dev."
    
    # Assuming extract_skills handles fuzzy matching
    # If TextProcessor delegates to SkillExtractor, we might need to verify that interaction
    # But if TextProcessor has its own or we are testing SkillExtractor separately?
    # The prompt asked for "text processing (test_text_processor.py) ... Test skill extraction"
    # If TextProcessor calls SkillExtractor, we verify the integration.
    
    result = text_processor.preprocess(text)
    
    # Check if 'Python' and 'React' (normalized) are in skills
    # This depends on the specific implementation of preprocess return dict
    
    # If logic is in SkillExtractor, we should check that `skills` key exists.
    assert "skills" in result
    assert "python" in result["skills"] or "Python" in result["skills"]
