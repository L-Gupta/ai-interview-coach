import React, {
  useEffect, useRef, useState,
  forwardRef, useImperativeHandle
} from 'react';
import RecordRTC from 'recordrtc';
import '../interview.css';

const VideoComponent = forwardRef(({ resumeId, currentQuestionId, onEmotion }, ref) => {
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

    return () => {
      streamRef.current?.getTracks().forEach(track => track.stop());
    };
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

  const uploadVideo = async (blob) => {
    const formData = new FormData();
    formData.append("resume_id", resumeId);
    formData.append("question_id", currentQuestionId || "q1");
    formData.append("video", blob, "response.webm");

    try {
      const uploadRes = await fetch("http://127.0.0.1:8000/upload", {
        method: "POST",
        body: formData,
      });

      const uploadData = await uploadRes.json();
      console.log("📤 Upload response:", uploadData)

      if (!uploadRes.ok) {
        throw new Error("Upload failed: " + (uploadData?.error || "Unknown error"));
      }

      const analyzeRes = await fetch("http://127.0.0.1:8000/analyze", {
        method: "POST",
        body: formData,
      });

      const analyzeData = await analyzeRes.json();
      console.log("🎞️ Video analysis response:", analyzeData);

      if (analyzeData.emotions && analyzeData.emotions.length > 0) {
        onEmotion?.(analyzeData.emotions);
      }

    } catch (err) {
      console.error("❌ Video upload/analyze error:", err);
    }
  };

  useImperativeHandle(ref, () => ({getVideoBlob: async () => {
    const recorder = new RecordRTC(streamRef.current, { type: 'video' });
    recorder.startRecording();
    await new Promise(resolve => setTimeout(resolve, 10000));
    await recorder.stopRecording();
    const blob = recorder.getBlob();
    await uploadVideo(blob);
    return blob;
  },
  stopMediaTracks: () => {
    streamRef.current?.getTracks().forEach(track => track.stop());
  }
}));

  return (
    <div className="interview-center">
      <video ref={videoRef} autoPlay muted playsInline className="webcam-preview" />
      <div className="webcam-controls">
        <button onClick={toggleMic}>{micMuted ? '🔇 Mic Off' : '🎙️ Mic On'}</button>
        <button onClick={toggleCam}>{camOff ? '📷 Cam Off' : '📷 Cam On'}</button>
      </div>
    </div>
  );
});

export default VideoComponent;
