# Gemini prompt templates for exit interview
TONE_PROMPT = """
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

EXPRESSION_PROMPT = """
You are an AI interviewer evaluating a candidate's facial behavior during a virtual interview.

Here is the extracted data:
- Dominant Emotions: {dominant_emotions}
- Average Eye Contact: {avg_eye_contact}%
- Total Distractions Detected: {total_distractions}
- Total Frames with No Face Detected: {total_face_absence}
- Was Another Person Detected: {multi_person_flag}

Your task:
- Write a short 2–3 line summary of the candidate's **facial expression behavior**
- Focus on their engagement, focus level, and any distraction cues
- Do NOT mention tone or audio-based behavior

Return ONLY a valid JSON object:
{
  "expression_summary": "..."
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
- Decide if it is a "Match", "Exaggerated", "Vague" or "Mismatch".
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
- Give a brief comment explaining the rationale behind the score.
- Return ONLY a valid JSON object. Do not include any extra text, commentary, or code fences.

Expected JSON format:
{{
  "score": 85,
  "comment": "Candidate shows strong alignment with communication skills, but lacks technical depth."
}}
"""

ACCURACY_PROMPT = """
You are evaluating the overall **accuracy** of a candidate's answers during an interview.

Here are the Q&A pairs:
{qa_pairs}

1. Give a score between 0 and 100 for overall factual accuracy and consistency.
2. Write a one-line comment justifying the score.

Return only a valid JSON object like this:
{
  "overall": 83,
  "comment": "Mostly accurate answers with minor factual gaps."
}
"""

SOFT_SKILL_PROMPT = """
You are generating a final soft skill analysis and improvement suggestions based on a candidate's interview.

Summary Data:
- Tone Summary: {tone_summary}
- Expression Summary: {expression_summary}
- Accuracy Score: {accuracy_score}
- Job Fit Score: {job_fit_score}
- Validation Results: {validation_summary}
- Distractions: {total_distractions}
- Eye Contact: {average_eye_contact}%

Your task:
1. Estimate the candidate's soft skills in three areas:
   - Communication
   - Confidence
   - Empathy

2. Suggest 2-3 **specific improvements** they can work on to perform better in interviews.

Return ONLY a valid JSON object:
{
  "soft_skills": {
    "communication": "strong | moderate | weak",
    "confidence": "strong | moderate | weak",
    "empathy": "strong | moderate | weak"
  },
  "suggestions": [
    "...",
    "...",
    "..."
  ]
}
"""
