// InterviewComponent.jsx

import React, { useState, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import AnalysisComponent from './analysis/AnalysisComponent';
import VideoComponent from './media/VideoComponent';
import QuestionComponent from './questions/QuestionComponent';
import AudioComponent from './media/AudioComponent';
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

      {/* Center Column: Video + Audio */}
      <div className="interview-center">
        <div className="video-audio-stack">
          <VideoComponent 
            ref={videoRef}
            resumeId={resumeId}
            currentQuestionId={currentQuestionId}
            onEmotion = {setEmotion}
          />
          <AudioComponent
            onTranscript={setTranscript}
            onTone={setTone}
            currentQuestionId={currentQuestionId}
            resume_id={resumeId}
            currentQuestion={currentQuestion}
            videoRef={videoRef}
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
