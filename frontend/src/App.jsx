import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

import './App.css';
import Header from './components/header/HeaderComponent';
import HomeComponent from './components/home/HomeComponent';
import JobInfoComponent from './components/job-info/JobInfoComponent';
import InterviewComponent from './components/interview/InterviewComponent';
import SummaryComponent from './components/summary/SummaryComponent';

function App() {
  const [questions, setQuestions] = useState([]);

  return (
    <Router>
      <div className="app-container">
        <Header />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<HomeComponent />} />
            <Route path="/job-info" element={<JobInfoComponent setQuestions={setQuestions} />} />
            <Route path="/interview" element={<InterviewComponent questions={questions} />} />
            <Route path="/summary" element={<SummaryComponent />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
