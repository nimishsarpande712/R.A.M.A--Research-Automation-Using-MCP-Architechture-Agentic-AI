import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import '../Login/Login.css';

const Register = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (password !== confirm) {
      setError('Passwords do not match');
      return;
    }

    setLoading(true);
    try {
      await axios.post('http://localhost:8000/api/auth/register', { email, password });
      setSuccess('Account created! You can sign in now.');
      setTimeout(() => navigate('/'), 1000);
    } catch (err) {
      if (err.response) {
        setError(err.response.data.detail || 'Registration failed.');
      } else if (err.request) {
        setError('Unable to connect to server. Please try again later.');
      } else {
        setError('An unexpected error occurred. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-form">
        <h2>Create Account</h2>
        <p className="login-subtitle">Join RAMA to explore agentic research tools</p>
        <form onSubmit={handleSubmit}>
          <div className="input-group">
            <label htmlFor="email">Email</label>
            <input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </div>
          <div className="input-group">
            <label htmlFor="password">Password</label>
            <input id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </div>
          <div className="input-group">
            <label htmlFor="confirm">Confirm Password</label>
            <input id="confirm" type="password" value={confirm} onChange={(e) => setConfirm(e.target.value)} required />
          </div>
          {error && <div className="error-message">{error}</div>}
          {success && <div className="success-message" style={{background:'rgba(0,201,167,0.1)',color:'#00C9A7',border:'1px solid #00C9A7',padding:'12px',borderRadius:'5px',marginBottom:'20px'}}> {success} </div>}
          <button type="submit" className="signin-btn" disabled={loading}>{loading ? 'Creating...' : 'Create Account'}</button>
        </form>
        <p style={{marginTop:'12px', color:'#A0A0B0'}}>Already have an account? <Link to="/" style={{color:'#6B48FF'}}>Sign in</Link></p>
      </div>
    </div>
  );
};

export default Register;
