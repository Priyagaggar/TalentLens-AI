
import logging
import time
from typing import List, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer, util

logger = logging.getLogger(__name__)

class AdvancedMatcher:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AdvancedMatcher, cls).__new__(cls)
            logger.info("Loading BERT model (all-MiniLM-L6-v2)... This may take a moment.")
            start = time.time()
            cls._model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info(f"BERT model loaded in {time.time() - start:.2f}s")
        return cls._instance

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculates semantic similarity between two texts using BERT embeddings.
        Returns float between 0.0 and 1.0.
        """
        embeddings = self._model.encode([text1, text2], convert_to_tensor=True)
        # util.cos_sim returns a tensor, we assume 1st vs 2nd
        score = util.cos_sim(embeddings[0], embeddings[1])
        return float(score[0][0])

    def batch_compare(self, resumes: List[str], job_description: str) -> List[float]:
        """
        Efficiently compares a list of resume texts against a single JD.
        Returns a list of similarity scores.
        """
        if not resumes:
            return []
            
        # Encode JD once
        jd_embedding = self._model.encode(job_description, convert_to_tensor=True)
        
        # Encode Resumes in batch
        resume_embeddings = self._model.encode(resumes, convert_to_tensor=True)
        
        # Calculate cosine similarity against all
        scores = util.cos_sim(jd_embedding, resume_embeddings)[0]
        
        # Convert to list of floats
        return [float(s) for s in scores]

    def compare_methods(self, resumes: List[Dict[str, Any]], job_description: str) -> List[Dict[str, Any]]:
        """
        Runs both BERT and a provided TF-IDF scorer (passed or re-instantiated) 
        to show side-by-side comparison.
        
        Note: This method assumes functional parity with the architecture. 
        For now, it returns just the BERT scores enriched data.
        """
        # Extract texts
        texts = [r.get("text", "") for r in resumes]
        if not texts:
            return []
            
        bert_scores = self.batch_compare(texts, job_description)
        
        results = []
        for i, score in enumerate(bert_scores):
            results.append({
                "id": resumes[i].get("id"),
                "bert_score": score,
                # "tfidf_score" would be calculated elsewhere or passed in
            })
            
        return results
