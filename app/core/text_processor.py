
import re
import string
import logging
from typing import List, Set, Dict

import nltk
import spacy
from nltk.corpus import stopwords

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextProcessor:
    def __init__(self, spacy_model: str = "en_core_web_sm"):
        """
        Initialize the TextProcessor with NLTK resources and SpaCy model.
        """
        logger.info("Initializing TextProcessor...")
        
        # Ensure NLTK resources are available
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            logger.info("Downloading NLTK stopwords...")
            nltk.download('stopwords')
            
        self.stop_words = set(stopwords.words('english'))
        
        # Load SpaCy model
        try:
            self.nlp = spacy.load(spacy_model)
        except OSError:
            logger.warning(f"SpaCy model '{spacy_model}' not found. Downloading...")
            from spacy.cli import download
            download(spacy_model)
            self.nlp = spacy.load(spacy_model)

        # Define a common skills database (can be expanded)
        self.skills_db = {
            "python", "java", "c++", "c#", "javascript", "typescript", "ruby", "php", "go", "rust",
            "html", "css", "react", "angular", "vue", "node.js", "django", "flask", "fastapi", "spring",
            "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
            "docker", "kubernetes", "aws", "azure", "gcp", "terraform", "jenkins",
            "machine learning", "deep learning", "nlp", "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy",
            "git", "jira", "agile", "scrum"
        }

    def clean_text(self, text: str) -> str:
        """
        Removes special characters and extra whitespace.
        """
        # Remove special characters (keep alphanumeric and basic punctuation)
        # We replace newline characters with spaces to handle multi-line sentences
        text = text.replace('\n', ' ')
        
        # Remove non-ascii characters usually found in resumes (bullet points etc)
        text = re.sub(r'[^\x00-\x7F]+', ' ', text)
        
        # Remove specific special chars but keep some useful for context (like + for C++, # for C#)
        # This regex keeps alphanumeric, whitespace, and @ (email), + (C++), # (C#), . (Node.js)
        # But for general cleaning we often want to be stricter.
        # Let's do a general clean but preserve key tech symbols if possible.
        # Ideally, we clean *after* extraction, but here we are preparing for NLP.
        # For simplicity: Keep alphanumeric and spaces.
        # Note: Skills like "C++" needs special handling if we strip '+'.
        # Strategy: Standardize whitespace first.
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def normalize_text(self, text: str) -> str:
        """
        Converts text to lowercase.
        """
        return text.lower()

    def remove_stopwords(self, text: str) -> str:
        """
        Removes NLTK english stopwords from the text.
        """
        tokens = text.split()
        filtered_tokens = [word for word in tokens if word.lower() not in self.stop_words]
        return " ".join(filtered_tokens)

    def lemmatize_text(self, text: str) -> str:
        """
        Lemmatizes text using SpaCy.
        """
        doc = self.nlp(text)
        return " ".join([token.lemma_ for token in doc])

    def extract_emails(self, text: str) -> List[str]:
        """
        Extracts email addresses using regex.
        """
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        return list(set(re.findall(email_pattern, text)))

    def extract_phone_numbers(self, text: str) -> List[str]:
        """
        Extracts phone numbers using regex.
        Supports various formats:
        - (123) 456-7890
        - 123-456-7890
        - +1 123 456 7890
        """
        # This pattern is quite permissive to catch international formats
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}'
        matches = re.findall(phone_pattern, text)
        # re.findall with groups returns tuples. We need to reconstruct or simply use a non-grouping regex or filter.
        # Let's use a simpler approach that captures the whole string for list return
        # Using finditer is safer to get the whole match
        
        matches = []
        for match in re.finditer(phone_pattern, text):
            matches.append(match.group())
        
        # Filter out short numbers (false positives)
        return [m.strip() for m in matches if len(re.sub(r'\D', '', m)) >= 10]

    def extract_skills(self, text: str) -> List[str]:
        """
        Extracts skills present in the text based on the predefined skills database.
        Includes handling for phrase matching.
        """
        normalized_text = self.normalize_text(text)
        found_skills = set()
        
        # Simple token/phrase matching
        # For more complex matching, SpaCy EntityRuler is better, but this suffices for 'beginner-friendly'
        for skill in self.skills_db:
            # We enforce word boundaries to avoid finding "c" in "cloud" or "go" in "google"
            # escape skill for regex
            escaped_skill = re.escape(skill)
            pattern = r'\b' + escaped_skill + r'\b'
            if re.search(pattern, normalized_text):
                found_skills.add(skill)
        
        return list(found_skills)

    def preprocess(self, text: str) -> Dict[str, any]:
        """
        Runs the full pipeline to clean text and extract metadata.
        Returns a dictionary with cleaned text and extracted entities.
        """
        # 1. Extraction (before heavy cleaning that might remove special chars needed for emails)
        emails = self.extract_emails(text)
        phones = self.extract_phone_numbers(text)
        
        # 2. Cleaning Pipeline
        cleaned = self.clean_text(text)
        normalized = self.normalize_text(cleaned)
        no_stopwords = self.remove_stopwords(normalized)
        lemmatized = self.lemmatize_text(no_stopwords)
        
        # 3. Skill Extraction (on normalized text)
        skills = self.extract_skills(cleaned) # Use cleaned (preserves case if needed? actually extract_skills normalizes)

        return {
            "original_text": text,
            "cleaned_text": cleaned,
            "lemmatized_text": lemmatized,
            "emails": emails,
            "phone_numbers": phones,
            "skills": skills
        }

if __name__ == "__main__":
    # Self-test
    processor = TextProcessor()
    
    sample_text = """
    Jane Doe
    jane.doe@example.com | (555) 123-4567
    
    Experienced Software Engineer with 5 years in Python, FastAPI, and Machine Learning.
    Skilled in Docker, AWS, and Git.
    """
    
    print("--- Processing Sample Text ---")
    results = processor.preprocess(sample_text)
    
    print(f"Emails: {results['emails']}")
    print(f"Phones: {results['phone_numbers']}")
    print(f"Skills: {results['skills']}")
    print(f"Lemmatized: {results['lemmatized_text']}")
