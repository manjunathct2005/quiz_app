"""
Hugging Face Inference API wrapper used to generate quiz questions.

Uses huggingface_hub.InferenceClient (chat-completions style) against a
configurable instruction-tuned model. The model is asked to return strict
JSON so we can parse it into structured quiz objects.

All settings come directly from config.py -- nothing to configure inside
the app itself.
"""
from __future__ import annotations
import json
import re
from huggingface_hub import InferenceClient

import config


def _get_client() -> InferenceClient:
    if not config.HF_API_TOKEN or "PASTE_YOUR" in config.HF_API_TOKEN:
        raise RuntimeError(
            "HF_API_TOKEN is not set. Open config.py and paste your Hugging Face "
            "token (from https://huggingface.co/settings/tokens)."
        )
    return InferenceClient(token=config.HF_API_TOKEN, provider=config.HF_PROVIDER)


def _build_prompt(stream: str, subject: str, topic: str, difficulty: str, n: int) -> str:
    diff_note = (
        "Mix easy, medium and hard questions roughly evenly."
        if difficulty == "Mixed"
        else f"All questions should be {difficulty.lower()} difficulty."
    )
    return f"""You are an experienced Class 12 ({stream} stream) {subject} teacher setting a
short test for a student on the topic "{topic}".

Create exactly {n} multiple-choice questions (MCQs) strictly from this topic,
suitable for the Indian Class 12 / Intermediate 2nd year board exam level.
{diff_note}

Return ONLY valid JSON (no markdown fences, no commentary, no extra text)
matching exactly this schema:

{{
  "questions": [
    {{
      "question": "string",
      "options": {{"A": "string", "B": "string", "C": "string", "D": "string"}},
      "correct_option": "A" | "B" | "C" | "D",
      "explanation": "1-3 sentence explanation of why the correct option is right",
      "difficulty": "Easy" | "Medium" | "Hard"
    }}
  ]
}}

Rules:
- Exactly {n} items in "questions".
- Each question must have exactly 4 options (A-D), only one correct.
- Explanations must be factually accurate and concise.
- Do not repeat the same question twice.
- Output raw JSON only.
"""


def _extract_json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```(json)?", "", text.strip(), flags=re.IGNORECASE).strip()
    text = re.sub(r"```$", "", text.strip()).strip()
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        raise ValueError("Model did not return JSON.")
    return json.loads(match.group(0))


def generate_quiz(stream: str, subject: str, topic: str, difficulty: str, n: int) -> list[dict]:
    """
    Returns a list of question dicts:
    {question, options: {A,B,C,D}, correct_option, explanation, difficulty}
    """
    prompt = _build_prompt(stream, subject, topic, difficulty, n)
    models_to_try = [config.HF_MODEL, *config.HF_FALLBACK_MODELS]

    last_error = None
    for model in models_to_try:
        try:
            client = _get_client()
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You output strict JSON only. No prose."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=3000,
                temperature=0.7,
            )
            content = resp.choices[0].message.content
            data = _extract_json(content)
            questions = data.get("questions", [])
            if not questions:
                raise ValueError("Empty question list returned.")
            cleaned = []
            for q in questions[:n]:
                opts = q.get("options", {})
                if not all(k in opts for k in ("A", "B", "C", "D")):
                    continue
                if q.get("correct_option") not in ("A", "B", "C", "D"):
                    continue
                cleaned.append({
                    "question": q.get("question", "").strip(),
                    "options": {k: str(opts[k]).strip() for k in ("A", "B", "C", "D")},
                    "correct_option": q["correct_option"],
                    "explanation": q.get("explanation", "").strip(),
                    "difficulty": q.get("difficulty", difficulty),
                })
            if cleaned:
                return cleaned
        except Exception as e:  # noqa: BLE001
            last_error = e
            continue

    raise RuntimeError(f"Could not generate quiz from Hugging Face models. Last error: {last_error}")
