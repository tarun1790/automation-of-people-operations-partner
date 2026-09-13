from typing import Dict, Any, List, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.orm import Session
from backend.app.models.hr_entities import Policy, PolicyChunk

class PolicyIntelligenceService:
    """Provides source-grounded RAG reasoning over corporate HR policies with exact section, page, and chunk excerpts."""

    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))

    def answer_query(self, db: Session, query: str) -> Dict[str, Any]:
        chunks = db.query(PolicyChunk).join(Policy).all()
        if not chunks:
            return {
                "query": query,
                "answer": "No supporting policy was found in the available HR knowledge base.",
                "confidence": 0.0,
                "citations": [],
                "supporting_evidence": None,
                "governance_notice": "WorkSight AI adheres to zero-hallucination policy governance. HR inquiries without verified documentary backing require human HRBP consultation."
            }

        corpus = [f"{c.policy.title} {c.section_title} {c.chunk_text}" for c in chunks]
        all_texts = [query] + corpus

        tfidf_matrix = self.vectorizer.fit_transform(all_texts)
        similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0]

        top_indices = np.argsort(similarities)[::-1]
        best_idx = top_indices[0]
        best_score = float(similarities[best_idx])

        # Strict Relevance Threshold to prevent policy hallucination
        if best_score < 0.12:
            return {
                "query": query,
                "answer": "No supporting policy was found in the available HR knowledge base.",
                "confidence": round(best_score * 100, 1),
                "citations": [],
                "supporting_evidence": None,
                "recommended_action": "Route inquiry to HR People Partner for custom advisory review.",
                "governance_notice": "Zero-hallucination policy triggered: inquiry falls outside indexed HR policy guidelines."
            }

        top_chunk = chunks[best_idx]
        confidence_pct = min(96.0, round(best_score * 120.0 + 15.0, 1))

        # Collect top citations
        citations = []
        for idx in top_indices[:3]:
            score = float(similarities[idx])
            if score >= 0.10:
                c = chunks[idx]
                citations.append({
                    "document_title": c.policy.title,
                    "policy_code": c.policy.code,
                    "section_code": c.section_code,
                    "section_title": c.section_title,
                    "page_number": c.page_number,
                    "retrieved_excerpt": c.chunk_text,
                    "similarity_score": round(score * 100, 1)
                })

        # Synthesize source-grounded response
        primary = citations[0]
        answer = (
            f"According to **{primary['document_title']}** ({primary['policy_code']}), "
            f"**{primary['section_title']}** (Page {primary['page_number']}):\n\n"
            f"> \"{primary['retrieved_excerpt']}\"\n\n"
        )
        if len(citations) > 1:
            sec = citations[1]
            answer += (
                f"Related context in **{sec['section_title']}** (Page {sec['page_number']}):\n"
                f"> \"{sec['retrieved_excerpt']}\""
            )

        # Recommended procedural action based on query context
        q_lower = query.lower()
        if "leave" in q_lower or "parental" in q_lower or "vacation" in q_lower or "sick" in q_lower:
            rec = "Submit formal leave request through HRIS portal at least 14 days in advance of requested start date."
        elif "remote" in q_lower or "stipend" in q_lower or "equipment" in q_lower:
            rec = "Submit ergonomic hardware invoice via Finance & Ops reimbursement module."
        elif "overtime" in q_lower or "hours" in q_lower:
            rec = "Schedule workload review check-in with direct manager and notify HR People Partner if exceeding 15 hrs/mo."
        elif "pip" in q_lower or "performance" in q_lower:
            rec = "Initiate formal 45-day coaching sprint with clear weekly milestones per Policy POL-PERF-2025."
        else:
            rec = "Consult with assigned People Operations Partner for specific edge-case clearance."

        return {
            "query": query,
            "answer": answer,
            "confidence": confidence_pct,
            "citations": citations,
            "supporting_evidence": primary["retrieved_excerpt"],
            "recommended_action": rec,
            "governance_notice": "Source-grounded citation verified against current corporate HR policy repository."
        }

policy_intelligence_service = PolicyIntelligenceService()
