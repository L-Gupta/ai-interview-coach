// QuestionComponent.jsx
import React, { useState, useEffect } from 'react';
import { generateFirstQuestion, generateLastQuestion } from './ques_first_and_last';
import { generateNextQuestion } from './ques_next';
import { useLocation } from 'react-router-dom';
import './interview.css';

const BACKEND_BASE = "http://127.0.0.1:8000";

let currentAudio = null;
const speakQuestion = async (text) => {
  try {
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

  const MAX_QUESTIONS = 6;

  useEffect(() => {
    if (transcript) setAnswer(transcript);
  }, [transcript]);

  const startInterview = async () => {
    if (hasStarted || !name) return;
    const first = generateFirstQuestion(name);
    setHasStarted(true);
    setLoading(false);
    setQuestion(first);
    setCurrentQuestionId('q1');
    setCurrentQuestion(first);
    await speakQuestion(first);
  };

  const handleSubmit = async () => {
    if (!answer.trim() || isEnding) return;

    const updatedHistory = [...history, { question, answer }];
    setHistory(updatedHistory);
    setAnswer('');
    clearTranscript?.();
    const nextCount = updatedHistory.length + 1;

    if (nextCount > MAX_QUESTIONS) {
      // Always use a fixed farewell string
      const bye = generateLastQuestion(name);
      setQuestion(bye);
      setCurrentQuestionId('end');
      setCurrentQuestion(bye);
      setIsEnding(true);
      await speakQuestion(bye);
      setTimeout(() => onReadyToExit?.(), 3500);
      return;
    }

    setLoading(true);
    const nextQ = await generateNextQuestion(resumeId, role);
    setQuestion(nextQ);
    setCurrentQuestion(nextQ);
    setCurrentQuestionId(`q${nextCount}`);
    setLoading(false);
    await speakQuestion(nextQ);
  };

  const questionCount = history.length + (question ? 1 : 0);

  return (
    <div className="question-panel">
      <div className="question-header">
        <h2>
          {hasStarted
            ? (isEnding ? 'Wrapping up' : `Interview Question ${questionCount}`)
            : 'Ready to start?'}
        </h2>
        {hasStarted && question && !isEnding && (
          <button
            className="repeat-btn"
            onClick={() => speakQuestion(question)}
            title="Repeat question audio"
          >
            ⟲ Repeat
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
          ) : isEnding ? (
            <p>{question}</p> // No "Q:" prefix for farewell
          ) : (
            <p><strong>Q:</strong> {question}</p>
          )}

          {!isEnding && (
            <div className="answer-box">
              <input
                type="text"
                placeholder="Type your answer or use audio"
                value={answer}
                onChange={(e) => setAnswer(e.target.value)}
              />
              <button
                className="submit-btn"
                onClick={handleSubmit}
                disabled={loading}
              >
                ✅ Submit
              </button>
            </div>
          )}

          {transcript && !isEnding && (
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
