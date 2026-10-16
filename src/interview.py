from .llm import generate_json


def generate_questions(text: str, kind: str = "technical", n: int = 5, job_desc: str = "") -> list:
    focus = ("technical questions on the candidate's skills and projects" if kind == "technical"
             else "HR / behavioural questions (STAR style) based on their experience")
    prompt = f"""Create {n} {focus}.
Return a JSON list of objects: {{"question": str, "sample_answer": str, "tip": str}}.
Sample answers must reference the candidate's actual background.
{('JOB DESCRIPTION: ' + job_desc[:1500]) if job_desc else ''}
RESUME:
{text[:5000]}"""
    res = generate_json("You are a rigorous interviewer.", prompt, max_new_tokens=1400)
    return res if isinstance(res, list) else res.get("questions", [res])


def evaluate_answer(question: str, answer: str) -> dict:
    prompt = f"""Question: {question}\nCandidate answer: {answer}
Return JSON: "score" (0-10), "feedback" (string), "improved_answer" (string)."""
    return generate_json("You are a strict but fair interview coach.", prompt)
