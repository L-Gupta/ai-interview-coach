// API Configuration
const BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

// Get authorization token from localStorage
function getAuthToken() {
  return localStorage.getItem("access_token");
}

// Get authorization headers
function getHeaders(includeAuth = false) {
  const headers = { "Content-Type": "application/json" };
  if (includeAuth) {
    const token = getAuthToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
  }
  return headers;
}

// ============= AUTHENTICATION ENDPOINTS =============

export async function register(userData) {
  const res = await fetch(`${BASE_URL}/api/v1/auth/register`, {
    method: "POST",
    headers: getHeaders(false),
    body: JSON.stringify(userData),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function login(credentials) {
  const res = await fetch(`${BASE_URL}/api/v1/auth/login`, {
    method: "POST",
    headers: getHeaders(false),
    body: JSON.stringify(credentials),
  });
  if (!res.ok) throw new Error(await res.text());
  const data = await res.json();
  if (data.access_token) {
    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token || "");
  }
  return data;
}

export async function logout() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
}

export function isAuthenticated() {
  return !!getAuthToken();
}

// ============= INTERVIEW ENDPOINTS =============

export async function startInterview(sessionData) {
  const res = await fetch(`${BASE_URL}/api/v1/interview/start`, {
    method: "POST",
    headers: getHeaders(true),
    body: JSON.stringify(sessionData),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getNextQuestion(sessionId) {
  const res = await fetch(`${BASE_URL}/api/v1/interview/${sessionId}/question`, {
    method: "GET",
    headers: getHeaders(true),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function submitAnswer(sessionId, answerData) {
  const res = await fetch(`${BASE_URL}/api/v1/interview/${sessionId}/submit-answer`, {
    method: "POST",
    headers: getHeaders(true),
    body: JSON.stringify(answerData),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getInterviewReport(sessionId) {
  const res = await fetch(`${BASE_URL}/api/v1/interview/${sessionId}/report`, {
    method: "GET",
    headers: getHeaders(true),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function endInterview(sessionId) {
  const res = await fetch(`${BASE_URL}/api/v1/interview/${sessionId}/end`, {
    method: "POST",
    headers: getHeaders(true),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

// ============= RESUME ENDPOINTS =============

export async function uploadResume(file, resumeId = null) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("resume_id", resumeId || file.name.split('.')[0]);

  const res = await fetch(`${BASE_URL}/api/v1/file/upload-resume`, {
    method: "POST",
    headers: { "Authorization": `Bearer ${getAuthToken()}` },
    body: formData,
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getResumeStatus(resumeId) {
  const res = await fetch(`${BASE_URL}/api/v1/file/resume-status/${resumeId}`, {
    headers: getHeaders(true),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function reprocessResume(resumeId) {
  const res = await fetch(`${BASE_URL}/api/v1/file/reprocess-resume/${resumeId}`, {
    method: "POST",
    headers: getHeaders(true),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

// ============= HEALTH CHECK =============

export async function healthCheck() {
  try {
    const res = await fetch(`${BASE_URL}/health`);
    return res.ok;
  } catch (error) {
    return false;
  }
}
