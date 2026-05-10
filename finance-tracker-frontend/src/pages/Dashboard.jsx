import React, { useEffect, useState } from 'react';
import api from '../api/axios';
import { useNavigate } from 'react-router-dom';
import Transactions from './Transactions';

function Dashboard() {
    const [balance, setBalance] = useState(null);
    const [summary, setSummary] = useState([]);
    const [error, setError] = useState('');
    const navigate = useNavigate();

    useEffect(() => {
        const token = localStorage.getItem('access');

        if (!token) {
            navigate('/');
            return;
        }

        const fetchData = async () => {
            try {
                const balanceRes = await api.get('finance/transactions/balance/', {
                    headers: { Authorization: `Bearer ${token}` }
                });
                setBalance(balanceRes.data);

                const summaryRes = await api.get('finance/transactions/monthly_summary/', {
                    headers: { Authorization: `Bearer ${token}` }
                });
                setSummary(summaryRes.data);
            } catch (err) {
                setError('Failed to load data');
                // If unauthorized, redirect to login
                if (err.response?.status === 401) {
                    localStorage.removeItem('access');
                    localStorage.removeItem('refresh');
                    navigate('/');
                }
            }
        };

        fetchData();
    }, [navigate]);

    const handleLogout = () => {
        localStorage.removeItem('access');
        localStorage.removeItem('refresh');
        navigate('/');
    };

    return (
        <div className="dashboard-container w-100 min-vh-100 bg-light py-4">
            <div className="container-fluid">
                <div className="row">
                    <div className="col-12">
                        {/* Top Header */}
                        <div className="d-flex justify-content-between align-items-center bg-white p-3 rounded shadow-sm mb-4">
                            <h2 className="mb-0 fw-bold text-primary">
                                <span className="me-2">📊</span>
                                Personal Finance Dashboard
                            </h2>
                            <button
                                className="btn btn-outline-primary btn-sm px-4"
                                onClick={() => navigate('/transactions')}
                            >
                                Transactions
                            </button>
                            <button
                                className="btn btn-outline-primary btn-sm px-4"
                                onClick={() => navigate('/categories')}
                            >
                                Manage Categories
                            </button>
                            <button
                                className="btn btn-outline-danger btn-sm px-4"
                                onClick={handleLogout}
                            >
                                Logout
                            </button>
                        </div>

                        {/* Error Alert */}
                        {error && (
                            <div className="alert alert-danger alert-dismissible fade show mb-4" role="alert">
                                <strong>Error!</strong> {error}
                            </div>
                        )}

                        {/* Balance Section */}
                        {balance && (
                            <div className="row g-3 mb-4">
                                <div className="col-12 col-sm-6 col-lg-4">
                                    <div className="card h-100 shadow-sm border-0 border-start border-success border-4">
                                        <div className="card-body text-center py-4">
                                            <h6 className="card-subtitle mb-2 text-muted text-uppercase">Total Income</h6>
                                            <h2 className="card-title text-success fw-bold mb-0">
                                                ₹{balance.total_income.toLocaleString()}
                                            </h2>
                                        </div>
                                    </div>
                                </div>
                                <div className="col-12 col-sm-6 col-lg-4">
                                    <div className="card h-100 shadow-sm border-0 border-start border-danger border-4">
                                        <div className="card-body text-center py-4">
                                            <h6 className="card-subtitle mb-2 text-muted text-uppercase">Total Expense</h6>
                                            <h2 className="card-title text-danger fw-bold mb-0">
                                                ₹{balance.total_expense.toLocaleString()}
                                            </h2>
                                        </div>
                                    </div>
                                </div>
                                <div className="col-12 col-sm-12 col-lg-4">
                                    <div className="card h-100 shadow-sm border-0 border-start border-primary border-4">
                                        <div className="card-body text-center py-4">
                                            <h6 className="card-subtitle mb-2 text-muted text-uppercase">Net Balance</h6>
                                            <h2 className="card-title text-primary fw-bold mb-0">
                                                ₹{balance.balance.toLocaleString()}
                                            </h2>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Monthly Summary */}
                        <div className="card shadow-sm border-0">
                            <div className="card-header bg-white border-bottom py-3">
                                <h4 className="mb-0 text-secondary">
                                    <span className="me-2">📅</span>
                                    Monthly Summary
                                </h4>
                            </div>
                            <div className="card-body p-0">
                                <div className="table-responsive">
                                    <table className="table table-hover mb-0">
                                        <thead className="table-light">
                                            <tr>
                                                <th scope="col" className="text-center py-3">Month</th>
                                                <th scope="col" className="text-center py-3">Income (₹)</th>
                                                <th scope="col" className="text-center py-3">Expense (₹)</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {summary.length > 0 ? (
                                                summary.map((item) => (
                                                    <tr key={item.month}>
                                                        <td className="text-center py-3 fw-semibold">{item.month}</td>
                                                        <td className="text-center py-3 text-success">
                                                            {item.income.toLocaleString()}
                                                        </td>
                                                        <td className="text-center py-3 text-danger">
                                                            {item.expense.toLocaleString()}
                                                        </td>
                                                    </tr>
                                                ))
                                            ) : (
                                                <tr>
                                                    <td colSpan="3" className="text-center py-5 text-muted">
                                                        No data available
                                                    </td>
                                                </tr>
                                            )}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Dashboard;