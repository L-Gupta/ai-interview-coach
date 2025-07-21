// frontend/src/components/AudioRecorder.jsx
import React, { useState, useRef } from 'react';
import './audio-recorder.css';

function AudioComponent() {
  const [recording, setRecording] = useState(false);
  const [audioURL, setAudioURL] = useState(null);
  const [transcript, setTranscript] = useState('');
  const [emotion, setEmotion] = useState('');
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mediaRecorder = new MediaRecorder(stream);
    mediaRecorderRef.current = mediaRecorder;
    audioChunksRef.current = [];

    mediaRecorder.ondataavailable = event => {
      audioChunksRef.current.push(event.data);
    };

    mediaRecorder.onstop = async () => {
      const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
      const audioURL = URL.createObjectURL(audioBlob);
      setAudioURL(audioURL);

      const formData = new FormData();
      formData.append("file", audioBlob, "recording.webm");

      try {
        const res = await fetch("http://127.0.0.1:8000/analyze-audio/", {
          method: "POST",
          body: formData,
        });

        const data = await res.json();
        setTranscript(data.transcript || "No transcript found.");
        setEmotion(data.emotion || "No emotion detected.");
      } catch (err) {
        setTranscript("Error retrieving transcript.");
        setEmotion("Error analyzing emotion.");
        console.error(err);
      }
    };

    mediaRecorder.start();
    setRecording(true);
  };

  const stopRecording = () => {
    mediaRecorderRef.current.stop();
    setRecording(false);
  };

  return (
    <div className="audio-recorder">
      <h2>🎤 Record Your Answer</h2>

      <button 
        onClick={recording ? stopRecording : startRecording}
        className={recording ? "stop-btn" : "start-btn"}>
        {recording ? "⏹️ Stop Recording" : "🎙️ Start Recording"}
      </button>

      {audioURL && (
        <div className="audio-preview">
          <audio controls src={audioURL}></audio>
        </div>
      )}

      {transcript && (
        <div className="transcript-box">
          <h4>📝 Transcript:</h4>
          <p>{transcript}</p>
        </div>
      )}

      {emotion && (
        <div className="emotion-box">
          <h4>😊 Detected Emotion:</h4>
          <p>{emotion}</p>
        </div>
      )}
    </div>
  );
}

export default AudioComponent
