import React, { useState, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import AnalysisComponent from './AnalysisComponent';
import QuestionComponent from './QuestionComponent';
import AVComponent from './AVComponent';
import { exitInterview } from './exit';
import './interview.css';

function InterviewComponent() {
  const location = useLocation();
  const navigate = useNavigate();
  const videoRef = useRef();
  const { resumeId, role } = location.state || {};

  const [transcript, setTranscript] = useState('');
  const [currentQuestionId, setCurrentQuestionId] = useState('q1');
  const [tone, setTone] = useState([]);
  const [emotion, setEmotion] = useState([]);
  const [currentQuestion, setCurrentQuestion] = useState("");

  const clearTranscript = () => setTranscript('');

  const handleExit = () => {
    videoRef.current?.stopMediaTracks();
    exitInterview(resumeId, role, navigate);
  };

  return (
    <div className="interview-3col">
      {/* Left Column: Analysis */}
      <div className="interview-left">
        <AnalysisComponent 
          currentQuestionId={currentQuestionId}
          tone={tone}
          emotion={emotion}
        />
      </div>

      {/* Center Column: AV Recording */}
      <div className="interview-center">
        <div className="video-audio-stack">
          <AVComponent
            ref={videoRef}
            onTranscript={setTranscript}
            onTone={setTone}
            onEmotion={setEmotion}
            resume_id={resumeId}
            currentQuestionId={currentQuestionId}
            currentQuestion={currentQuestion}
          />
          <div className="exit-wrapper">
            <button className="exit-button" onClick={handleExit}>🚪 Exit Interview</button>
          </div>
        </div>
      </div>

      {/* Right Column: Questions */}
      <div className="interview-right">
        <QuestionComponent 
          resumeId={resumeId} 
          role={role} 
          transcript={transcript}
          setCurrentQuestionId={setCurrentQuestionId}
          clearTranscript={clearTranscript}
          setCurrentQuestion={setCurrentQuestion}
        />
      </div>
    </div>
  );
}

export default InterviewComponent;