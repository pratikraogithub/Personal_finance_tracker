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
            const response = await api.post('token/', {
                username,
                password
            });

            localStorage.setItem('access', response.data.access);
            localStorage.setItem('refresh', response.data.refresh);

            navigate('/dashboard');
        } catch (err) {
            setError('Invalid username or password');
        }
    };

    return (
        <div className="container" style={{ maxWidth: 400, marginTop: 80 }}>
            <h2 className="mb-4">Login</h2>
            <form onSubmit={handleLogin}>
                <div className="mb-3">
                    <input type="text" placeholder="Username" className="form-control"
                        value={username} onChange={(e) => setUsername(e.target.value)} required />
                </div>
                <div className="mb-3">
                    <input type="password" placeholder="Password" className="form-control"
                        value={password} onChange={(e) => setPassword(e.target.value)} required />
                </div>
                {error && <p className="text-danger">{error}</p>}
                <button className="btn btn-primary w-100">Login</button>
            </form>
        </div>
    );
}

export default Login;
