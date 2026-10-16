"""Job-description matching: 60% skill overlap + 40% semantic similarity."""
from .parser import TECH_SKILLS, SOFT_SKILLS, find_skills


def _semantic(a: str, b: str) -> float:
    try:
        from sentence_transformers import SentenceTransformer, util
        m = getattr(_semantic, "model", None) or SentenceTransformer("all-MiniLM-L6-v2")
        _semantic.model = m
        return max(0.0, float(util.cos_sim(m.encode(a[:2000]), m.encode(b[:2000]))))
    except Exception:
        return 0.0


def match_job(resume_text: str, jd_text: str, use_semantic: bool = True) -> dict:
    vocab = TECH_SKILLS + SOFT_SKILLS
    have, need = set(find_skills(resume_text, vocab)), set(find_skills(jd_text, vocab))
    matched, missing = sorted(have & need), sorted(need - have)
    overlap = len(matched) / len(need) if need else 0.0
    sem = _semantic(resume_text, jd_text) if use_semantic else overlap
    score = round(100 * (0.6 * overlap + 0.4 * sem), 1)
    return {"score": score, "matched_skills": matched, "missing_skills": missing,
            "skill_overlap_pct": round(100 * overlap, 1), "semantic_pct": round(100 * sem, 1)}


def match_advice(resume_text: str, jd_text: str, result: dict) -> dict:
    from .llm import generate_json
    prompt = f"""Match score {result['score']}/100. Missing skills: {result['missing_skills']}.
Return JSON: "summary" (string), "how_to_close_gaps" (list), "resume_improvements" (list).
JOB DESCRIPTION:
{jd_text[:3000]}
RESUME:
{resume_text[:3000]}"""
    return generate_json("You are an expert career coach.", prompt)
