import React, { useState } from 'react';
import './job-info.css';
import { useNavigate } from 'react-router-dom';

// Component receives setQuestions from parent (App.jsx) to store Gemini questions globally
function JobInfoComponent({ setQuestions }) {
  const [selectedRole, setSelectedRole] = useState(''); // State for selected job role
  const [resumeFile, setResumeFile] = useState(null);   // State for uploaded resume file
  const [loading, setLoading] = useState(false);        // Loading state to disable the form and show progress
  const navigate = useNavigate();                         // React Router navigation hook

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();

    // Check that both fields are filled
    if (!selectedRole || !resumeFile) {
      alert("Please select a role and upload your resume.");
      return;
    }

    // Prepare FormData to send file + role to backend
    const formData = new FormData();
    formData.append('resume', resumeFile);
    formData.append('role', selectedRole);

    try {
      setLoading(true); // Disable button while loading

      // Send POST request to backend endpoint
      console.log("Submitting to backend:", selectedRole, resumeFile);
      const response = await fetch('http://127.0.0.1:8000/questions/generate', {
        method: 'POST',
        body: formData,
      });

      // Handle server error
      if (!response.ok) throw new Error('Server Error');

      // Extract JSON response
      const data = await response.json();

      // Save questions to state via parent setter
      setQuestions(data.questions);

      // Navigate to the interview page
      navigate('/interview');
    } catch (error) {
      // Show error to user
      alert('Failed to generate questions. Try again.');
      console.error(error);
    } finally {
      setLoading(false); // Re-enable form
    }
  };

  return (
    <div className="job-info-container">
      <h2>Step 1: Choose Role & Upload Resume</h2>

      {/* Main Form */}
      <form onSubmit={handleSubmit}>
        
        {/* Dropdown for role selection */}
        <div className="input-group">
          <label>Select Job Role:</label>
          <select value={selectedRole} onChange={(e) => setSelectedRole(e.target.value)}>
            <option value="" disabled>Select a role</option>
            <option value="Software Engineer">Software Engineer</option>
            <option value="Data Scientist">Data Scientist</option>
            <option value="Product Manager">Product Manager</option>
          </select>
        </div>

        {/* File upload for resume (PDF only) */}
        <div className="input-group">
          <label>Upload Resume (PDF only):</label>
          <input
            type="file"
            accept=".pdf"
            onChange={(e) => setResumeFile(e.target.files[0])}
          />
        </div>

        {/* Submit button */}
        <button type="submit" disabled={loading}>
          {loading ? 'Generating...' : 'Start Interview'}
        </button>
      </form>
    </div>
  );
}

export default JobInfoComponent;
