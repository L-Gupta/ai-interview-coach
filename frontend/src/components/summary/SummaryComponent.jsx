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
        const res = await fetch(`http://127.0.0.1:8000/interview/exit/${resumeId}`, {
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

  return (
    <div className="summary-container">
      <h2>Interview Summary</h2>

      <div className="summary-section">
        <h3>Emotion Report</h3>
        <p><strong>Tone:</strong> {summaryData.emotion_report?.tone_summary}</p>
        <p><strong>Expression:</strong> {summaryData.emotion_report?.expression_summary}</p>
      </div>

      <div className="summary-section">
        <h3>Experience Validation</h3>
        <ul>
          {Object.entries(summaryData.validation || {}).map(([q, result]) => (
            <li key={q}>{q}: {result}</li>
          ))}
        </ul>
      </div>

      <div className="summary-section">
        <h3>Job-Fit Score</h3>
        <p>{summaryData.job_fit_score}%</p>
      </div>

      <div className="summary-section">
        <h3>Accuracy Scores</h3>
        <ul>
          {Object.entries(summaryData.accuracy_scores || {}).map(([q, score]) => (
            <li key={q}>{q}: {score}%</li>
          ))}
        </ul>
      </div>

      {summaryData.pdf_url && (
        <a className="download-btn" href={summaryData.pdf_url} target="_blank" rel="noopener noreferrer">
          Download PDF Report
        </a>
      )}
    </div>
  );
}

export default SummaryComponent;
