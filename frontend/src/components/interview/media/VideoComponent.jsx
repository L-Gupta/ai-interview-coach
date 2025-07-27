import React, { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../interview.css';
import AudioComponent from './AudioComponent';

function VideoComponent({ onTranscript, resumeId, conversationHistory, role}) {
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const [micMuted, setMicMuted] = useState(false);
  const [camOff, setCamOff] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    async function startMedia() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
        streamRef.current = stream;
        if (videoRef.current) videoRef.current.srcObject = stream;
      } catch (error) {
        console.error('Media access error:', error);
      }
    }
    startMedia();
  }, []);

  const toggleMic = () => {
    const track = streamRef.current?.getAudioTracks()[0];
    if (track) {
      track.enabled = !track.enabled;
      setMicMuted(!track.enabled);
    }
  };

  const toggleCam = () => {
    const track = streamRef.current?.getVideoTracks()[0];
    if (track) {
      track.enabled = !track.enabled;
      setCamOff(!track.enabled);
    }
  };

  const handleExitInterview = async () => {
    if (!window.confirm("Are you sure you want to end the interview?")) return;

    // Stop camera and mic
    streamRef.current?.getTracks().forEach(track => track.stop());

    // ✅ Send resumeId,  conversation history and role to backend
    fetch(`http://127.0.0.1:8000/interview/exit/${resumeId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ conversation_history: conversationHistory, role: role }),
    }).catch(err => console.error('Error finalizing interview:', err));

    // ✅ Navigate to summary page with resumeId
    navigate('/summary', { state: { resumeId } });
  };

  return (
    <div className="interview-center">
      <video ref={videoRef} autoPlay muted playsInline className="webcam-preview" />
      
      <div className="webcam-controls">
        <button onClick={toggleMic}>{micMuted ? '🔇 Mic Off' : '🎙️ Mic On'}</button>
        <button onClick={toggleCam}>{camOff ? '📷 Cam Off' : '📷 Cam On'}</button>
      </div>

      <div className="recording-section">
        <AudioComponent onTranscript={onTranscript} />
      </div>

      <button className="exit-button" onClick={handleExitInterview}>🚪 Exit Interview</button>
    </div>
  );
}

export default VideoComponent;
