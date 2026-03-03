"""
Reviewer Recommendation Service

Uses NLP-based similarity matching to recommend reviewers for papers based on:
1. Profile matching: Reviewer specialization vs paper keywords/research area/abstract
2. History matching: Papers previously reviewed vs current paper content

Uses TF-IDF vectorization with cosine similarity for text matching.
"""

import logging
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from app.db.models import User, Paper, ReviewSubmission, OnlineReview, UserRole

logger = logging.getLogger(__name__)


class RecommendationService:
    """Service for computing reviewer recommendations based on paper content."""
    
    # Weight configuration for combining scores
    PROFILE_WEIGHT = 0.5  # Weight for profile/specialization match
    HISTORY_WEIGHT = 0.5  # Weight for review history match
    
    # Minimum score threshold to be considered "recommended"
    MIN_RECOMMENDATION_SCORE = 0.15
    
    # Maximum number of reviewers to mark as recommended
    MAX_RECOMMENDED = 5
    
    def __init__(self, db: Session):
        self.db = db
        self._vectorizer = None
        self._paper_cache = {}
    
    def _get_vectorizer(self) -> TfidfVectorizer:
        """Get or create TF-IDF vectorizer instance."""
        if self._vectorizer is None:
            self._vectorizer = TfidfVectorizer(
                lowercase=True,
                stop_words='english',
                ngram_range=(1, 2),  # Unigrams and bigrams
                max_features=5000,
                min_df=1,
                max_df=0.95
            )
        return self._vectorizer
    
    def _combine_paper_text(self, paper: Paper) -> str:
        """Combine paper fields into a single searchable text."""
        parts = []
        
        if paper.keyword:
            # Keywords are most important - add multiple times for weight
            parts.append(paper.keyword)
            parts.append(paper.keyword)
        
        if paper.research_area:
            parts.append(paper.research_area)
            parts.append(paper.research_area)
        
        if paper.abstract:
            parts.append(paper.abstract)
        
        if paper.title:
            parts.append(paper.title)
        
        return ' '.join(parts).lower().strip()
    
    def _get_reviewer_review_history(self, reviewer_id: int) -> List[Paper]:
        """Get papers that a reviewer has reviewed."""
        # Get all completed reviews by this reviewer
        reviews = self.db.query(OnlineReview).filter(
            OnlineReview.reviewer_id == str(reviewer_id),
            OnlineReview.review_status.in_(['completed', 'submitted'])
        ).all()
        
        # Get the papers associated with these reviews
        paper_ids = [review.paper_id for review in reviews if review.paper_id]
        
        if not paper_ids:
            return []
        
        papers = self.db.query(Paper).filter(Paper.id.in_(paper_ids)).all()
        return papers
    
    def _build_reviewer_history_text(self, reviewer_id: int) -> str:
        """Build aggregated text from reviewer's review history."""
        papers = self._get_reviewer_review_history(reviewer_id)
        
        if not papers:
            return ""
        
        # Combine keywords and research areas from all reviewed papers
        parts = []
        for paper in papers:
            if paper.keyword:
                parts.append(paper.keyword)
            if paper.research_area:
                parts.append(paper.research_area)
        
        return ' '.join(parts).lower().strip()
    
    def _compute_text_similarity(self, text1: str, text2: str) -> float:
        """Compute similarity between two texts using multiple strategies."""
        if not text1 or not text2:
            return 0.0
        
        # Clean and normalize texts
        text1 = text1.lower().strip()
        text2 = text2.lower().strip()
        
        if not text1 or not text2:
            return 0.0
        
        try:
            # Extract words, removing punctuation
            import re
            words1 = set(re.findall(r'\b[a-z]{3,}\b', text1))
            words2 = set(re.findall(r'\b[a-z]{3,}\b', text2))
            
            if not words1 or not words2:
                return 0.0
            
            # Strategy 1: Exact word matches
            exact_matches = words1 & words2
            
            # Strategy 2: Partial/substring matches (e.g., "engineer" in "engineering")
            partial_matches = set()
            for w1 in words1:
                for w2 in words2:
                    # Check if one word contains the other (min 4 chars to avoid noise)
                    if len(w1) >= 4 and len(w2) >= 4:
                        if w1 in w2 or w2 in w1:
                            partial_matches.add((w1, w2))
                        # Check if they share a common stem (first 5+ chars)
                        elif len(w1) >= 5 and len(w2) >= 5 and w1[:5] == w2[:5]:
                            partial_matches.add((w1, w2))
            
            # Calculate score
            total_matches = len(exact_matches) + (len(partial_matches) * 0.7)
            
            if total_matches > 0:
                # Normalize by the smaller word set
                min_words = min(len(words1), len(words2))
                score = min(total_matches / min_words, 1.0)
                
                # Boost if there are exact matches
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
    
    def _compute_profile_similarity(self, paper: Paper, reviewer: User) -> Tuple[float, str]:
        """
        Compute similarity between paper content and reviewer specialization.
        
        Returns:
            Tuple of (similarity_score, match_reason)
        """
        paper_text = self._combine_paper_text(paper)
        reviewer_spec = (reviewer.specialization or "").lower().strip()
        
        if not paper_text or not reviewer_spec:
            return 0.0, ""
        
        similarity = self._compute_text_similarity(paper_text, reviewer_spec)
        
        # Generate match reason if there's a meaningful match
        match_reason = ""
        if similarity > 0.1:
            import re
            paper_words = set(re.findall(r'\b[a-z]{3,}\b', paper_text))
            spec_words = set(re.findall(r'\b[a-z]{3,}\b', reviewer_spec))
            
            # Find matching words (exact or partial)
            matched_terms = []
            for pw in paper_words:
                for sw in spec_words:
                    if pw == sw or (len(pw) >= 4 and len(sw) >= 4 and (pw in sw or sw in pw)):
                        matched_terms.append(sw.title())
                        break
            
            if matched_terms:
                unique_terms = list(dict.fromkeys(matched_terms))[:3]  # Dedupe, take top 3
                match_reason = f"Expertise in {', '.join(unique_terms)}"
            elif similarity > 0.15:
                match_reason = f"Related expertise: {reviewer_spec.title()[:30]}"
        
        return similarity, match_reason
    
    def _compute_history_similarity(self, paper: Paper, reviewer_id: int) -> Tuple[float, str]:
        """
        Compute similarity between paper content and reviewer's past reviewed papers.
        
        Returns:
            Tuple of (similarity_score, match_reason)
        """
        paper_text = self._combine_paper_text(paper)
        history_text = self._build_reviewer_history_text(reviewer_id)
        
        if not paper_text or not history_text:
            return 0.0, ""
        
        similarity = self._compute_text_similarity(paper_text, history_text)
        
        # Generate match reason if there's a meaningful match
        match_reason = ""
        if similarity > 0.1:
            # Count how many similar papers they've reviewed
            papers_reviewed = len(self._get_reviewer_review_history(reviewer_id))
            if papers_reviewed > 0:
                match_reason = f"Reviewed {papers_reviewed} similar paper{'s' if papers_reviewed > 1 else ''}"
        
        return similarity, match_reason
    
    def compute_recommendation_score(
        self, 
        paper: Paper, 
        reviewer: User
    ) -> Dict:
        """
        Compute overall recommendation score for a reviewer given a paper.
        
        Returns:
            Dict with score, is_recommended flag, and match reasons
        """
        # Compute profile similarity
        profile_score, profile_reason = self._compute_profile_similarity(paper, reviewer)
        
        # Compute history similarity
        history_score, history_reason = self._compute_history_similarity(paper, reviewer.id)
        
        # Combine scores with weights
        combined_score = (
            self.PROFILE_WEIGHT * profile_score + 
            self.HISTORY_WEIGHT * history_score
        )
        
        # Build match reason (prefer profile match, then history)
        match_reason = profile_reason or history_reason
        
        return {
            "score": round(combined_score, 4),
            "profile_score": round(profile_score, 4),
            "history_score": round(history_score, 4),
            "match_reason": match_reason
        }
    
    def get_recommendations(
        self,
        paper: Paper,
        reviewers: List[User]
    ) -> List[Dict]:
        """
        Get recommendation data for all reviewers given a paper.
        
        Args:
            paper: The paper being assigned
            reviewers: List of available reviewers
            
        Returns:
            List of dicts with reviewer ID and recommendation data
        """
        if not paper or not reviewers:
            return []
        
        results = []
        
        for reviewer in reviewers:
            try:
                rec_data = self.compute_recommendation_score(paper, reviewer)
                results.append({
                    "reviewer_id": reviewer.id,
                    **rec_data
                })
            except Exception as e:
                logger.error(f"Error computing recommendation for reviewer {reviewer.id}: {e}")
                results.append({
                    "reviewer_id": reviewer.id,
                    "score": 0.0,
                    "profile_score": 0.0,
                    "history_score": 0.0,
                    "match_reason": ""
                })
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        
        # Mark top reviewers as recommended (if they meet minimum threshold)
        recommended_count = 0
        for result in results:
            if (recommended_count < self.MAX_RECOMMENDED and 
                result["score"] >= self.MIN_RECOMMENDATION_SCORE):
                result["is_recommended"] = True
                recommended_count += 1
            else:
                result["is_recommended"] = False
        
        return results
    
    def enrich_reviewers_with_recommendations(
        self,
        paper_id: int,
        reviewers_list: List[Dict]
    ) -> List[Dict]:
        """
        Enrich a list of reviewer dicts with recommendation data.
        
        Args:
            paper_id: ID of the paper being assigned
            reviewers_list: List of reviewer dicts (from API response)
            
        Returns:
            Enriched list with recommendation fields added
        """
        # Fetch the paper
        paper = self.db.query(Paper).filter(Paper.id == paper_id).first()
        if not paper:
            logger.warning(f"Paper {paper_id} not found for recommendations")
            # Return original list with default recommendation values
            for reviewer in reviewers_list:
                reviewer["is_recommended"] = False
                reviewer["recommendation_score"] = 0.0
                reviewer["match_reason"] = ""
            return reviewers_list
        
        # Get reviewer IDs from the list
        reviewer_ids = [r.get("id") for r in reviewers_list if r.get("id")]
        
        if not reviewer_ids:
            return reviewers_list
        
        # Fetch reviewer objects
        reviewers = self.db.query(User).filter(User.id.in_(reviewer_ids)).all()
        reviewer_map = {r.id: r for r in reviewers}
        
        # Compute recommendations
        recommendations = self.get_recommendations(paper, reviewers)
        rec_map = {r["reviewer_id"]: r for r in recommendations}
        
        # Enrich the original list
        for reviewer_dict in reviewers_list:
            reviewer_id = reviewer_dict.get("id")
            rec_data = rec_map.get(reviewer_id, {})
            
            reviewer_dict["is_recommended"] = rec_data.get("is_recommended", False)
            reviewer_dict["recommendation_score"] = rec_data.get("score", 0.0)
            reviewer_dict["match_reason"] = rec_data.get("match_reason", "")
        
        # Sort by recommendation score (recommended first)
        reviewers_list.sort(
            key=lambda x: (x.get("is_recommended", False), x.get("recommendation_score", 0)),
            reverse=True
        )
        
        return reviewers_list
