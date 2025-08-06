const BASE_URL = "http://localhost:8000"; 

// Call first question endpoint
export async function getFirstQuestion(role, resume_id) {
  const res = await fetch(`${BASE_URL}/generate-first-question`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ role, resume_id }),
  });
  return res.json();
}

// Call follow-up question endpoint
export async function getFollowupQuestion(role, resume_id, history) {
  const res = await fetch(`${BASE_URL}/generate-followup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ role, resume_id, history }),
  });
  return res.json();
}
