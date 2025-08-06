export async function exitInterview(resumeId, role, navigate) {
  if (!window.confirm("Are you sure you want to end the interview?")) return;

  try {
    // 🔌 Call backend to finalize
    await fetch(`http://127.0.0.1:8000/interview/exit/${resumeId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ role }),
    });

    // 🚪 Navigate to summary page
    navigate('/summary', { state: { resumeId } });
  } catch (error) {
    console.error("❌ Exit interview error:", error);
  }
}