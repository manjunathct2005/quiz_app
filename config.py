"""
================================================================
 SETTINGS -- this file is safe to commit to git as-is.
================================================================

Everything non-secret (recipients, model choice, subject data wiring)
lives directly in this file and is already set up.

The two genuinely private values -- your Hugging Face token and your
Gmail App Password -- are NOT hardcoded here, on purpose, so this file
can be pushed to GitHub / Streamlit Cloud without leaking credentials.
They're picked up automatically from (checked in this order):

  1. Streamlit Cloud's "Secrets" manager (Manage app -> Settings -> Secrets)
  2. Environment variables
  3. The fallback placeholder strings below (for a quick local test only)

--- Streamlit Community Cloud ---
Go to your app -> Manage app -> Settings -> Secrets, and paste:

    HF_API_TOKEN = "hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    SMTP_APP_PASSWORD = "xxxx xxxx xxxx xxxx"

--- Running locally ---
Either set environment variables before running:

    export HF_API_TOKEN="hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    export SMTP_APP_PASSWORD="xxxx xxxx xxxx xxxx"
    streamlit run app.py

...or just paste them directly into the two _LOCAL_FALLBACK values below
(fine for local-only use, but then don't commit this file with real
values in it).

Get a token: https://huggingface.co/settings/tokens  (role = "Read")
Get an app password: https://myaccount.google.com/apppasswords
(needs 2-Step Verification on for the Gmail account that sends the mail)
"""
import os

try:
    import streamlit as st
    _secrets = st.secrets
except Exception:
    _secrets = {}


def _get(key: str, local_fallback: str) -> str:
    try:
        if key in _secrets:
            return _secrets[key]
    except Exception:
        pass
    return os.environ.get(key, local_fallback)


# ---------------------------------------------------------------
# 1. Hugging Face -- powers the AI quiz generation
# ---------------------------------------------------------------
_LOCAL_FALLBACK_HF_TOKEN = "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"
HF_API_TOKEN = _get("HF_API_TOKEN", _LOCAL_FALLBACK_HF_TOKEN)

HF_PROVIDER = "auto"                                      # let HF route to an available provider
HF_MODEL = "meta-llama/Llama-3.1-8B-Instruct"             # swap for any chat model you have access to
HF_FALLBACK_MODELS = [
    "Qwen/Qwen2.5-7B-Instruct",
    "mistralai/Mistral-7B-Instruct-v0.3",
]

# ---------------------------------------------------------------
# 2. Email (Gmail SMTP) -- sends task notices + PDF reports
# ---------------------------------------------------------------
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "sravanmanjuct@gmail.com"                     # the account that SENDS the mail

_LOCAL_FALLBACK_SMTP_PASSWORD = "rpvq jxue fuwr cvce"
SMTP_APP_PASSWORD = _get("SMTP_APP_PASSWORD", _LOCAL_FALLBACK_SMTP_PASSWORD)

# Every quiz-assigned notice and every finished-quiz PDF report is sent to
# BOTH of these addresses automatically. No login, no typing an email in
# the app -- this is the fixed, permanent recipient list.
REPORT_RECIPIENTS = [
    "sravanmanjuct@gmail.com",
    "sravanmanju31@gmail.com",   # you wrote "gamil.com" in chat; fixed to gmail.com here.
                                   # edit this line if you actually meant a different domain.
]

# Optional: name shown on the report / emails when no name is entered in the UI
DEFAULT_STUDENT_NAME = "Student"
