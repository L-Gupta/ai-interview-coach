# Gemini prompt templates for exit interview
EMOTION_PROMPT = """
You are analyzing the emotional tone and expressions of a candidate during an interview.

Tone Data (per question):
{tone_dict}

Expression Data (per question):
{expression_dict}

Your task:
- Summarize the candidate's overall tone and emotional state.
- Summarize their facial expressions and engagement style.
- Use the provided data only, do not invent information.
- Return ONLY a valid JSON object. Do not include any extra text, commentary, or code fences.

Expected JSON format:
{
  "tone_summary": "Calm and confident",
  "expression_summary": "Positive and engaging"
}
"""

VALIDATION_PROMPT = """
You are validating if the candidate's answer matches their resume.

Candidate Answer:
{answer}

Relevant Resume Content:
{chunk}

Your task:
- Compare the answer with the resume content.
- Decide if it is a "Match", "Exaggerated", or "Mismatch".
- Be strict and accurate; base your judgment only on the provided data.
- Return ONLY a valid JSON object. Do not include any extra text, commentary, or code fences.

Expected JSON format:
{ "validation": "Match" }
"""

JOB_FIT_PROMPT = """
You are evaluating a candidate's fit for the role of {role}.

Candidate Answers:
{answers}

Relevant Resume Chunks:
{context}

Your task:
- Assign a job-fit score between 1 and 100 based on alignment between answers and resume.
- Use the provided context; do not infer extra data.
- Return ONLY a valid JSON object with a single key "score".
- Do not include any explanation, commentary, or code fences.

Expected JSON format:
{ "score": 85 }
"""

ACCURACY_PROMPT = """
You are scoring the accuracy of the candidate's answers based on the questions asked.

Questions and Answers:
{qa_pairs}

Your task:
- Assign a score (1-100) to each question based on how accurate and relevant the answer is.
- Use question keys q1, q2, q3... matching the order provided.
- Return ONLY a valid JSON object with integer scores.
- Do not include any explanation, commentary, or code fences.

Expected JSON format:
{
  "q1": 85,
  "q2": 70,
  "q3": 90
}
"""