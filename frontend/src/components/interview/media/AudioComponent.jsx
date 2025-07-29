import React, { useState, useRef, useEffect } from 'react';
import RecordRTC from 'recordrtc';
import '../interview.css';

function AudioComponent({ onTranscript, onEmotions, resume_id, currentQuestionId, currentQuestion }) {
  const [recording, setRecording] = useState(false);
  const [audioURL, setAudioURL] = useState(null);
  const recorderRef = useRef(null);

  //🎤 Start recording audio as WAV
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      const recorder = new RecordRTC(stream, {
        type: 'audio',
        mimeType: 'audio/wav',
        recorderType: RecordRTC.StereoAudioRecorder,
        numberOfAudioChannels: 1,
        desiredSampRate: 16000
      });

      recorderRef.current = recorder;
      recorder.startRecording();
      setRecording(true);

      console.log("🎤 Recording started (WAV, 16kHz mono)");
    } catch (err) {
      console.error("Microphone access error:", err);
      alert("Unable to access microphone. Please allow mic permissions.");
    }
  };

  // ⏹️ Stop recording and send to backend
  const stopRecording = async () => {
    if (!recorderRef.current) return;

    recorderRef.current.stopRecording(async () => {
      const blob = recorderRef.current.getBlob();
      const url = URL.createObjectURL(blob);
      setAudioURL(url);

      // ✅ Prepare form data with audio + metadata
      const formData = new FormData();
      formData.append("file", blob, "recording.wav");
      formData.append("resume_id", resume_id);
      formData.append("question_id", currentQuestionId || "q1");
      formData.append("question", currentQuestion || "Unknown Question")

      try {
        // 📤 1️⃣ Call /audio-transcribe (transcription + conv_history.json)
        const transcribeRes  = await fetch("http://127.0.0.1:8000/audio-transcribe", {
          method: "POST",
          body: formData,
        });

        const transcribeData = await transcribeRes.json();
        console.log("✅ Transcript response:", transcribeData);

        if (onTranscript) {
          onTranscript(transcribeData.transcript || "No transcript found.");
        }

        // 📤 2️⃣ Call /tone-analysis (chunking + emotions + tone.json)
        const toneRes = await fetch("http://127.0.0.1:8000/tone-analysis", {
          method: "POST",
          body: formData,
        });

        const toneData = await toneRes.json();
        console.log("✅ Tone analysis response:", toneData);

        if (onEmotions && toneData.emotions) {
          onEmotions(toneData.emotions);
        }
        
      } catch (err) {
        console.error("❌ Error uploading audio:", err);
      }

      setRecording(false);
    });
  };

  useEffect(() => {
    return () => {
      if (recorderRef.current) {
        recorderRef.current.destroy();
        recorderRef.current = null;
      }
    };
  }, []);

  return (
    <div className="audio-recorder">
      <h2>🎤 Record Your Answer</h2>

      <button onClick={recording ? stopRecording : startRecording} className={recording ? "stop-btn" : "start-btn"}>
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
