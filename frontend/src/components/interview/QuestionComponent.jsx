import React, { useState, useEffect } from 'react';
import { generateFirstQuestion } from './ques_first';
import { generateNextQuestion } from './ques_next';
import { useLocation } from 'react-router-dom';
import './interview.css';

const speakQuestion = async (text) => {
  try {
    const response = await fetch("https://api.deepgram.com/v1/speak", {
      method: "POST",
      headers: {
        "Authorization": `Token ${process.env.REACT_APP_DEEPGRAM_API_KEY}`,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg" // ✅ Force Deepgram to return audio
      },
      body: JSON.stringify({
        text: text,
        model: "aura-asteria-en"
      }),
    });

    const blob = await response.blob();
    console.log("🔊 Deepgram blob type:", blob.type);

    // ✅ If response is not audio, print the actual error message
    if (!blob.type.startsWith("audio/")) {
      const errorText = await blob.text();
      console.error("❌ Invalid audio blob response from Deepgram:", errorText);
      return;
    }

    const audio = new Audio(URL.createObjectURL(blob));
    audio.play();

  } catch (err) {
    console.error("🔇 TTS playback failed:", err);
  }
};



function QuestionComponent({ transcript, setCurrentQuestionId, clearTranscript, setCurrentQuestion }) {
  const location = useLocation();
  const { name, resumeId, role } = location.state || {};

  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(true);
  const [history, setHistory] = useState([]);
  const [answer, setAnswer] = useState('');

  useEffect(() => {
    if (!name) return;

    const first = generateFirstQuestion(name);
    setQuestion(first);
    setCurrentQuestionId('q1');
    setLoading(false);
    setCurrentQuestion(first);
    speakQuestion(first);
  }, [name, setCurrentQuestionId, setCurrentQuestion]);

  useEffect(() => {
    if (transcript) {
      setAnswer(transcript);
    }
  }, [transcript]);

  const handleSubmit = async () => {
    if (!answer.trim()) return;

    const updatedHistory = [...history, { question, answer }];
    setHistory(updatedHistory);
    setAnswer('');

    if (clearTranscript) clearTranscript();

    const nextQuestionId = `q${updatedHistory.length + 1}`;
    setCurrentQuestionId(nextQuestionId);

    setLoading(true);
    const nextQ = await generateNextQuestion(resumeId, role);
    setQuestion(nextQ);
    setCurrentQuestion(nextQ);
    speakQuestion(nextQ)
    setLoading(false);
  };

  return (
    <div className="question-panel">
      <h2>Interview Question</h2>
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
          />
          <button className="submit-btn" onClick={handleSubmit} disabled={loading}>✅ Submit</button>
        </div>

        {transcript && (
          <div className="transcript-box">
            <h4>📝 Transcript:</h4>
            <p>{transcript}</p>
          </div>
        )}
      </div>

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
