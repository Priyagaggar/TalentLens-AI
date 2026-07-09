
import logging
import os
import time
import numpy as np
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Computes cosine similarity between two vectors."""
    a = np.array(vec1)
    b = np.array(vec2)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


def _tfidf_similarity(text1: str, text2: str) -> float:
    """Lightweight TF-IDF cosine similarity fallback (no RAM-heavy models)."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity as sk_cosine
    try:
        vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
        tfidf_matrix = vectorizer.fit_transform([text1, text2])
        score = sk_cosine(tfidf_matrix[0], tfidf_matrix[1])[0][0]
        return float(score)
    except Exception as e:
        logger.warning(f"TF-IDF fallback failed: {e}")
        return 0.0


def _get_hf_embedding(text: str, api_token: str) -> List[float] | None:
    """
    Gets sentence embedding from HuggingFace Inference API.
    Uses all-MiniLM-L6-v2 model (same as local BERT) — no local memory cost.
    Returns None on failure so caller can fall back to TF-IDF.
    """
    import httpx
    API_URL = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"
    headers = {"Authorization": f"Bearer {api_token}"}

    # Truncate text to stay within API limits (512 tokens ≈ 2000 chars)
    text = text[:2000]

    try:
        response = httpx.post(
            API_URL,
            headers=headers,
            json={"inputs": text, "options": {"wait_for_model": True}},
            timeout=30.0,
        )
        if response.status_code == 200:
            result = response.json()
            # API returns a list of floats (the embedding vector)
            if isinstance(result, list) and len(result) > 0:
                return result
        logger.warning(f"HuggingFace API returned status {response.status_code}: {response.text[:200]}")
        return None
    except Exception as e:
        logger.warning(f"HuggingFace API call failed: {e}")
        return None


class AdvancedMatcher:
    """
    Calculates semantic similarity between resumes and job descriptions.

    Strategy (in order of preference):
    1. HuggingFace Inference API (BERT quality, zero local RAM)
    2. TF-IDF cosine similarity fallback (if HF API unavailable/rate-limited)
    """

    def __init__(self):
        self._hf_token: str | None = os.environ.get("HF_API_TOKEN") or os.environ.get("HUGGINGFACE_API_TOKEN")
        if self._hf_token:
            logger.info("AdvancedMatcher: HuggingFace Inference API mode enabled.")
        else:
            logger.warning(
                "AdvancedMatcher: HF_API_TOKEN not set. "
                "Falling back to TF-IDF similarity (still accurate for keyword matching)."
            )

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculates semantic similarity between two texts.
        Returns float between 0.0 and 1.0.
        """
        if self._hf_token:
            emb1 = _get_hf_embedding(text1, self._hf_token)
            emb2 = _get_hf_embedding(text2, self._hf_token)
            if emb1 is not None and emb2 is not None:
                return _cosine_similarity(emb1, emb2)
            logger.warning("HF API failed for calculate_similarity, falling back to TF-IDF.")

        return _tfidf_similarity(text1, text2)

    def batch_compare(self, resumes: List[str], job_description: str) -> List[float]:
        """
        Compares a list of resume texts against a single job description.
        Returns a list of similarity scores.
        """
        if not resumes:
            return []

        if self._hf_token:
            # Get JD embedding once
            jd_embedding = _get_hf_embedding(job_description, self._hf_token)
            if jd_embedding is not None:
                scores = []
                for resume_text in resumes:
                    resume_embedding = _get_hf_embedding(resume_text, self._hf_token)
                    if resume_embedding is not None:
                        scores.append(_cosine_similarity(jd_embedding, resume_embedding))
                    else:
                        # Fall back to TF-IDF for this individual resume
                        scores.append(_tfidf_similarity(resume_text, job_description))
                return scores
            logger.warning("HF API failed for JD embedding in batch_compare, falling back to TF-IDF for all.")

        # Full TF-IDF fallback for all resumes
        return [_tfidf_similarity(r, job_description) for r in resumes]

    def compare_methods(self, resumes: List[Dict[str, Any]], job_description: str) -> List[Dict[str, Any]]:
        """
        Compares resumes against a job description and returns enriched results.
        """
        texts = [r.get("text", "") for r in resumes]
        if not texts:
            return []

        scores = self.batch_compare(texts, job_description)

        results = []
        for i, score in enumerate(scores):
            results.append({
                "id": resumes[i].get("id"),
                "bert_score": score,
            })
        return results
