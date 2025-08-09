// QuestionComponent.jsx
import React, { useState, useEffect } from 'react';
import { generateFirstQuestion, generateLastQuestion } from './ques_first_and_last';
import { generateNextQuestion } from './ques_next';
import { useLocation } from 'react-router-dom';
import './interview.css';

const BACKEND_BASE = "http://127.0.0.1:8000"; // hardcoded per your request

// 🔊 Singleton audio so questions don't overlap
let currentAudio = null;

const speakQuestion = async (text) => {
  try {
    // Stop any previous playback
    if (currentAudio) {
      try { currentAudio.pause(); } catch {}
      try { currentAudio.src = ""; } catch {}
      currentAudio = null;
    }

    const res = await fetch(`${BACKEND_BASE}/tts`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, model: "aura-asteria-en" })
    });

    if (!res.ok) {
      console.error("❌ Backend TTS failed:", await res.text());
      return;
    }

    const blob = await res.blob();
    const url = URL.createObjectURL(blob);

    const audio = new Audio();
    audio.preload = "auto";
    audio.playsInline = true;
    audio.src = url;
    currentAudio = audio;

    // When called inside a click handler (Submit / Start), autoplay policies allow this
    await audio.play();

    audio.onended = () => {
      URL.revokeObjectURL(url);
      if (currentAudio === audio) currentAudio = null;
    };
  } catch (err) {
    console.error("🔇 TTS playback failed:", err);
  }
};

function QuestionComponent({
  transcript,
  setCurrentQuestionId,
  clearTranscript,
  setCurrentQuestion,
  onReadyToExit
}) {
  const location = useLocation();
  const { name, resumeId, role } = location.state || {};

  const [hasStarted, setHasStarted] = useState(false);
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const [answer, setAnswer] = useState('');
  const [isEnding, setIsEnding] = useState(false);

  // Total questions allowed (intro + follow-ups)
  const MAX_QUESTIONS = 6;

  // Keep input synced with latest mic transcript
  useEffect(() => {
    if (transcript) setAnswer(transcript);
  }, [transcript]);

  // Start interview on click (prevents autoplay block for the very first question)
  const startInterview = async () => {
    if (hasStarted || !name) return;
    const first = generateFirstQuestion(name);
    setHasStarted(true);
    setLoading(false);
    setQuestion(first);
    setCurrentQuestionId('q1');
    setCurrentQuestion(first);

    // Speak the first question within the same user gesture
    await speakQuestion(first);
  };

  const handleSubmit = async () => {
    if (!answer.trim() || isEnding) return;

    const updatedHistory = [...history, { question, answer }];
    setHistory(updatedHistory);
    setAnswer('');
    clearTranscript?.();

    // Next human-friendly index after this submission
    const nextCount = updatedHistory.length + 1;

    // If we've already asked & answered MAX_QUESTIONS, now we do the goodbye
    if (nextCount > MAX_QUESTIONS) {
      const bye = generateLastQuestion(name);
      setQuestion(bye);
      setCurrentQuestionId('end');
      setCurrentQuestion(bye);
      setIsEnding(true);

      // 🔊 Speak farewell as part of the click chain
      await speakQuestion(bye);

      // Optional: auto-exit after a short delay
      setTimeout(() => onReadyToExit?.(), 3500);
      return;
    }

    // Otherwise fetch the next question
    setLoading(true);
    const nextQ = await generateNextQuestion(resumeId, role);
    setQuestion(nextQ);
    setCurrentQuestion(nextQ);
    setCurrentQuestionId(`q${nextCount}`);
    setLoading(false);

    // 🔊 Speak the next question immediately after submit (still user-initiated)
    await speakQuestion(nextQ);
  };

  // Live counter: answered so far + currently shown
  const questionCount = history.length + (question ? 1 : 0);

  return (
    <div className="question-panel">
      <div className="question-header">
        <h2>{hasStarted ? `Interview Question ${questionCount}` : 'Ready to start?'}</h2>
        {hasStarted && question && !isEnding && (
          <button
            className="play-btn"
            onClick={() => speakQuestion(question)}
            title="Play question audio"
          >
            🔊 Play
          </button>
        )}
      </div>

      {!hasStarted ? (
        <div className="question-card">
          <p>Click below to begin. We’ll read the first question out loud.</p>
          <button className="submit-btn" onClick={startInterview}>
            ▶️ Start Interview
          </button>
        </div>
      ) : (
        <div className="question-card">
          {loading ? (
            <p>Loading question...</p>
          ) : (
            <p><strong>Q:</strong> {question}</p>
          )}

          <div className="answer-box">
            <input
              type="text"
              placeholder="Type your answer or use audio"
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              disabled={isEnding}
            />
            <button
              className="submit-btn"
              onClick={handleSubmit}
              disabled={loading || isEnding}
            >
              {isEnding ? 'Finishing…' : '✅ Submit'}
            </button>
          </div>

          {transcript && (
            <div className="transcript-box">
              <h4>📝 Transcript:</h4>
              <p>{transcript}</p>
            </div>
          )}
        </div>
      )}

      {history.length > 0 && (
        <div className="questions-list">
          <h4>Previous Questions:</h4>
          {history.map((item, idx) => (
            <div key={idx} className="question-item submitted">
              <p><strong>Q:</strong> {item.question}</p>
              <p><strong>A:</strong> {item.answer}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default QuestionComponent;
