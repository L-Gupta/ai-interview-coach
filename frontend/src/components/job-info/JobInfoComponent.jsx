import React, { useState } from 'react';
import './job-info.css';
import { useNavigate } from 'react-router-dom';
import Footer from '../footer/FooterComponent';

function JobInfoComponent() {
  const [selectedRole, setSelectedRole] = useState('');
  const [resumeFile, setResumeFile] = useState(null);
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  // Function to sanitize name for use as resume_id
  const generateResumeId = (name) => {
    return name
      .trim()
      .toLowerCase()
      .replace(/\s+/g, '_')          // replace spaces with underscores
      .replace(/[^a-z_]/g, '');      // remove numbers and symbols
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedRole || !resumeFile || !name.trim()) {
      alert("Please enter your name, select a role, and upload your resume.");
      return;
    }

    setLoading(true);
    try {
      const resumeId = generateResumeId(name);
      const formData = new FormData();
      formData.append('file', resumeFile);
      formData.append('resume_id', resumeId); // send name with underscores as resume_id

      const uploadRes = await fetch('http://127.0.0.1:8000/file/upload-resume', {
        method: 'POST',
        body: formData,
      });

      if (!uploadRes.ok) throw new Error('Resume upload failed');
      console.log("✅ Resume uploaded with ID:", resumeId);

      navigate('/interview', {
        state: {
          name: name.trim(),
          role: selectedRole,
          resumeId: resumeId
        }
      });

    } catch (error) {
      alert('Error starting interview. Check console.');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="job-info-container">
      <h2>Please enter your name, choose your role and upload your resume</h2>
      <form onSubmit={handleSubmit}>
        <div className="input-group">
          <label>Enter Your Name:</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g. John Doe"
          />
        </div>

        <div className="input-group">
          <label>Select Job Role:</label>
          <select value={selectedRole} onChange={(e) => setSelectedRole(e.target.value)}>
            <option value="" disabled>Select a role</option>
            <option value="Software Engineer">Software Engineer</option>
            <option value="Data Scientist">Data Scientist</option>
            <option value="Product Manager">Product Manager</option>
            <option value="Computer Engineer">Computer Engineer</option>
            <option value="Mechanical Engineer">Mechanical Engineer</option>
            <option value="Company Secretary">Company Secretary</option>
          </select>
        </div>

        <div className="input-group">
          <label>Upload Resume (PDF only):</label>
          <input
            type="file"
            accept=".pdf"
            onChange={(e) => setResumeFile(e.target.files[0])}
          />
        </div>

        <button type="submit" disabled={loading}>
          {loading ? 'Processing...' : 'Start Interview'}
        </button>
      </form>
      <Footer />
    </div>
  );
}

export default JobInfoComponent;
