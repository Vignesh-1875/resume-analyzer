"""PDF text extraction + rule-based resume parsing."""
import io
import re

TECH_SKILLS = ["python", "java", "c++", "c#", "javascript", "typescript", "sql", "mongodb", "mysql",
    "postgresql", "react", "node.js", "django", "flask", "fastapi", "streamlit", "pandas", "numpy",
    "scikit-learn", "tensorflow", "pytorch", "keras", "machine learning", "deep learning", "nlp",
    "transformers", "hugging face", "llm", "computer vision", "docker", "kubernetes", "aws", "azure",
    "gcp", "git", "linux", "rest api", "tableau", "power bi", "excel", "spark", "hadoop", "html", "css"]
SOFT_SKILLS = ["communication", "leadership", "teamwork", "problem solving", "time management",
    "adaptability", "critical thinking", "collaboration", "creativity", "mentoring", "presentation"]

SECTIONS = {
    "education": r"education|academic",
    "experience": r"experience|employment|internship|work history",
    "projects": r"projects?",
    "skills": r"skills|technologies|tech stack",
}


def extract_text(file_bytes: bytes) -> str:
    from pypdf import PdfReader
    reader = PdfReader(io.BytesIO(file_bytes))
    return "\n".join((p.extract_text() or "") for p in reader.pages).strip()


def find_skills(text: str, vocab) -> list:
    low = text.lower()
    return sorted({s for s in vocab if re.search(rf"(?<![\w+#]){re.escape(s)}(?![\w+#])", low)})


def split_sections(text: str) -> dict:
    out, current = {k: [] for k in SECTIONS}, None
    for line in text.splitlines():
        stripped = line.strip().strip(":").lower()
        hit = next((k for k, pat in SECTIONS.items()
                    if len(stripped) < 40 and re.fullmatch(rf"({pat})", stripped)), None)
        if hit:
            current = hit
        elif current and line.strip():
            out[current].append(line.strip())
    return {k: "\n".join(v) for k, v in out.items()}


def parse_resume(text: str) -> dict:
    email = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text)
    phone = re.search(r"(\+?\d[\d\s().-]{8,}\d)", text)
    sec = split_sections(text)
    return {
        "email": email.group(0) if email else None,
        "phone": phone.group(0).strip() if phone else None,
        "technical_skills": find_skills(text, TECH_SKILLS),
        "soft_skills": find_skills(text, SOFT_SKILLS),
        "education": sec["education"],
        "experience": sec["experience"],
        "projects": sec["projects"],
        "raw_skills_section": sec["skills"],
    }
