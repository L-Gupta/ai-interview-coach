# Gemini prompt templates for exit interview

EMOTION_PROMPT = """
Analyze the candidate's tone and expressions across questions.

Tone Dictionary:
{tone_dict}

Expression Dictionary:
{expression_dict}

Summarize overall tone and expressions.
Return only JSON in the format:
{{
  "tone_summary": "Calm and confident",
  "expression_summary": "Positive and engaging"
}}
"""

VALIDATION_PROMPT = """
Compare the candidate's answer with their resume information.

Answer:
{answer}

Resume Chunk:
{chunk}

Determine if the answer is a "Match", "Exaggerated", or "Mismatch".
Return only JSON in the format:
{{ "validation": "Match" }}
"""

JOB_FIT_PROMPT = """
You are evaluating a candidate for the role of {role}.

Candidate's Answers:
{answers}

Relevant Resume Chunks:
{context}

Based on this information, provide a job-fit score (1-100) as a JSON object:

{{ "score": 85 }}
Return only the JSON.
"""

ACCURACY_PROMPT = """
Evaluate the accuracy of the candidate's answers based on the questions.

Questions & Answers:
{qa_pairs}

Return ONLY a valid JSON object with question keys (q1, q2...) and integer scores (1-100).
Do not include any explanation, only JSON.

Example output:
{{
  "q1": 85,
  "q2": 70,
  "q3": 90
}}
"""
