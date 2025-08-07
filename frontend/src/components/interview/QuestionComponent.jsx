import React, { useState, useEffect } from 'react';
import { generateFirstQuestion } from './ques_first';
import { generateNextQuestion } from './ques_next';
import './interview.css';

function QuestionComponent({ resumeId, role, transcript, setCurrentQuestionId, clearTranscript, setCurrentQuestion }) {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(true);
  const [history, setHistory] = useState([]);
  const [answer, setAnswer] = useState('');

  useEffect(() => {
    if (!resumeId || !role) return;

    const fetchFirst = async () => {
      const q = await generateFirstQuestion(resumeId, role);
      setQuestion(q);
      setCurrentQuestionId('q1'); // first question id
      setLoading(false);
      setCurrentQuestion(q);
    };

    fetchFirst();
  }, [resumeId, role, setCurrentQuestionId, setCurrentQuestion]);

  // Auto-fill answer box when transcript updates
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

    // ✅ Clear transcript in parent so it doesn't carry over
    if (clearTranscript) clearTranscript();

    // Next question ID
    const nextQuestionId = `q${updatedHistory.length + 1}`;
    setCurrentQuestionId(nextQuestionId);

    setLoading(true);
    const nextQ = await generateNextQuestion( resumeId, role);
    setQuestion(nextQ);
    setCurrentQuestion(nextQ)
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
