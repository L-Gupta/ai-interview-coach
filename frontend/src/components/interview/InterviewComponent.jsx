import React, { useState } from 'react';
import './interview.css';
import { useLocation } from 'react-router-dom';
import AnalysisComponent from './analysis/AnalysisComponent';
import VideoComponent from './media/VideoComponent';
import QuestionComponent from './questions/QuestionComponent';
import AudioComponent from './media/AudioComponent';

function InterviewComponent() {
  const location = useLocation();
  const { resumeId, role } = location.state || {};
  const [transcript, setTranscript] = useState('');
  const [currentQuestionId, setCurrentQuestionId] = useState('q1');
  const [currentEmotions, setCurrentEmotions] = useState([])
  const [currentQuestion, setCurrentQuestion] = useState("")
  const clearTranscript = () => setTranscript('');


  return (
    <div className="interview-3col">
      {/* Left Column: Analysis */}
      <div className="interview-left">
        <AnalysisComponent 
          resumeId={resumeId} 
          currentQuestionId={currentQuestionId}
          emotions={currentEmotions}
        />
      </div>

      {/* Center Column: Video + Audio */}
      <div className="interview-center">
        <div className="video-audio-stack">
          <VideoComponent 
            resumeId={resumeId} 
            conversationHistory={transcript} 
            role={role} 
          />
          <AudioComponent 
            onTranscript={setTranscript} 
            onEmotions={setCurrentEmotions} 
            currentQuestionId={currentQuestionId}
            resume_id={resumeId}   
            currentQuestion={currentQuestion} 
          />

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
