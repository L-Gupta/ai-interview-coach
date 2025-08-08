def followup_question_prompt(role: str, resume_context: str, conversation_text: str) -> str:
    return (
        f"You are an AI interview coach. The candidate is applying for the role of {role}.\n"
        f"Resume summary:\n\n{resume_context}\n\n"
        f"Conversation so far:\n\n{conversation_text}\n\n"
        f"Your task:\n"
        f"- Generate ONLY the next follow-up interview question.\n"
        f"- Base it on the candidate's previous answers and the job role.\n"
        f"- DO NOT include explanations, greetings, or any text other than the question.\n"
        f"- Return ONLY the question as plain text, no quotes, no prefixes like 'Q:'."
    )
