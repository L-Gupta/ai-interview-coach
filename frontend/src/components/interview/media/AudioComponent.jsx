import React, { useState, useRef } from 'react';
import '../interview.css';

function AudioComponent({ onTranscript }) {
  const [recording, setRecording] = useState(false);
  const [audioURL, setAudioURL] = useState(null);
  const [transcript, setTranscript] = useState('');
  const [emotion, setEmotion] = useState('');
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const startRecording = async () => {
    try {
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
          const t = data.transcript || "No transcript found.";
          setTranscript(t);
          setEmotion(data.emotion || "No emotion detected.");

          // ✅ Send transcript up to parent
          if (onTranscript) onTranscript(t);

        } catch (err) {
          setTranscript("Error retrieving transcript.");
          setEmotion("Error analyzing emotion.");
          console.error(err);
        }
      };

      mediaRecorder.start();
      setRecording(true);
    } catch (err) {
      console.error("Microphone access error:", err);
      alert("Unable to access microphone. Please allow mic permissions.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setRecording(false);
    }
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
    </div>
  );
}

export default AudioComponent;
