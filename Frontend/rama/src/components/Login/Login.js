import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import './Login.css';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await axios.post('http://localhost:8000/api/auth/login', {
        email,
        password
      });

      // Store JWT token in localStorage
      if (response.data.access_token) {
        localStorage.setItem('access_token', response.data.access_token);
        
        // Redirect to workspace page
        navigate('/workspace');
      } else {
        setError('Login failed. No token received.');
      }
    } catch (err) {
      // Handle error
      if (err.response) {
        setError(err.response.data.detail || 'Login failed. Please check your credentials.');
      } else if (err.request) {
        setError('Unable to connect to server. Please try again later.');
      } else {
        setError('An unexpected error occurred. Please try again.');
      }
      console.error('Login error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-form">
        <h2>RAMA Login</h2>
        <p className="login-subtitle">Research Automation Using MCP Server & Agentic AI</p>
        
        <form onSubmit={handleSubmit}>
          <div className="input-group">
            <label htmlFor="email">Email</label>
            <input 
              type="email" 
              id="email" 
              name="email" 
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required 
            />
          </div>
          
          <div className="input-group">
            <label htmlFor="password">Password</label>
            <input 
              type="password" 
              id="password" 
              name="password" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required 
            />
          </div>

          {error && <div className="error-message">{error}</div>}
          
          <button type="submit" className="signin-btn" disabled={loading}>
            {loading ? 'Signing In...' : 'Sign In'}
          </button>
  </form>
  <p style={{marginTop:'12px', color:'#A0A0B0'}}>New here? <Link to="/register" style={{color:'#6B48FF'}}>Create an account</Link></p>
      </div>
    </div>
  );
};

export default Login;
