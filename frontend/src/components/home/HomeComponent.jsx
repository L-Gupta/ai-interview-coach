import React from 'react';
import './home.css';
import { Link } from 'react-router-dom';

function HomeComponent() {
  return (
    <div className="home-container">
      <section className="hero-section">
        <h1>Welcome to AI Interview Coach</h1>
        <p>
          Prepare for real-world interviews using AI. Get personalized questions,
          resume validation, and voice-video analysis in one seamless experience.
        </p>
        <Link to="/job-info" className="get-started-btn">
            Get Started
        </Link>
      </section>
    </div>
  );
}

export default HomeComponent;
