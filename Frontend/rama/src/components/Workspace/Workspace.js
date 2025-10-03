import React, { useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import './Workspace.css';

const Workspace = () => {
  const navigate = useNavigate();

  useEffect(() => {
    // Check if user is authenticated
    const token = localStorage.getItem('access_token');
    if (!token) {
      navigate('/');
    }
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    navigate('/');
  };

  return (
    <div className="workspace-container">
      <header className="workspace-header">
        <h1>RAMA Neural Interface</h1>
        <button onClick={handleLogout} className="logout-btn">Logout</button>
      </header>
      
      <div className="workspace-content">
        <div className="welcome-section">
          <h2>Welcome to RAMA</h2>
          <p>Research Automation Using MCP Server & Agentic AI</p>
          
          <div className="action-buttons">
            <Link to="/research" className="research-btn">
              🔬 Start Research Session
            </Link>
          </div>
          
          <div className="stats-grid">
            <div className="stat-card">
              <h3>Papers Processed</h3>
              <p className="stat-number">1,273</p>
              <span className="stat-label">Documents Synthesized</span>
            </div>
            <div className="stat-card">
              <h3>Hypotheses Generated</h3>
              <p className="stat-number">43</p>
              <span className="stat-label">Novel Ideas Formulated</span>
            </div>
            <div className="stat-card">
              <h3>Synthesis Confidence</h3>
              <p className="stat-number">94%</p>
              <span className="stat-label">Accuracy & Cohesion</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Workspace;
