import re
from typing import Dict, Any, List, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class RecruitmentIntelligenceEngine:
    """Ranks candidates using resumes, job requirements, and skill relevance with bias mitigation."""

    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))

    def _normalize_skill(self, skill: str) -> str:
        return re.sub(r'[^a-zA-Z0-9+#]', '', skill.strip().lower())

    def extract_skills_from_text(self, text: str, skill_universe: List[str]) -> List[str]:
        found = set()
        clean_text = text.lower()
        for skill in skill_universe:
            # Word boundary matching for precision
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, clean_text):
                found.add(skill)
        return sorted(list(found))

    def evaluate_candidate(
        self,
        candidate_data: Dict[str, Any],
        requisition_data: Dict[str, Any],
        anonymize_bias: bool = False
    ) -> Dict[str, Any]:
        req_skills_raw = [s.strip() for s in requisition_data.get("required_skills_csv", "").split(",") if s.strip()]
        pref_skills_raw = [s.strip() for s in requisition_data.get("preferred_skills_csv", "").split(",") if s.strip()]
        min_exp = float(requisition_data.get("min_experience_years", 3.0))

        cand_skills_raw = [s.strip() for s in candidate_data.get("parsed_skills_csv", "").split(",") if s.strip()]
        cand_exp = float(candidate_data.get("years_of_experience", 0.0))
        resume_text = candidate_data.get("resume_text", "")

        # Compute skill overlap
        req_norm = {self._normalize_skill(s): s for s in req_skills_raw}
        cand_norm = {self._normalize_skill(s): s for s in cand_skills_raw}

        matched_skills = [req_norm[k] for k in req_norm if k in cand_norm]
        missing_skills = [req_norm[k] for k in req_norm if k not in cand_norm]

        skill_match_pct = (len(matched_skills) / max(1, len(req_skills_raw))) * 100.0

        # Compute experience alignment
        if cand_exp >= min_exp:
            exp_alignment = min(100.0, 85.0 + (cand_exp - min_exp) * 4.0)
        else:
            exp_alignment = max(20.0, (cand_exp / min_exp) * 80.0)

        # Compute Semantic Text Similarity using TF-IDF
        job_desc = f"{requisition_data.get('title', '')} {requisition_data.get('job_description', '')} {' '.join(req_skills_raw)}"
        cand_desc = f"{candidate_data.get('current_title', '')} {resume_text} {' '.join(cand_skills_raw)}"

        try:
            tfidf_matrix = self.vectorizer.fit_transform([job_desc, cand_desc])
            semantic_score = float(cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]) * 100.0
        except Exception:
            semantic_score = skill_match_pct

        # Composite Score: 50% Skill match, 25% Experience, 25% Semantic depth
        composite = round(0.50 * skill_match_pct + 0.25 * exp_alignment + 0.25 * semantic_score, 1)

        # Recommendation Tier
        if composite >= 82.0 and len(missing_skills) <= 1:
            recommendation = "Strong Hire"
        elif composite >= 65.0:
            recommendation = "Consider"
        else:
            recommendation = "Do Not Hire"

        alias = candidate_data.get("anonymized_alias") or f"Candidate #{candidate_data.get('id', 1):03d}"
        display_name = alias if anonymize_bias else candidate_data.get("full_name", "Anonymous Candidate")

        return {
            "id": candidate_data.get("id"),
            "requisition_id": requisition_data.get("id"),
            "full_name": display_name,
            "anonymized_alias": alias,
            "email": "masked@privacy.internal" if anonymize_bias else candidate_data.get("email"),
            "years_of_experience": cand_exp,
            "current_title": candidate_data.get("current_title"),
            "parsed_skills": cand_skills_raw,
            "skill_match_pct": round(skill_match_pct, 1),
            "experience_alignment_pct": round(exp_alignment, 1),
            "composite_score": composite,
            "recommendation": recommendation,
            "stage": candidate_data.get("stage", "Screening"),
            "key_strengths": matched_skills[:5],
            "skill_gaps": missing_skills,
            "radar_metrics": {
                "skills": round(skill_match_pct, 1),
                "experience": round(exp_alignment, 1),
                "semantic_relevance": round(semantic_score, 1),
                "readiness": min(100.0, round(composite * 1.05, 1))
            }
        }

recruitment_engine = RecruitmentIntelligenceEngine()
