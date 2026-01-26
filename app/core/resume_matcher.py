
import logging
from typing import Optional

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResumeMatcher:
    def __init__(self):
        """
        Initializes the TF-IDF Vectorizer with specific parameters optimized for text matching.
        
        TF-IDF (Term Frequency-Inverse Document Frequency) reflects the importance of a word 
        in a document relative to a collection (corpus).
        - max_features=500: Keeps only the top 500 most frequent terms to reduce noise and dimensionality.
        - ngram_range=(1, 2): Considers both single words ("Python") and pairs ("Machine Learning").
        - stop_words='english': Removes common English words (the, is, at) that carry little meaning.
        """
        self.vectorizer = TfidfVectorizer(
            max_features=500,
            ngram_range=(1, 2),
            stop_words='english'
        )
        self.jd_vector = None
        self.is_fitted = False

    def fit(self, jd_text: str):
        """
        Fits the vectorizer on the Job Description (JD).
        This establishes the vocabulary and vector space based on what the job requires.
        
        Args:
            jd_text (str): The raw text of the job description.
        """
        if not jd_text or not jd_text.strip():
            logger.error("Job Description text is empty. Cannot fit vectorizer.")
            self.is_fitted = False
            return

        try:
            # We fit_transform on the JD text. 
            # Note: usually we fit on a corpus, but here we define the 'universe' of terms
            # primarily by the JD, effectively checking intersection with the Resume.
            # Alternately, we could fit on [jd, resume] combined, but fitting on JD ensures
            # the feature space is driven by the JD's requirements.
            
            # Using fit_transform on a list containing the JD
            self.jd_vector = self.vectorizer.fit_transform([jd_text])
            self.is_fitted = True
            logger.info("ResumeMatcher fitted successfully on Job Description.")
        except Exception as e:
            logger.error(f"Error fitting vectorizer: {e}")
            self.is_fitted = False

    def score_resume(self, resume_text: str) -> float:
        """
        Calculates the relevance score of the resume against the fitted Job Description.
        
        Args:
            resume_text (str): The raw text of the resume.
            
        Returns:
            float: A similarity score between 0.0 and 1.0 (cosine similarity).
                   Returns 0.0 if matcher is not fitted or text is empty.
        """
        if not self.is_fitted:
            logger.warning("Matcher must be fitted with a Job Description before scoring.")
            return 0.0

        if not resume_text or not resume_text.strip():
            logger.warning("Empty resume text provided. Score: 0.0")
            return 0.0

        try:
            # Transform resume text using the already fitted vectorizer (JD vocabulary)
            # This ignores words in resume that are NOT in the JD (which is desired behavior usually,
            # we only care about if they have what JD asks for).
            resume_vector = self.vectorizer.transform([resume_text])

            # Calculate Cosine Similarity
            # cosine_similarity returns a matrix [[similarity]]
            similarity_matrix = cosine_similarity(self.jd_vector, resume_vector)
            score = similarity_matrix[0][0]
            
            # Convert to standard python float and round
            return round(float(score), 4)
            
        except Exception as e:
            logger.error(f"Error scoring resume: {e}")
            return 0.0

if __name__ == "__main__":
    # Test execution
    matcher = ResumeMatcher()
    
    sample_jd = """
    We are looking for a Python Developer with experience in FastAPI and Machine Learning.
    Must know Docker, AWS, and Git.
    Preferred skills: React, SQL, and communication skills.
    """
    
    good_resume = """
    Experienced Python Developer.
    I have built APIs using FastAPI and deployed ML models on AWS.
    Proficient in Docker, Git, and SQL.
    Good communication skills.
    """
    
    bad_resume = """
    I am a Graphic Designer.
    I know Photoshop, Illustrator, and Figma.
    I like painting and art.
    """
    
    print("--- Fitting Matcher with JD ---")
    matcher.fit(sample_jd)
    
    print("\n--- Scoring Resumes ---")
    score_good = matcher.score_resume(good_resume)
    print(f"Good Resume Score: {score_good} (Expected High)")
    
    score_bad = matcher.score_resume(bad_resume)
    print(f"Bad Resume Score: {score_bad} (Expected Low)")
    
    score_empty = matcher.score_resume("")
    print(f"Empty Resume Score: {score_empty} (Expected 0.0)")
