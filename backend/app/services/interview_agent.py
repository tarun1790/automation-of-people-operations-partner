import re
from typing import Dict, Any, List, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class InterviewIntelligenceAgent:
    """Generates role-specific questions, evaluates candidate responses with STAR scoring, and builds structured scorecards."""

    QUESTION_BANK = {
        "Engineering": [
            {
                "question": "Describe a scenario where a critical distributed production service experienced a severe latency spike or failure. How did you diagnose the root cause, isolate the issue, and implement a resilient resolution?",
                "category": "System Resiliency & Incident Response",
                "competency": "Distributed Systems & Debugging",
                "criteria": "Expects clear STAR framework: Situation, Task, Action (metrics, tracing, profiling), and quantifiable Result (latency recovery, automated tests, runbooks).",
                "sample_follow_up": "What circuit-breaking or rate-limiting patterns did you introduce to prevent cascading failures in neighboring services?"
            },
            {
                "question": "How do you design a zero-downtime database schema migration for a high-throughput table processing thousands of writes per second?",
                "category": "Data Architecture & Scalability",
                "competency": "Database Reliability & State Management",
                "criteria": "Look for dual-write patterns, backward-compatible column addition, background backfills, and shadow read verification.",
                "sample_follow_up": "How did you verify data consistency between the old and new columns before deprecating the old schema?"
            }
        ],
        "Data & AI": [
            {
                "question": "Walk us through how you optimized a machine learning model or deep learning pipeline (e.g. PyTorch/CUDA) that was bottlenecked by GPU memory or high inference latency.",
                "category": "ML Systems & Performance Optimization",
                "competency": "GPU Acceleration & Model Deployment",
                "criteria": "Look for batch sizing, mixed precision (FP16/BF16), kernel fusion, CUDA streams, quantization, and profiling tools (Nsight/PyTorch Profiler).",
                "sample_follow_up": "How did you balance inference throughput versus numerical precision loss during quantization?"
            }
        ],
        "General": [
            {
                "question": "Tell me about a time when you had a strong disagreement with a technical lead or product manager regarding architecture or timeline trade-offs. How did you navigate this to achieve alignment?",
                "category": "Behavioral & Conflict Resolution",
                "competency": "Collaboration & Stakeholder Management",
                "criteria": "STAR methodology: Focus on objective evidence, empathy, trade-off matrix evaluation, and team-first alignment.",
                "sample_follow_up": "Looking back, what would you have communicated earlier to minimize friction?"
            }
        ]
    }

    def generate_role_questions(self, role_title: str, required_skills: List[str]) -> List[Dict[str, Any]]:
        dept_key = "Data & AI" if any(s.lower() in ["pytorch", "machine learning", "cuda", "llm"] for s in required_skills) else "Engineering" if any(s.lower() in ["kubernetes", "aws", "go", "python", "backend"] for s in required_skills) else "General"

        questions = list(self.QUESTION_BANK.get(dept_key, self.QUESTION_BANK["General"]))
        # Add dynamic skill-based question
        if required_skills:
            top_skill = required_skills[0]
            questions.append({
                "question": f"In your experience with {top_skill}, what is the most complex architecture challenge you tackled, and what key trade-offs did you evaluate?",
                "category": f"Deep Technical Competency: {top_skill}",
                "competency": f"{top_skill} Mastery",
                "criteria": f"Deep practical knowledge of {top_skill} edge cases, performance limits, and integration patterns.",
                "sample_follow_up": f"What monitoring and observability metrics did you establish specifically for {top_skill}?"
            })
        return questions

    def evaluate_response(self, role_title: str, question: str, criteria: str, candidate_answer: str) -> Dict[str, Any]:
        ans = candidate_answer.strip()
        word_count = len(ans.split())

        if word_count < 15:
            return {
                "overall_score": 35.0,
                "technical_correctness_score": 30.0,
                "relevance_score": 40.0,
                "depth_score": 25.0,
                "star_structure_score": 30.0,
                "communication_score": 45.0,
                "strengths": ["Direct response"],
                "missing_aspects": ["Lacks concrete STAR structure", "Missing technical metrics and depth", "No mention of actions or outcomes"],
                "signal": "Do Not Hire",
                "suggested_follow_up": "Can you provide a specific, real-world example from your past work detailing the exact actions you personally took?",
                "evaluator_summary": "Response was too brief and lacked the technical substance required for this level."
            }

        # STAR detection heuristics
        ans_lower = ans.lower()
        has_situation = any(w in ans_lower for w in ["situation", "when i was", "at my previous", "in my project", "we had a", "there was a"])
        has_task = any(w in ans_lower for w in ["task", "my goal", "responsible for", "objective", "needed to"])
        has_action = any(w in ans_lower for w in ["action", "i implemented", "i configured", "i deployed", "i designed", "i investigated", "i wrote"])
        has_result = any(w in ans_lower for w in ["result", "reduced", "improved", "saved", "increased", "latency dropped", "outcome", "successfully"])

        star_count = sum([has_situation, has_task, has_action, has_result])
        star_score = round(min(100.0, star_count * 22.0 + 12.0), 1)

        # Technical keyword density and depth
        tech_terms = ["latency", "kubernetes", "database", "pipeline", "cache", "throughput", "metrics", "replica",
                      "error", "partition", "asynchronous", "architecture", "scale", "cpu", "memory", "cuda", "pytorch",
                      "terraform", "trade-off", "consistency", "rollback", "prometheus", "profiling"]
        matched_terms = [t for t in tech_terms if t in ans_lower]
        tech_score = round(min(100.0, len(matched_terms) * 12.0 + 35.0), 1)

        # Relevance via vector cosine similarity
        vectorizer = TfidfVectorizer(stop_words='english')
        try:
            mat = vectorizer.fit_transform([question + " " + criteria, ans])
            rel_score = round(float(cosine_similarity(mat[0:1], mat[1:2])[0][0]) * 100.0 + 20.0, 1)
            rel_score = min(98.0, max(40.0, rel_score))
        except Exception:
            rel_score = 75.0

        depth_score = round(min(100.0, min(word_count, 180) / 180.0 * 60.0 + (len(matched_terms) * 6.0)), 1)
        comm_score = round(min(96.0, 70.0 + (15.0 if star_count >= 3 else 0.0) + (10.0 if word_count > 60 else 0.0)), 1)

        overall = round(0.30 * tech_score + 0.25 * star_score + 0.20 * rel_score + 0.15 * depth_score + 0.10 * comm_score, 1)

        if overall >= 84.0 and star_count >= 3:
            signal = "Strong Hire"
        elif overall >= 68.0:
            signal = "Hire"
        elif overall >= 55.0:
            signal = "Leaning Hire"
        else:
            signal = "Do Not Hire"

        strengths = []
        if star_count >= 3:
            strengths.append("Structured narrative adhering closely to the STAR methodology.")
        if len(matched_terms) >= 3:
            strengths.append(f"Strong technical vocabulary demonstrating hands-on architectural experience ({', '.join(matched_terms[:3])}).")
        if has_result:
            strengths.append("Clearly highlighted measurable business or technical outcomes.")

        missing = []
        if not has_result:
            missing.append("Quantifiable post-resolution metrics (e.g. latency reduction %, uptime improvement).")
        if not has_action:
            missing.append("Specific personal actions distinct from broader team efforts.")
        if len(matched_terms) < 2:
            missing.append("Deeper technical tooling and architectural mechanisms.")

        return {
            "overall_score": overall,
            "technical_correctness_score": tech_score,
            "relevance_score": rel_score,
            "depth_score": depth_score,
            "star_structure_score": star_score,
            "communication_score": comm_score,
            "strengths": strengths if strengths else ["Engaged presentation"],
            "missing_aspects": missing if missing else ["Minor edge cases"],
            "signal": signal,
            "suggested_follow_up": "How did you monitor performance regressions after your solution reached 100% production traffic?",
            "evaluator_summary": f"Candidate demonstrates {signal.lower()} competency with {overall}% composite evaluation score."
        }

interview_intelligence_agent = InterviewIntelligenceAgent()
