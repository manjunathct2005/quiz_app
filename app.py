import streamlit as st
from pathlib import Path

import config
from modules.subjects_data import STREAMS, SUBJECT_ICON, TOPICS, DIFFICULTIES, QUESTION_COUNTS
from modules.hf_client import generate_quiz
from modules.email_utils import send_task_notification, send_report_email
from modules.pdf_report import build_report_pdf

st.set_page_config(
    page_title="AI Quiz Teacher — Class 12 MPC / BiPC",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_css():
    css_path = Path(__file__).parent / "assets" / "style.css"
    st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)


load_css()

# No login, no email entry -- reports always go to the fixed addresses in config.py
RECIPIENTS = config.REPORT_RECIPIENTS

if "quizzes" not in st.session_state:
    st.session_state.quizzes = {}   # subject -> quiz state dict
if "student_name" not in st.session_state:
    st.session_state.student_name = config.DEFAULT_STUDENT_NAME

# One-time setup nudge if config.py placeholders haven't been filled in
config_incomplete = (
    "PASTE_YOUR" in config.HF_API_TOKEN or "PASTE_YOUR" in config.SMTP_APP_PASSWORD
)
if config_incomplete:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.warning(
        "⚠️ **config.py isn't fully filled in yet.** Open `config.py` and paste your "
        "Hugging Face token and Gmail App Password (see the comments at the top of "
        "that file). Quiz generation and emails won't work until then."
    )
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------------------------------------------
# Sidebar
# ----------------------------------------------------------------------
with st.sidebar:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("#### 📧 Reports go to")
    for r in RECIPIENTS:
        st.write(r)
    st.session_state.student_name = st.text_input(
        "Student name (for the report)", value=st.session_state.student_name
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    stream = st.radio("🎯 Choose your stream", list(STREAMS.keys()), horizontal=True)
    st.caption("MPC → Maths, Physics, Chemistry")
    st.caption("BiPC → Botany, Zoology, Physics, Chemistry")
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------------------------------------------
# Header
# ----------------------------------------------------------------------
st.markdown('<div class="hero-title">🎓 AI Quiz Teacher</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-sub">Class 12 · Intermediate 2nd Year — pick a subject tab, choose a topic, '
    'and the AI teacher will set (and grade) your test.</div>',
    unsafe_allow_html=True,
)

subjects = STREAMS[stream]
tabs = st.tabs([f"{SUBJECT_ICON.get(s, '📘')} {s}" for s in subjects])

# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------

def reset_subject(subject: str):
    st.session_state.quizzes.pop(subject, None)


def render_setup(subject: str):
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(f"##### Set up a test — {subject}")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        topic = st.selectbox("Topic / Chapter", TOPICS.get(subject, []), key=f"topic_{subject}")
    with col2:
        difficulty = st.selectbox("Difficulty", DIFFICULTIES, key=f"diff_{subject}")
    with col3:
        n_q = st.selectbox("No. of questions", QUESTION_COUNTS, index=1, key=f"n_{subject}")

    if st.button("🚀 Generate & Start Quiz", key=f"start_{subject}", use_container_width=True):
        with st.spinner("Your AI teacher is preparing the test..."):
            try:
                questions = generate_quiz(stream, subject, topic, difficulty, n_q)
            except Exception as e:  # noqa: BLE001
                st.error(f"Couldn't generate the quiz: {e}")
                st.stop()

            st.session_state.quizzes[subject] = {
                "topic": topic,
                "difficulty": difficulty,
                "n": n_q,
                "questions": questions,
                "answers": {},
                "checked": {},
                "completed": False,
                "notified": False,
                "report_sent": False,
            }

        try:
            send_task_notification(
                student_name=st.session_state.student_name,
                stream=stream, subject=subject, topic=topic,
                difficulty=difficulty, n_questions=n_q,
            )
            st.session_state.quizzes[subject]["notified"] = True
        except Exception as e:  # noqa: BLE001
            st.warning(f"Quiz generated, but the assignment email couldn't be sent: {e}")

        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def render_quiz(subject: str, quiz: dict):
    total = len(quiz["questions"])
    answered = len(quiz["checked"])
    st.markdown(
        f'<span class="pill">{quiz["topic"]}</span>'
        f'<span class="pill">{quiz["difficulty"]}</span>'
        f'<span class="pill">{total} Questions</span>',
        unsafe_allow_html=True,
    )
    if quiz.get("notified"):
        st.caption(f"✅ Assignment email sent to {', '.join(RECIPIENTS)}")
    st.progress(answered / total if total else 0, text=f"{answered}/{total} answered")

    for i, q in enumerate(quiz["questions"]):
        checked = i in quiz["checked"]
        user_choice = quiz["answers"].get(i)
        is_correct = checked and user_choice == q["correct_option"]
        card_class = "question-card"
        if checked:
            card_class += " correct" if is_correct else " incorrect"

        st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
        st.markdown(f"**Q{i+1}. {q['question']}**  \n*{q.get('difficulty','')}*")

        option_labels = [f"{k}) {v}" for k, v in q["options"].items()]
        option_keys = list(q["options"].keys())
        default_idx = option_keys.index(user_choice) if user_choice in option_keys else 0

        choice_label = st.radio(
            "Choose an answer",
            option_labels,
            index=default_idx if user_choice else None,
            key=f"radio_{subject}_{i}",
            label_visibility="collapsed",
            disabled=checked,
        )
        if choice_label:
            chosen_key = choice_label.split(")")[0]
            quiz["answers"][i] = chosen_key

        c1, c2 = st.columns([1, 4])
        with c1:
            if not checked:
                if st.button("Check answer", key=f"check_{subject}_{i}", disabled=(i not in quiz["answers"])):
                    quiz["checked"][i] = True
                    st.rerun()
        with c2:
            if checked:
                if is_correct:
                    st.success(f"✅ Correct! Answer: {q['correct_option']}) {q['options'][q['correct_option']]}")
                else:
                    st.error(
                        f"❌ Incorrect. Your answer: {user_choice}) {q['options'].get(user_choice,'—')}  \n"
                        f"Correct answer: {q['correct_option']}) {q['options'][q['correct_option']]}"
                    )
                if q.get("explanation"):
                    st.info(f"💡 {q['explanation']}")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        can_finish = len(quiz["checked"]) == total and total > 0
        if st.button("🏁 Finish & Email Report", key=f"finish_{subject}", disabled=not can_finish, use_container_width=True):
            score = sum(1 for i, q in enumerate(quiz["questions"]) if quiz["answers"].get(i) == q["correct_option"])
            pdf_bytes = build_report_pdf(
                student_name=st.session_state.student_name,
                student_email=", ".join(RECIPIENTS),
                stream=stream, subject=subject, topic=quiz["topic"], difficulty=quiz["difficulty"],
                questions=quiz["questions"], answers=quiz["answers"],
            )
            quiz["score"] = score
            quiz["pdf_bytes"] = pdf_bytes
            quiz["completed"] = True
            try:
                send_report_email(
                    student_name=st.session_state.student_name,
                    subject=subject, topic=quiz["topic"], score=score, total=total,
                    pdf_bytes=pdf_bytes, pdf_filename=f"{subject}_{quiz['topic']}_report.pdf".replace(" ", "_"),
                )
                quiz["report_sent"] = True
            except Exception as e:  # noqa: BLE001
                st.warning(f"Report ready, but the email couldn't be sent: {e}")
            st.rerun()
        if not can_finish:
            st.caption("Check every question's answer to unlock the finish button.")
    with col_b:
        if st.button("🔄 Restart this subject", key=f"restart_{subject}", use_container_width=True):
            reset_subject(subject)
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def render_completed(subject: str, quiz: dict):
    total = len(quiz["questions"])
    score = quiz.get("score", 0)
    pct = round((score / total) * 100, 1) if total else 0

    st.markdown('<div class="glass-card score-hero">', unsafe_allow_html=True)
    st.markdown(f'<div class="score-num">{score} / {total}</div>', unsafe_allow_html=True)
    st.markdown(f"**{pct}% — {subject} · {quiz['topic']}**")
    if quiz.get("report_sent"):
        st.caption(f"📧 Full PDF report emailed to {', '.join(RECIPIENTS)}")
    else:
        st.caption("⚠️ Report email was not sent — you can still download it below.")
    st.download_button(
        "⬇️ Download PDF report",
        data=quiz["pdf_bytes"],
        file_name=f"{subject}_{quiz['topic']}_report.pdf".replace(" ", "_"),
        mime="application/pdf",
        use_container_width=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    with st.expander("📋 Review all questions & explanations"):
        for i, q in enumerate(quiz["questions"]):
            user_choice = quiz["answers"].get(i)
            correct = user_choice == q["correct_option"]
            st.markdown(f"**Q{i+1}. {q['question']}**")
            st.write(f"{'✅' if correct else '❌'} Your answer: {user_choice} — Correct: {q['correct_option']}")
            st.caption(q.get("explanation", ""))
            st.divider()

    if st.button("🔄 Take another test in this subject", key=f"again_{subject}"):
        reset_subject(subject)
        st.rerun()


# ----------------------------------------------------------------------
# Render each subject tab
# ----------------------------------------------------------------------
for tab, subject in zip(tabs, subjects):
    with tab:
        quiz = st.session_state.quizzes.get(subject)
        if quiz is None:
            render_setup(subject)
        elif not quiz["completed"]:
            render_quiz(subject, quiz)
        else:
            render_completed(subject, quiz)
