from src.parser import parse_resume, find_skills
from src.matcher import match_job

RESUME = """Jane Doe jane@x.com +1 555 123 4567
Education
B.Tech Computer Science, 2023
Experience
ML Intern - built NLP pipeline with Python, PyTorch and Docker. Strong communication.
Projects
Resume analyzer using Streamlit and MongoDB
Skills
Python, SQL"""


def test_parse():
    p = parse_resume(RESUME)
    assert p["email"] == "jane@x.com"
    assert "python" in p["technical_skills"] and "communication" in p["soft_skills"]
    assert "B.Tech" in p["education"] and "Streamlit" in p["projects"]


def test_skill_boundaries():
    assert "java" not in find_skills("I know javascript", ["java", "javascript"])


def test_match():
    r = match_job(RESUME, "Need Python, Docker, Kubernetes, AWS", use_semantic=False)
    assert r["matched_skills"] == ["docker", "python"]
    assert "kubernetes" in r["missing_skills"] and 0 < r["score"] < 100
