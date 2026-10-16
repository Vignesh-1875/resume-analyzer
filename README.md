# Resume Analyzer & Career Guidance System
Streamlit + Hugging Face (Qwen2.5 instruct) + MongoDB Atlas.

## Structure
```
app.py            Streamlit UI (auth, dashboard, 5 pages)
src/config.py     secret loading (env / st.secrets)
src/db.py         MongoDB Atlas client, indexes, history
src/auth.py       bcrypt registration/login
src/parser.py     PDF text + skills/education/experience/projects extraction
src/llm.py        HF model loader, chat generation, JSON helper
src/analyzer.py   LLM resume feedback and skill gaps
src/matcher.py    JD match score (60% skill overlap + 40% embeddings)
src/interview.py  technical/HR questions, sample answers, answer grading
tests/            pytest suite
COLAB.md          Colab smoke test for the pretrained model
```

## Setup
1. `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
2. MongoDB Atlas: create a free cluster, a DB user, add your IP to Network Access, copy the connection string.
3. `cp .env.example .env` and fill in `MONGODB_URI` (optional `HF_MODEL`, `HF_TOKEN` for gated models like Gemma).
   For Streamlit, you can use `.streamlit/secrets.toml` instead. Both files are git-ignored.
4. `streamlit run app.py`

Model choice: `Qwen/Qwen2.5-1.5B-Instruct` (CPU/T4 friendly), `Qwen/Qwen2.5-7B-Instruct` or `google/gemma-2-9b-it` (needs ~16GB+ GPU or 4-bit).

## Testing
- Unit: `pytest -q` (parser/matcher run without GPU or DB).
- Manual: register, login with wrong and right passwords, upload a text PDF and a scanned PDF, run a JD match, generate and grade interview questions, and check the `users` (hashed password only) and `analyses` collections in Atlas.

## Deployment
- **Streamlit Community Cloud**: push to GitHub, add `MONGODB_URI`, `HF_MODEL` in app Secrets. The free tier lacks a GPU, so use a small model or a hosted endpoint.
- **Docker/GPU VM**: `FROM python:3.11-slim`, install requirements, `CMD streamlit run app.py --server.port 8501`; pass secrets as env vars, put behind HTTPS (Nginx/Caddy), and allowlist the server IP in Atlas.
- Hugging Face Spaces (GPU) also works with the same secrets.

## Security notes
bcrypt hashes (cost 12), unique email index, generic login errors, TLS to Atlas, no secrets in code, 5 MB upload cap.
Before production add login rate limiting and session expiry.

## Optional: LoRA/QLoRA
Collect (resume, ideal feedback) pairs, load the model in 4-bit (`bitsandbytes`), attach a `peft` LoRA adapter (r=16, target q/k/v/o proj), train with `trl.SFTTrainer` on Colab, then point `HF_MODEL` at the merged or adapter model.
