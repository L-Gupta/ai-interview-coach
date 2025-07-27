import React, { useState } from 'react';
import './interview.css';
import { useLocation } from 'react-router-dom';
import AnalysisComponent from './analysis/AnalysisComponent';
import VideoComponent from './media/VideoComponent';
import QuestionComponent from './questions/QuestionComponent';

function InterviewComponent() {
  const location = useLocation();
  const { resumeId, role } = location.state || {};
  const [transcript, setTranscript] = useState('');

  return (
    <div className="interview-3col">
      {/* Left Column: Analysis */}
      <div className="interview-left">
        <AnalysisComponent />
      </div>

      {/* Center Column: Video + Audio */}
      <div className="interview-center">
        <VideoComponent onTranscript={setTranscript} resumeId={resumeId} conversationHistory={transcript} role={role} /> 
      </div>

      {/* Right Column: Questions */}
      <div className="interview-right">
        <QuestionComponent resumeId={resumeId} role={role} transcript={transcript} />
      </div>
    </div>
  );
}

export default InterviewComponent;
