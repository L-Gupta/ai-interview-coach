import React from 'react';
import './header.css';
import { Link } from 'react-router-dom'

function HeaderComponent() {
  return (
    <header className="site-header">
      <div className="header-container">
        <h1 className="logo">AI Interview Coach</h1>
        <nav className="nav-menu">
          <Link to="/">Home</Link>
          <Link to="/job-info">Upload Resume</Link>
          <Link to="/interview">Interview</Link>
        </nav>
      </div>
    </header>
  );
}

export default HeaderComponent;
