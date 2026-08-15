# 🎓 AI Quiz Teacher — Class 12 MPC / BiPC

A Streamlit portal that acts like an AI teacher for Class 12 (Intermediate
2nd year) MPC (Maths/Physics/Chemistry) and BiPC (Botany/Zoology/Physics/
Chemistry) students. No login screen -- open it and go straight to picking
a subject and topic.

- Pick a stream, then a subject tab, then a topic/chapter, difficulty, and
  number of questions.
- Hugging Face (via `huggingface_hub.InferenceClient`) generates a fresh MCQ
  quiz for that exact topic.
- Starting a quiz automatically emails a "task assigned" note to both fixed
  addresses configured in `config.py` (teacher-style assignment notice).
- Each question is checked instantly -- correct/incorrect, the right answer,
  and a short explanation.
- Finishing the quiz builds a full PDF score report (question-by-question,
  with explanations) and emails it to the same two addresses, plus offers
  it as a direct download.
- Glassmorphic, transparent, gradient UI.

## 1. Install (local)

```bash
cd quiz_app
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Configure the two secrets

`config.py` is safe to commit as-is — every setting except two is already
filled in. Only `HF_API_TOKEN` and `SMTP_APP_PASSWORD` are left out of the
file on purpose, since baking real credentials into a file that gets
pushed to GitHub would leak them. Pick **one** of these three ways to
supply them:

**A) Streamlit Community Cloud (recommended for deployment)**
Go to your deployed app → **Manage app → Settings → Secrets**, and paste:
```toml
HF_API_TOKEN = "hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxx"
SMTP_APP_PASSWORD = "xxxx xxxx xxxx xxxx"
```
This is what caused the `ModuleNotFoundError: config` you may have seen —
that happens if `config.py` itself never got pushed to your repo. Make
sure `config.py` is committed (it no longer contains secrets, so it's
fine to commit) and redeploy.

**B) Environment variables (local or your own server)**
```bash
export HF_API_TOKEN="hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxx"
export SMTP_APP_PASSWORD="xxxx xxxx xxxx xxxx"
streamlit run app.py
```

**C) Local secrets.toml (quick local testing)**
```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# then edit .streamlit/secrets.toml with real values
```

Get a token: https://huggingface.co/settings/tokens (role = "Read")
Get an app password: https://myaccount.google.com/apppasswords (needs
2‑Step Verification on for the Gmail account that sends mail)

> Note: you wrote `sravanmanju31@gamil.com` in the request — that reads
> like a typo of `gmail.com`, so `config.py` has it as
> `sravanmanju31@gmail.com`. Edit `REPORT_RECIPIENTS` in `config.py` if you
> actually meant a different domain.

## 3. Run

```bash
streamlit run app.py
```

No sign-in step. Open the app, pick MPC or BiPC, pick a subject tab, pick a
topic, and start the quiz. If the two secrets aren't set yet, the app shows
a one-line warning banner telling you exactly what's missing.

## Project layout

```
quiz_app/
├── app.py                       # Main Streamlit UI / flow (no login)
├── config.py                    # Settings file — safe to commit
├── modules/
│   ├── hf_client.py             # Hugging Face quiz generation (JSON MCQs)
│   ├── email_utils.py           # Task-assigned + PDF report emails (SMTP)
│   ├── pdf_report.py            # ReportLab PDF score report builder
│   └── subjects_data.py         # MPC/BiPC subjects & topic lists (editable)
├── assets/
│   └── style.css                # Glassmorphic / transparent theme
├── .streamlit/
│   └── secrets.toml.example     # Optional local secrets template
└── requirements.txt
```

## Deploying to Streamlit Community Cloud

1. Push this whole folder to a GitHub repo (`config.py` included — it has
   no secrets in it now).
2. On share.streamlit.io, point a new app at that repo, main file `app.py`.
3. After the first deploy (it'll show the "config isn't filled in" warning
   banner, which is expected), go to **Manage app → Settings → Secrets**
   and paste the two lines from step 2A above.
4. Reboot the app from the same menu — the warning banner disappears once
   both values are picked up.

## Notes / things you may want to tweak

- **Topic lists** in `modules/subjects_data.py` are indicative AP/TS
  Intermediate 2nd-year chapter names -- edit freely to match your exact
  syllabus/textbook.
- **Recipients**: `REPORT_RECIPIENTS` in `config.py` controls who gets the
  assignment notice and the final PDF -- both entries get every email,
  every time, with no prompt in the UI.
- If email sending fails (e.g. wrong app password), the quiz still works --
  you'll see a warning banner and can still download the PDF report
  directly from the app.
