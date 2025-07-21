import React, {useState} from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

import './App.css';
import Header from './components/header/HeaderComponent';
import HomeComponent from './components/home/HomeComponent';
import JobInfoComponent from './components/job-info/JobInfoComponent';
import InterviewComponent from './components/interview/InterviewComponent';

function App() {
  const [questions, setQuestions] = useState([]);
  return (
    <Router>
      <div className="app-container">
        <Header />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<HomeComponent />} />
            <Route path="/job-info" element={<JobInfoComponent />} />
            <Route path="/interview" element={<InterviewComponent questions={questions} />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
