"""
Journal Recommendation Service for Authors

Uses NLP-based similarity matching to recommend journals for papers based on:
1. Keyword matching: Author keywords vs Journal scope/aim
2. Abstract matching: Paper abstract vs Journal description/scope

Uses TF-IDF vectorization with cosine similarity for text matching.
Tuned for high accuracy with strict thresholds.
"""

import logging
import re
from typing import List, Dict, Tuple
from sqlalchemy.orm import Session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.db.models import Journal, JournalDetails

logger = logging.getLogger(__name__)


class JournalRecommendationService:
    """Service for computing journal recommendations based on paper keywords and abstract."""
    
    # Weight configuration - keywords are more important for accuracy
    KEYWORD_WEIGHT = 0.6  # Weight for keyword match
    ABSTRACT_WEIGHT = 0.4  # Weight for abstract match
    
    # Higher threshold for accuracy (only recommend when confident)
    MIN_RECOMMENDATION_SCORE = 0.25
    
    # Maximum recommendations to return
    MAX_RECOMMENDATIONS = 3
    
    # Bonus for exact keyword matches
    EXACT_MATCH_BONUS = 0.15
    
    def __init__(self, db: Session):
        self.db = db
    
    def _clean_html(self, text: str) -> str:
        """Remove HTML tags from text."""
        if not text:
            return ""
        # Remove HTML tags
        clean = re.sub(r'<[^>]+>', '', text)
        # Replace multiple whitespace with single space
        clean = re.sub(r'\s+', ' ', clean)
        return clean.strip()
    
    def _extract_words(self, text: str) -> set:
        """Extract meaningful words from text (3+ chars)."""
        if not text:
            return set()
        text = text.lower()
        return set(re.findall(r'\b[a-z]{3,}\b', text))
    
    def _build_journal_text(self, journal: Journal, details: JournalDetails = None) -> str:
        """Combine journal fields into searchable text."""
        parts = []
        
        # Journal name and description
        if journal.fld_journal_name:
            parts.append(journal.fld_journal_name)
        
        if journal.description:
            parts.append(self._clean_html(journal.description))
        
        # Journal details if available
        if details:
            if details.scope:
                # Scope is most important - add twice for weight
                parts.append(self._clean_html(details.scope))
                parts.append(self._clean_html(details.scope))
            
            if details.aim_objective:
                parts.append(self._clean_html(details.aim_objective))
            
            if details.about_journal:
                parts.append(self._clean_html(details.about_journal))
        
        return ' '.join(parts).lower().strip()
    
    def _compute_text_similarity(self, text1: str, text2: str) -> float:
        """Compute similarity between two texts using multiple strategies."""
        if not text1 or not text2:
            return 0.0
        
        text1 = text1.lower().strip()
        text2 = text2.lower().strip()
        
        if not text1 or not text2:
            return 0.0
        
        try:
            words1 = self._extract_words(text1)
            words2 = self._extract_words(text2)
            
            if not words1 or not words2:
                return 0.0
            
            # Strategy 1: Exact word matches
            exact_matches = words1 & words2
            
            # Strategy 2: Partial/substring matches
            partial_matches = set()
            for w1 in words1:
                for w2 in words2:
                    if len(w1) >= 4 and len(w2) >= 4:
                        if w1 in w2 or w2 in w1:
                            partial_matches.add((w1, w2))
                        elif len(w1) >= 5 and len(w2) >= 5 and w1[:5] == w2[:5]:
                            partial_matches.add((w1, w2))
            
            # Calculate score
            total_matches = len(exact_matches) + (len(partial_matches) * 0.7)
            
            if total_matches > 0:
                min_words = min(len(words1), len(words2))
                score = min(total_matches / min_words, 1.0)
                
                # Boost for exact matches
                if exact_matches:
                    score = min(score + 0.2, 1.0)
                
                return score
            
            # Strategy 3: TF-IDF for longer texts as fallback
            if len(text1.split()) >= 5 and len(text2.split()) >= 5:
                vectorizer = TfidfVectorizer(
                    lowercase=True,
                    stop_words='english',
                    ngram_range=(1, 2),
                    max_features=1000,
                    min_df=1
                )
                
                tfidf_matrix = vectorizer.fit_transform([text1, text2])
                similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
                
                return float(similarity)
            
            return 0.0
            
        except Exception as e:
            logger.warning(f"Error computing text similarity: {e}")
            return 0.0
    
    def _compute_keyword_match(self, keywords: List[str], journal_text: str) -> Tuple[float, List[str]]:
        """
        Compute how well keywords match the journal content.
        
        Returns:
            Tuple of (score, list of matched keywords)
        """
        if not keywords or not journal_text:
            return 0.0, []
        
        keywords_text = ' '.join(keywords)
        base_score = self._compute_text_similarity(keywords_text, journal_text)
        
        # Check for exact keyword matches (bonus for accuracy)
        journal_words = self._extract_words(journal_text)
        matched_keywords = []
        exact_match_count = 0
        
        for kw in keywords:
            kw_words = self._extract_words(kw)
            for kw_word in kw_words:
                if kw_word in journal_words:
                    exact_match_count += 1
                    matched_keywords.append(kw)
                    break
                # Check partial matches
                for jw in journal_words:
                    if len(kw_word) >= 4 and len(jw) >= 4:
                        if kw_word in jw or jw in kw_word:
                            matched_keywords.append(kw)
                            break
        
        # Apply exact match bonus
        if exact_match_count >= 2:
            base_score = min(base_score + self.EXACT_MATCH_BONUS, 1.0)
        elif exact_match_count >= 1:
            base_score = min(base_score + (self.EXACT_MATCH_BONUS / 2), 1.0)
        
        return base_score, list(set(matched_keywords))
    
    def _generate_match_reason(self, matched_keywords: List[str], keyword_score: float, abstract_score: float) -> str:
        """Generate a human-readable reason for the recommendation."""
        if matched_keywords:
            # Show up to 3 matched keywords
            kw_str = ', '.join(matched_keywords[:3])
            if len(matched_keywords) > 3:
                kw_str += f" +{len(matched_keywords) - 3} more"
            return f"Matches: {kw_str}"
        elif keyword_score > 0.3:
            return "Strong topic alignment"
        elif abstract_score > 0.3:
            return "Related to your research area"
        else:
            return "Relevant scope"
    
    def compute_journal_score(
        self,
        keywords: List[str],
        abstract: str,
        journal: Journal,
        details: JournalDetails = None
    ) -> Dict:
        """
        Compute recommendation score for a journal given keywords and abstract.
        
        Returns:
            Dict with score, is_recommended, and match_reason
        """
        journal_text = self._build_journal_text(journal, details)
        
        if not journal_text:
            return {
                "journal_id": journal.fld_id,
                "journal_name": journal.fld_journal_name,
                "score": 0.0,
                "is_recommended": False,
                "match_reason": ""
            }
        
        # Compute keyword match (weighted more heavily)
        keyword_score, matched_keywords = self._compute_keyword_match(keywords, journal_text)
        
        # Compute abstract match
        abstract_score = 0.0
        if abstract:
            abstract_score = self._compute_text_similarity(abstract, journal_text)
        
        # Combine scores with weights
        final_score = (keyword_score * self.KEYWORD_WEIGHT) + (abstract_score * self.ABSTRACT_WEIGHT)
        
        # Determine if recommended
        is_recommended = final_score >= self.MIN_RECOMMENDATION_SCORE
        
        # Generate reason
        match_reason = ""
        if is_recommended:
            match_reason = self._generate_match_reason(matched_keywords, keyword_score, abstract_score)
        
        return {
            "journal_id": journal.fld_id,
            "journal_name": journal.fld_journal_name,
            "score": round(final_score, 3),
            "is_recommended": is_recommended,
            "match_reason": match_reason
        }
    
    def get_recommendations(
        self,
        keywords: List[str],
        abstract: str = ""
    ) -> List[Dict]:
        """
        Get journal recommendations for given keywords and abstract.
        
        Args:
            keywords: List of keywords from the paper
            abstract: Paper abstract (optional but improves accuracy)
        
        Returns:
            List of recommended journals with scores and reasons
        """
        if not keywords:
            return []
        
        # Get all journals
        journals = self.db.query(Journal).all()
        
        if not journals:
            return []
        
        # Get all journal details
        details_map = {}
        all_details = self.db.query(JournalDetails).all()
        for d in all_details:
            details_map[str(d.journal_id)] = d
        
        # Compute scores for all journals
        scored_journals = []
        for journal in journals:
            details = details_map.get(str(journal.fld_id))
            score_result = self.compute_journal_score(keywords, abstract, journal, details)
            
            if score_result["is_recommended"]:
                scored_journals.append(score_result)
        
        # Sort by score descending
        scored_journals.sort(key=lambda x: x["score"], reverse=True)
        
        # Return top N recommendations
        return scored_journals[:self.MAX_RECOMMENDATIONS]
