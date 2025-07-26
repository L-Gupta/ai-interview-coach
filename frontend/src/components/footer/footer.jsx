import React from 'react';
import './footer.css';

const Footer = () => {
  return (
    <footer className="app-footer">
      <p>© 2025 AI Interview Coach | All Rights Reserved</p>
      <nav>
        <a href="/">Home</a> |
        <a href="/about">About</a> |
        <a href="/contact">Contact</a>
      </nav>
    </footer>
  );
};

export default Footer;
