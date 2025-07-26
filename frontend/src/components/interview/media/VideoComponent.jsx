import React, { useEffect, useRef, useState } from 'react';
import '../interview.css';
import AudioComponent from './AudioComponent';

function VideoComponent({ onTranscript }) {
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const [micMuted, setMicMuted] = useState(false);
  const [camOff, setCamOff] = useState(false);

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

  return (
    <div className="interview-center">
      <video ref={videoRef} autoPlay muted playsInline className="webcam-preview" />
      
      <div className="webcam-controls">
        <button onClick={toggleMic}>{micMuted ? '🔇 Mic Off' : '🎙️ Mic On'}</button>
        <button onClick={toggleCam}>{camOff ? '📷 Cam Off' : '📷 Cam On'}</button>
      </div>

      <div className="recording-section">
        {/* ✅ Pass onTranscript callback to AudioComponent */}
        <AudioComponent onTranscript={onTranscript} />
      </div>

      <button className="exit-button">🚪 Exit Interview</button>
    </div>
  );
}

export default VideoComponent;
