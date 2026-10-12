import { useState } from 'react';
import { uploadResume, getResumeStatus } from '../api';

export default function ResumeUpload() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState('');
  const [resumeId, setResumeId] = useState('');
  const [status, setStatus] = useState('');

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      if (!selectedFile.name.endsWith('.pdf') && !selectedFile.name.endsWith('.docx')) {
        setMessage('❌ Only PDF and DOCX files are allowed');
        return;
      }
      setFile(selectedFile);
      setMessage('');
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setMessage('❌ Please select a file first');
      return;
    }

    setUploading(true);
    setMessage('⏳ Uploading and processing...');

    try {
      const response = await uploadResume(file);
      setResumeId(response.resume_id);
      setMessage(`✅ Upload successful! Resume ID: ${response.resume_id}`);
      setFile(null);
      
      // Reset file input
      const fileInput = document.getElementById('resume-file');
      if (fileInput) fileInput.value = '';
    } catch (error) {
      setMessage(`❌ Upload failed: ${error.message}`);
    } finally {
      setUploading(false);
    }
  };

  const handleCheckStatus = async () => {
    if (!resumeId) {
      setMessage('❌ Please enter a resume ID');
      return;
    }

    try {
      setMessage('⏳ Fetching status...');
      const response = await getResumeStatus(resumeId);
      setStatus(JSON.stringify(response, null, 2));
    } catch (error) {
      setMessage(`❌ Status check failed: ${error.message}`);
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '600px', margin: '0 auto' }}>
      <h1>Resume Upload</h1>
      
      {/* Upload Section */}
      <div style={{
        border: '2px solid #ccc',
        borderRadius: '8px',
        padding: '20px',
        marginBottom: '20px',
        backgroundColor: '#f9f9f9'
      }}>
        <h2>Upload Your Resume</h2>
        <p style={{ color: '#666', fontSize: '14px' }}>
          Supported formats: PDF, DOCX
        </p>
        
        <div style={{ marginBottom: '15px' }}>
          <input
            id="resume-file"
            type="file"
            accept=".pdf,.docx"
            onChange={handleFileSelect}
            disabled={uploading}
            style={{ cursor: uploading ? 'not-allowed' : 'pointer' }}
          />
          {file && <p style={{ color: '#0066cc', marginTop: '10px' }}>Selected: {file.name}</p>}
        </div>

        <button
          onClick={handleUpload}
          disabled={uploading || !file}
          style={{
            padding: '12px 24px',
            fontSize: '16px',
            backgroundColor: uploading || !file ? '#ccc' : '#0066cc',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: uploading || !file ? 'not-allowed' : 'pointer',
            fontWeight: 'bold'
          }}
        >
          {uploading ? 'Uploading...' : 'Upload Resume'}
        </button>

        {message && (
          <p style={{
            marginTop: '15px',
            padding: '10px',
            backgroundColor: message.includes('✅') ? '#e8f5e9' : 
                             message.includes('❌') ? '#ffebee' : '#e3f2fd',
            color: message.includes('✅') ? '#2e7d32' :
                   message.includes('❌') ? '#c62828' : '#1565c0',
            borderRadius: '4px',
            fontSize: '14px'
          }}>
            {message}
          </p>
        )}
      </div>

      {/* Status Check Section */}
      {resumeId && (
        <div style={{
          border: '2px solid #ccc',
          borderRadius: '8px',
          padding: '20px',
          backgroundColor: '#f9f9f9'
        }}>
          <h2>Check Processing Status</h2>
          
          <div style={{ marginBottom: '15px' }}>
            <label>Resume ID: </label>
            <input
              type="text"
              value={resumeId}
              onChange={(e) => setResumeId(e.target.value)}
              style={{ width: '100%', padding: '8px', marginTop: '5px' }}
            />
          </div>

          <button
            onClick={handleCheckStatus}
            style={{
              padding: '10px 20px',
              backgroundColor: '#4caf50',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontWeight: 'bold'
            }}
          >
            Check Status
          </button>

          {status && (
            <pre style={{
              marginTop: '15px',
              padding: '10px',
              backgroundColor: '#f0f0f0',
              borderRadius: '4px',
              fontSize: '12px',
              overflow: 'auto',
              maxHeight: '300px'
            }}>
              {status}
            </pre>
          )}
        </div>
      )}

      {/* API Endpoint Info */}
      <div style={{
        marginTop: '20px',
        padding: '15px',
        backgroundColor: '#f0f7ff',
        borderLeft: '4px solid #0066cc',
        fontSize: '12px'
      }}>
        <h3 style={{ margin: '0 0 10px 0' }}>API Endpoints Being Used:</h3>
        <p style={{ margin: '5px 0' }}>
          Upload: <code>POST /api/v1/file/upload-resume</code>
        </p>
        <p style={{ margin: '5px 0' }}>
          Status: <code>GET /api/v1/file/resume-status/&#123;resumeId&#125;</code>
        </p>
      </div>
    </div>
  );
}
