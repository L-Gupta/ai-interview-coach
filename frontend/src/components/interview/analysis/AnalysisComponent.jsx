import React from 'react';
import './../interview.css';

function AnalysisComponent({ currentQuestionId, emotions = [] }) {
  return (
    <div className="interview-left">
      <div className="analysis-card">
        {emotions.length === 0 ? (
          <p>Waiting for analysis...</p>
        ) : (
          <div>
            <h4>Emotions for {currentQuestionId}</h4>
            <ul>
              {emotions.map((tone, idx) => (
                <li key={idx}>{tone.toLowerCase()}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}

export default AnalysisComponent;
