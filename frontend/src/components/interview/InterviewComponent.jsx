import React, { useEffect, useRef, useState } from 'react';
import './interview.css';
import AudioComponent from './AudioComponent'

function InterviewComponent({ questions }) {
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const [micMuted, setMicMuted] = useState(false);
  const [camOff, setCamOff] = useState(false);
  const [mediaError, setMediaError] = useState('');
  const [submittedIndexes, setSubmittedIndexes] = useState([]);
  const [activeIndex, setActiveIndex] = useState(0);

  useEffect(() => {
    async function startMedia() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
        streamRef.current = stream;
        if (videoRef.current) videoRef.current.srcObject = stream;
      } catch (error) {
        console.error('Error accessing media devices:', error);
        setMediaError('Could not access webcam or mic.');
      }
    }
    startMedia();
  }, []);

  const toggleMic = () => {
    const audioTrack = streamRef.current?.getAudioTracks()[0];
    if (audioTrack) {
      const newState = !audioTrack.enabled;
      audioTrack.enabled = newState;
      setMicMuted(!newState);
    }
  };

  const toggleCamera = () => {
    const videoTrack = streamRef.current?.getVideoTracks()[0];
    if (videoTrack) {
      videoTrack.enabled = !videoTrack.enabled;
      setCamOff(!videoTrack.enabled);
    }
  };

  const handleSubmitAnswer = () => {
    setSubmittedIndexes([...submittedIndexes, activeIndex]);
    setActiveIndex((prev) => (prev + 1 < questions.length ? prev + 1 : prev));
  };

  const handleRepeat = () => {
    const synth = window.speechSynthesis;
    const utterance = new SpeechSynthesisUtterance(questions[activeIndex]);
    synth.speak(utterance);
  };

  return (
    <div className="interview-3col">
        {/* Left: Live Feedback Placeholder */}
        <div className="interview-left">
            <h3>Live Feedback</h3>
            <div className="feedback-placeholder">(dynamic tone & emotion feedback will show here)</div>
        </div>

        {/* Center: Webcam and Controls */}
        <div className="interview-center">
            <video ref={videoRef} autoPlay muted playsInline className="webcam-preview" />

            <div className="webcam-controls">
                <button onClick={toggleMic}>{micMuted ? '🔇 Mic Off' : '🎙️ Mic On'}</button>
                <button onClick={toggleCamera}>{camOff ? '📷❌ Cam Off' : '📷 Cam On'}</button>
            </div>

            <AudioComponent />

            <button className="end-interview-button">
                🚪 End Interview
            </button>

        {mediaError && <p className="error-text">{mediaError}</p>}
        </div>

        {/* Right: Question List */}
        <div className="interview-right">
            <h3>Questions</h3>
            {questions.map((q, index) => (
                <div
                    key={index}
                    className={`question-box ${submittedIndexes.includes(index) ? 'submitted' : ''}`}
                    style={{ display: index > activeIndex ? 'none' : 'block' }}>
                    
                    <p><strong>Q{index + 1}:</strong> {q}</p>

                    {!submittedIndexes.includes(index) && (
                    <div className="question-actions">
                        <button onClick={handleRepeat}>🔁 Repeat</button>
                        <button onClick={handleSubmitAnswer}>📤 Submit</button>
                    </div>
                    )}
                </div>
            ))}
        </div>
    </div>
  );
}

export default InterviewComponent;
