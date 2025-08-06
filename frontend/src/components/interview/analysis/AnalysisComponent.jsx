import React from 'react';
import './../interview.css';

function AnalysisComponent({ currentQuestionId, tone = [], emotion = [] }) {
  const isEmpty = tone.length === 0 && emotion.length === 0;

  return (
    <div className="interview-left">
      <div className="analysis-card">
        {isEmpty ? (
          <p>Waiting for analysis...</p>
        ) : (
          <div>
            <h4>Analysis for Question: {currentQuestionId}</h4>

            {tone.length > 0 && (
              <>
                <strong>🎤 Tone (Audio):</strong>
                <ul>
                  {tone.map((t, idx) => (
                    <li key={`tone-${idx}`}>{t.toLowerCase()}</li>
                  ))}
                </ul>
              </>
            )}

            {emotion.length > 0 && (
              <>
                <strong>🎥 Emotions (Facial):</strong>
                <ul>
                  {emotion.map((e, idx) => (
                    <li key={`emotion-${idx}`}>{e.toLowerCase()}</li>
                  ))}
                </ul>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default AnalysisComponent;
