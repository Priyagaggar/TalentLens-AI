
import re
import string
import logging
from typing import List, Set, Dict

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextProcessor:
    def __init__(self):
        """
        Initialize the TextProcessor with NLTK resources only.
        SpaCy has been removed to reduce memory usage on Render free tier (512MB limit).
        Lemmatization is now handled by NLTK's WordNetLemmatizer (lightweight).
        """
        logger.info("Initializing TextProcessor (lightweight NLTK-only mode)...")
        
        # Ensure NLTK resources are available
        for resource in ['corpora/stopwords', 'corpora/wordnet', 'tokenizers/punkt']:
            try:
                nltk.data.find(resource)
            except LookupError:
                name = resource.split('/')[-1]
                logger.info(f"Downloading NLTK resource: {name}...")
                nltk.download(name, quiet=True)
            
        self.stop_words = set(stopwords.words('english'))
        self._lemmatizer = WordNetLemmatizer()

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
        text = text.replace('\n', ' ')
        text = re.sub(r'[^\x00-\x7F]+', ' ', text)
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
        Lemmatizes text using NLTK WordNetLemmatizer (lightweight, no SpaCy required).
        """
        tokens = text.split()
        lemmatized = [self._lemmatizer.lemmatize(token) for token in tokens]
        return " ".join(lemmatized)

    def extract_emails(self, text: str) -> List[str]:
        """
        Extracts email addresses using regex.
        """
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        return list(set(re.findall(email_pattern, text)))

    def extract_phone_numbers(self, text: str) -> List[str]:
        """
        Extracts phone numbers using regex.
        """
        phone_pattern = r'(\+?\d{1,3}[-.\\s]?)?(\(?\d{3}\)?[-.\\s]?)?\d{3}[-.\\s]?\d{4}'
        matches = []
        for match in re.finditer(phone_pattern, text):
            matches.append(match.group())
        return [m.strip() for m in matches if len(re.sub(r'\D', '', m)) >= 10]

    def extract_skills(self, text: str) -> List[str]:
        """
        Extracts skills present in the text based on the predefined skills database.
        """
        normalized_text = self.normalize_text(text)
        found_skills = set()
        for skill in self.skills_db:
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
        emails = self.extract_emails(text)
        phones = self.extract_phone_numbers(text)
        cleaned = self.clean_text(text)
        normalized = self.normalize_text(cleaned)
        no_stopwords = self.remove_stopwords(normalized)
        lemmatized = self.lemmatize_text(no_stopwords)
        skills = self.extract_skills(cleaned)

        return {
            "original_text": text,
            "cleaned_text": cleaned,
            "lemmatized_text": lemmatized,
            "emails": emails,
            "phone_numbers": phones,
            "skills": skills
        }

if __name__ == "__main__":
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
    print(f"Lemmatized (first 100 chars): {results['lemmatized_text'][:100]}")
