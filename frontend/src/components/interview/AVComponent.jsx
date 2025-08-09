import React, {
  useState, useRef, useEffect,
  forwardRef, useImperativeHandle
} from 'react';
import RecordRTC from 'recordrtc';
import './interview.css';

const AVComponent = forwardRef(({ onTranscript, onTone, onEmotion, resume_id, currentQuestionId, currentQuestion }, ref) => {
  const [recording, setRecording] = useState(false);
  const [audioURL, setAudioURL] = useState(null);

  const recorderRef = useRef(null);       // Ref for audio recorder
  const videoRef = useRef(null);          // Ref for video preview <video> element
  const streamRef = useRef(null);         // Ref for webcam + mic media stream
  const camRecorderRef = useRef(null);    // Ref for video recorder

  const [micMuted, setMicMuted] = useState(false);
  const [camOff, setCamOff] = useState(false);

  // 🟢 Request webcam + mic access once on mount
  useEffect(() => {
    async function startMedia() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
        streamRef.current = stream;
        if (videoRef.current) videoRef.current.srcObject = stream;
      } catch (err) {
        console.error("❌ Media access error:", err);
        alert("Please allow camera and microphone access.");
      }
    }
    startMedia();

    return () => {
      streamRef.current?.getTracks().forEach(track => track.stop());
    };
  }, []);

  // ▶️ Start audio + video recording
  const startRecording = async () => {
    try {
      const audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });

      // 🎤 Setup audio recorder
      const recorder = new RecordRTC(audioStream, {
        type: 'audio',
        mimeType: 'audio/wav',
        recorderType: RecordRTC.StereoAudioRecorder,
        numberOfAudioChannels: 1,
        desiredSampRate: 16000
      });

      recorderRef.current = recorder;
      recorder.startRecording();

      // 🎥 Setup and start video recorder using existing streamRef
      camRecorderRef.current = new RecordRTC(streamRef.current, { type: 'video' });
      camRecorderRef.current.startRecording();

      setRecording(true);
      console.log("🎙️ Audio and 🎥 Video recording started");
    } catch (err) {
      console.error("❌ Microphone access error:", err);
      alert("Unable to access microphone.");
    }
  };

  // ⏹️ Stop both recordings and call all analysis endpoints
  const stopRecording = async () => {
    if (!recorderRef.current || !camRecorderRef.current) return;

    recorderRef.current.stopRecording(async () => {
      const audioBlob = recorderRef.current.getBlob();
      const audioURL = URL.createObjectURL(audioBlob);
      setAudioURL(audioURL);

      const formData = new FormData();
      formData.append("file", audioBlob, "recording.wav");
      formData.append("resume_id", resume_id);
      formData.append("question_id", currentQuestionId || "q1");
      formData.append("question", currentQuestion || "Unknown Question");

      try {
        // 🎯 ENDPOINT: /audio-transcribe
        const transcribeRes = await fetch("http://127.0.0.1:8000/audio-transcribe", {
          method: "POST",
          body: formData,
        });
        const transcribeData = await transcribeRes.json();
        console.log("✅ /audio-transcribe response:", transcribeData);
        if (onTranscript) onTranscript(transcribeData.transcript || "No transcript found.");

        // 🎯 ENDPOINT: /tone-analysis
        const toneRes = await fetch("http://127.0.0.1:8000/tone-analysis", {
          method: "POST",
          body: formData,
        });
        const toneData = await toneRes.json();
        console.log("✅ /tone-analysis response:", toneData);
        const qid = currentQuestionId || "q1";
        const tones = (toneData && (toneData[qid] || toneData.tone || toneData.emotions)) || [];
        if (onTone) onTone(tones);

        // Stop and process video recording
        camRecorderRef.current.stopRecording(async () => {
          const videoBlob = camRecorderRef.current.getBlob();

          const videoForm = new FormData();
          videoForm.append("resume_id", resume_id);
          videoForm.append("question_id", currentQuestionId || "q1");
          videoForm.append("video", videoBlob, "response.webm");

          // 🎯 ENDPOINT: /upload
          const uploadRes = await fetch("http://127.0.0.1:8000/video-upload", {
            method: "POST",
            body: videoForm,
          });
          const uploadData = await uploadRes.json();
          console.log("✅ /upload response:", uploadData);
          if (!uploadRes.ok) throw new Error("Upload failed: " + (uploadData?.error || "Unknown error"));

          // 🎯 ENDPOINT: /analyze
          const analyzeRes = await fetch("http://127.0.0.1:8000/video-analyze", {
            method: "POST",
            body: videoForm,
          });
          const analyzeData = await analyzeRes.json();
          console.log("✅ /analyze response:", analyzeData);

          if (analyzeData.emotions && analyzeData.emotions.length > 0) {
            onEmotion?.(analyzeData.emotions);
          }
        });

      } catch (err) {
        console.error("❌ Error uploading or analyzing media:", err);
      }

      setRecording(false);
    });
  };

  // 🎚️ Toggle mic on/off
  const toggleMic = () => {
    const track = streamRef.current?.getAudioTracks()[0];
    if (track) {
      track.enabled = !track.enabled;
      setMicMuted(!track.enabled);
    }
  };

  // 🎥 Toggle webcam on/off
  const toggleCam = () => {
    const track = streamRef.current?.getVideoTracks()[0];
    if (track) {
      track.enabled = !track.enabled;
      setCamOff(!track.enabled);
    }
  };

  // 🛑 Allow parent to stop tracks if needed
  useImperativeHandle(ref, () => ({
    stopMediaTracks: () => {
      streamRef.current?.getTracks().forEach(track => track.stop());
    }
  }));

  return (
    <div className="av-recorder">
      <h2>🎙️🎥 Interview Recorder</h2>

      {/* Live webcam preview */}
      <video ref={videoRef} autoPlay muted playsInline className="webcam-preview" />

      {/* Mic and Camera toggles */}
      <div className="webcam-controls">
        <button onClick={toggleMic}>{micMuted ? '🔇 Mic Off' : '🎙️ Mic On'}</button>
        <button onClick={toggleCam}>{camOff ? '📷 Cam Off' : '📷 Cam On'}</button>
      </div>

      {/* Record/Stop control */}
      <div className="recording-controls">
        <button onClick={recording ? stopRecording : startRecording} className={recording ? "stop-btn" : "start-btn"}>
          {recording ? "⏹️ Stop Recording" : "▶️ Start Recording"}
        </button>
      </div>

      {/* Audio preview */}
      {audioURL && (
        <div className="audio-preview">
          <h4>🔊 Audio Preview</h4>
          <audio controls src={audioURL}></audio>
        </div>
      )}
    </div>
  );
});

export default AVComponent;
