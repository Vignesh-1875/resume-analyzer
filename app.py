import logging

import streamlit as st
from database import save_resume_analysis, get_resume_history
from src import auth, parser, analyzer, matcher, interview, db

st.set_page_config(page_title="Resume Analyzer & Career Guidance", page_icon="📄", layout="wide")

LOGGER = logging.getLogger(__name__)


def apply_theme():
    st.markdown(
        """
        <style>
        :root {
            --ink: #e8eef7;
            --muted: #9aa9bd;
            --panel: #121b2b;
            --panel-soft: #18243a;
            --accent: #64d8cb;
            --accent-strong: #43b9ac;
        }
        .stApp {
            background:
                radial-gradient(circle at 85% 5%, rgba(100, 216, 203, .13), transparent 28rem),
                linear-gradient(135deg, #09111f 0%, #0d1524 55%, #111a2c 100%);
        }
        .block-container { max-width: 1180px; padding-top: 2rem; }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #101a2b 0%, #0b1321 100%);
            border-right: 1px solid rgba(100, 216, 203, .16);
        }
        h1, h2, h3 { letter-spacing: -.03em; }
        .hero {
            padding: 2rem 2.2rem;
            border: 1px solid rgba(100, 216, 203, .22);
            border-radius: 24px;
            background: linear-gradient(135deg, rgba(24, 36, 58, .92), rgba(18, 27, 43, .72));
            box-shadow: 0 20px 60px rgba(0, 0, 0, .22);
            margin-bottom: 1.5rem;
        }
        .eyebrow {
            color: var(--accent);
            font-size: .78rem;
            font-weight: 700;
            letter-spacing: .14em;
            text-transform: uppercase;
        }
        .hero p, .muted { color: var(--muted); }
        div[data-testid="stMetric"] {
            background: var(--panel);
            border: 1px solid rgba(100, 216, 203, .15);
            border-radius: 16px;
            padding: 1rem;
        }
        .stButton > button {
            border-radius: 12px;
            border: 1px solid rgba(100, 216, 203, .35);
            background: linear-gradient(135deg, var(--accent-strong), #398baf);
            color: #07131f;
            font-weight: 700;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def show(obj):
    if isinstance(obj, dict) and "raw" in obj:
        st.write(obj["raw"])
    else:
        st.json(obj)


def login_page():
    apply_theme()
    st.title("📄 Resume Analyzer & Career Guidance")
    t1, t2 = st.tabs(["Login", "Register"])
    with t1:
        with st.form("login"):
            e, p = st.text_input("Email"), st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                user = auth.login(e, p)
                if user:
                    st.session_state.user = user
                    st.rerun()
                st.error("Invalid credentials.")
    with t2:
        with st.form("reg"):
            n, e, p = st.text_input("Name"), st.text_input("Email "), st.text_input("Password ", type="password")
            if st.form_submit_button("Create account"):
                ok, msg = auth.register(n, e, p)
                (st.success if ok else st.error)(msg)


def dashboard():
    apply_theme()
    user = st.session_state.user
    st.sidebar.write(f"👋 {user['name']}")
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()
    page = st.sidebar.radio("Navigate", ["Resume Analysis", "Job Match", "Career Guidance",
                                         "Interview Practice", "History"])

    if page == "Resume Analysis":
        st.markdown(
            """
            <section class="hero">
                <div class="eyebrow">Career intelligence workspace</div>
                <h1>Turn your resume into your next opportunity.</h1>
                <p>Upload a PDF to uncover strengths, close skill gaps, and get practical guidance tailored to your target role.</p>
            </section>
            """,
            unsafe_allow_html=True,
        )
        f = st.file_uploader("Upload resume (PDF, max 5 MB)", type="pdf")
        role = st.text_input("Target role (optional)")
        if f and st.button("Analyze"):
            if f.size > 5 * 1024 * 1024:
                st.error("This file is larger than 5 MB. Please upload a smaller PDF.")
                return
            try:
                text = parser.extract_text(f.getvalue())
            except Exception:
                LOGGER.exception("Resume text extraction failed for %s", f.name)
                st.error("We could not read this PDF. Please try a text-based PDF.")
                return
            if len(text) < 100:
                st.error("Could not extract text (scanned PDF?)."); return
            st.session_state.resume_text, st.session_state.parsed = text, parser.parse_resume(text)
            with st.status("Building your resume insights", expanded=False) as status:
                status.write("Reading resume sections")
                status.write("Generating tailored recommendations")
                try:
                    st.session_state.analysis = analyzer.analyze_resume(
                        text, st.session_state.parsed, role
                    )
                    save_resume_analysis(
                        user_id=user["id"],
                        filename=f.name,
                        analysis=st.session_state.analysis,
                    )
                except Exception:
                    LOGGER.exception("Resume analysis failed for %s", f.name)
                    status.update(label="Analysis could not be completed", state="error")
                    st.error(
                        "The AI service could not analyze this resume right now. "
                        "Check the model configuration and try again."
                    )
                    return
                status.update(label="Resume insights ready", state="complete")
        if "parsed" in st.session_state:
            p = st.session_state.parsed
            c1, c2 = st.columns(2)
            c1.subheader("Technical skills"); c1.write(", ".join(p["technical_skills"]) or "—")
            c2.subheader("Soft skills"); c2.write(", ".join(p["soft_skills"]) or "—")
            with st.expander("Education"): st.text(p["education"] or "Not detected")
            with st.expander("Experience"): st.text(p["experience"] or "Not detected")
            with st.expander("Projects"): st.text(p["projects"] or "Not detected")
            st.subheader("AI feedback"); show(st.session_state.analysis)
        return

    if "resume_text" not in st.session_state:
        st.info("Upload and analyze a resume first."); return
    text = st.session_state.resume_text

    if page == "Job Match":
        jd = st.text_area("Paste job description", height=250)
        if jd and st.button("Match"):
            res = matcher.match_job(text, jd)
            st.metric("Match score", f"{res['score']}%")
            st.progress(min(int(res["score"]), 100))
            st.success("Matching: " + (", ".join(res["matched_skills"]) or "—"))
            st.error("Missing: " + (", ".join(res["missing_skills"]) or "—"))
            with st.spinner("Preparing your gap-closing plan..."):
                res["advice"] = matcher.match_advice(text, jd, res)
            show(res["advice"]); db.save_analysis(user["id"], "job_match", res)

    elif page == "Career Guidance":
        show(st.session_state.get("analysis", {}))

    elif page == "Interview Practice":
        kind = st.selectbox("Type", ["technical", "hr"])
        if st.button("Generate questions"):
            with st.spinner("Creating questions from your experience..."):
                st.session_state.qs = interview.generate_questions(text, kind)
            db.save_analysis(user["id"], "interview", {"kind": kind, "qs": st.session_state.qs})
        for i, q in enumerate(st.session_state.get("qs", [])):
            if not isinstance(q, dict): st.write(q); continue
            st.markdown(f"**Q{i+1}. {q.get('question', q)}**")
            with st.expander("Sample answer & tip"):
                st.write(q.get("sample_answer", "")); st.caption(q.get("tip", ""))
            ans = st.text_area("Your answer", key=f"a{i}")
            if ans and st.button("Evaluate", key=f"e{i}"):
                show(interview.evaluate_answer(q.get("question", ""), ans))

    elif page == "History":
        resume_history = get_resume_history(user["id"])
        if resume_history:
            st.subheader("Resume insight history")
            for d in resume_history:
                created_at = d["created_at"].astimezone().strftime("%Y-%m-%d %H:%M")
                with st.expander(f"{d['filename']} · {created_at}"):
                    show(d["analysis"])
        else:
            st.info("Your completed resume analyses will appear here.")

        st.subheader("Other activity")
        for d in db.list_analyses(user["id"]):
            if d["kind"] == "resume":
                continue
            with st.expander(f"{d['kind']} - {d['created_at']:%Y-%m-%d %H:%M}"):
                st.json(d["payload"], expanded=False)


(dashboard if "user" in st.session_state else login_page)()
