export async function generateFirstQuestion(resumeId, role) {
  try {
    const res = await fetch('http://127.0.0.1:8000/question/generate-first-question', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ resume_id: resumeId, role: role })
    });

    if (!res.ok) throw new Error('Failed to generate question');
    const data = await res.json();
    return data.question || 'No question generated.';
  } catch (err) {
    console.error('Error generating first question:', err);
    return 'Error generating question.';
  }
}
