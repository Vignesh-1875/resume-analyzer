from .llm import generate_json

SYSTEM = "You are a senior technical recruiter and career coach. Be specific and constructive."


def analyze_resume(text: str, parsed: dict, target_role: str = "") -> dict:
    prompt = f"""Analyze this resume{f' for the target role: {target_role}' if target_role else ''}.
Detected skills: {parsed['technical_skills'] + parsed['soft_skills']}
Return JSON with keys: "technical_skills" (list), "non_technical_skills" (list),
"strengths" (list), "weaknesses" (list), "feedback" (list of actionable tips),
"missing_skills" (list of skill gaps for the role), "overall_score" (0-100 int),
"career_paths" (list of 3 objects with "role" and "next_steps").

RESUME:
{text[:6000]}"""
    return generate_json(SYSTEM, prompt)
