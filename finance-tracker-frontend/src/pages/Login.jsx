// Login.jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/axios';

function Login() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleLogin = async (e) => {
        e.preventDefault();
        setError('');
        try {
            const response = await api.post('token/', { username, password });
            localStorage.setItem('access', response.data.access);
            localStorage.setItem('refresh', response.data.refresh);
            navigate('/dashboard');
        } catch (err) {
            setError('Invalid username or password');
        }
    };

    return (
        <div
            style={{
                position: 'fixed',
                top: 0, left: 0, right: 0, bottom: 0,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                // background: '#f8f9fA',     // subtle page bg
                background: 'linear-gradient(135deg, #007bff, #00c6ff)',
                zIndex: 1050                // sit on top of layout if needed
            }}
        >
            <div className="card shadow-lg border-0" style={{ width: '100%', maxWidth: 420, margin: '0 1rem', borderRadius: '1rem' }}>
                <div className="card-body p-4">
                    <h3 className="text-center mb-4 text-primary">Login</h3>

                    <form onSubmit={handleLogin}>
                        <div className="mb-3">
                            <label className="form-label">Username</label>
                            <input
                                type="text"
                                placeholder="Enter your username"
                                className="form-control"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                required
                            />
                        </div>

                        <div className="mb-3">
                            <label className="form-label">Password</label>
                            <input
                                type="password"
                                placeholder="Enter your password"
                                className="form-control"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                            />
                        </div>

                        {error && <div className="alert alert-danger text-center py-2">{error}</div>}

                        <button type="submit" className="btn btn-primary w-100">Login</button>
                    </form>
                    <div className="d-flex justify-content-between align-items-center mb-3 mt-3">
                        <div className="form-check">
                            <input className="form-check-input" type="checkbox" id="rememberMe" />
                            <label className="form-check-label" htmlFor="rememberMe">Remember me</label>
                        </div>
                        <a href="#" className="text-decoration-none">Forgot password?</a>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Login;
