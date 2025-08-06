import React, { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import "./summary.css";

function SummaryComponent() {
  const location = useLocation();
  const { resumeId } = location.state || {};

  const [loading, setLoading] = useState(true);
  const [summaryData, setSummaryData] = useState(null);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const res = await fetch(`http://127.0.0.1:8000/interview/summary/${resumeId}`, {
          method: "GET",
        });
        const data = await res.json();
        setSummaryData(data);
      } catch (err) {
        console.error("Error fetching summary:", err);
      } finally {
        setLoading(false);
      }
    };
    if (resumeId) fetchSummary();
  }, [resumeId]);

  if (!resumeId) return <div className="summary-container">No resume ID provided</div>;
  if (loading) return <div className="summary-container">Loading summary...</div>;

  const expression = summaryData.expression_report || {};
  const tone = summaryData.tone_report || {};
  const integrity = summaryData.integrity || {};

  return (
    <div className="summary-container">
      <h2>Interview Summary</h2>

      {/* 1️⃣ Tone & Expression */}
      <div className="summary-section">
        <h3>Behavioral Analysis</h3>
        <p><strong>🎤 Tone Summary:</strong> {tone.tone_summary || "N/A"}</p>
        <p><strong>🎥 Expression Summary:</strong> {expression.expression_summary || "N/A"}</p>
        <p><strong>Dominant Emotions:</strong> {expression.dominant_emotions?.join(", ") || "N/A"}</p>
        <p><strong>Average Eye Contact:</strong> {expression.average_eye_contact}%</p>
        <p><strong>Total Distractions:</strong> {expression.total_distractions}</p>
        <p><strong>Times Face Was Absent:</strong> {expression.total_face_absence}</p>
        <p><strong>Multiple People Detected:</strong> {expression.multi_person_flag ? "Yes" : "No"}</p>
      </div>

      {/* 2️⃣ Candidate Verification */}
      <div className="summary-section">
        <h3>Verification of Candidate</h3>
        {Object.entries(summaryData.validation || {}).map(([q, result]) => (
          <p key={q}><strong>{q}:</strong> {result}</p>
        ))}
      </div>

      {/* 3️⃣ Job Fit */}
      <div className="summary-section">
        <h3>Job Fit</h3>
        <p><strong>Score:</strong> {summaryData.job_fit_score}%</p>
        <p><strong>AI Comment:</strong> {summaryData.job_fit_comment || "No comment provided."}</p>
      </div>

      {/* 4️⃣ Accuracy */}
      <div className="summary-section">
        <h3>Accuracy of Responses</h3>
        <ul>
          {Object.entries(summaryData.accuracy_scores || {}).map(([q, score]) => (
            <li key={q}>{q}: {score}%</li>
          ))}
        </ul>
      </div>

      {/* 5️⃣ Integrity Check */}
      <div className="summary-section">
        <h3>Integrity Check</h3>
        <p><strong>Unfair Assistance Detected:</strong> {integrity.unfair_assistance ? "Yes" : "No"}</p>
        <p><strong>Distractions:</strong></p>
        <ul>
          {(integrity.distractions || []).map((item, idx) => (
            <li key={idx}>⚠️ {item}</li>
          ))}
        </ul>
      </div>

      {/* 6️⃣ PDF Link */}
      {summaryData.pdf_url && (
        <a className="download-btn" href={summaryData.pdf_url} target="_blank" rel="noopener noreferrer">
          📄 Download Full PDF Report
        </a>
      )}
    </div>
  );
}

export default SummaryComponent;
