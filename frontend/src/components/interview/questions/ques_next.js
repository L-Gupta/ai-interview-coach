export async function generateNextQuestion(resumeId, role) {
  try {
    // Call the follow-up question generation
    const res = await fetch('http://127.0.0.1:8000/question/generate-followup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        resume_id: resumeId,
        role: role
      })
    });

    if (!res.ok) throw new Error('Failed to generate follow-up question');
    const data = await res.json();
    return data.question || 'No follow-up question generated.';
  } catch (err) {
    console.error('Error generating follow-up question:', err);
    return 'Error generating follow-up question.';
  }
}
