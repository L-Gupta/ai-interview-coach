import React, { useState } from 'react';
import './job-info.css';
import { useNavigate } from 'react-router-dom';
import Footer from '../footer/FooterComponent';

function JobInfoComponent({}) {
  const [selectedRole, setSelectedRole] = useState('');
  const [resumeFile, setResumeFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedRole || !resumeFile) {
      alert("Please select a role and upload your resume.");
      return;
    }

    setLoading(true);
    try {
      // ✅ 1. Upload resume
      const formData = new FormData();
      formData.append('file', resumeFile);

      const uploadRes = await fetch('http://127.0.0.1:8000/file/upload-resume', {
        method: 'POST',
        body: formData,
      });

      if (!uploadRes.ok) throw new Error('Resume upload failed');
      const uploadData = await uploadRes.json();
      const resumeId = uploadData.resume_id;
      console.log("✅ Resume uploaded, ID:", resumeId);

      // ✅ 2. Navigate to interview with state
      navigate('/interview', {
        state: {
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
      <h2>Step 1: Choose Role & Upload Resume</h2>
      <form onSubmit={handleSubmit}>
        <div className="input-group">
          <label>Select Job Role:</label>
          <select value={selectedRole} onChange={(e) => setSelectedRole(e.target.value)}>
            <option value="" disabled>Select a role</option>
            <option value="Software Engineer">Software Engineer</option>
            <option value="Data Scientist">Data Scientist</option>
            <option value="Product Manager">Product Manager</option>
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
