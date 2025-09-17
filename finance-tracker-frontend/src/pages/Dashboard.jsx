import React, { useEffect, useState } from 'react';
import api from '../api/axios';

function Dashboard() {
    const [balance, setBalance] = useState(null);
    const [summary, setSummary] = useState([]);
    const [error, setError] = useState('');

    const token = localStorage.getItem('access');

    useEffect(() => {
        const fetchData = async () => {
            try {
                const balanceRes = await api.get('finance/balance/', {
                    headers: { Authorization: `Bearer ${token}` }
                });
                setBalance(balanceRes.data);

                const summaryRes = await api.get('finance/summary/monthly/', {
                    headers: { Authorization: `Bearer ${token}` }
                });
                setSummary(summaryRes.data);
            } catch (err) {
                setError('Failed to load data');
            }
        };

        fetchData();
    }, [token]);

    return (
        <div className="container mt-4">
            <h2>Dashboard</h2>
            {error && <p className="text-danger">{error}</p>}

            {balance && (
                <div className="mb-4">
                    <p><strong>Total Income:</strong> ₹{balance.total_income}</p>
                    <p><strong>Total Expense:</strong> ₹{balance.total_expense}</p>
                    <p><strong>Balance:</strong> ₹{balance.balance}</p>
                </div>
            )}

            <h4>Monthly Summary</h4>
            <table className="table table-bordered mt-3">
                <thead>
                    <tr>
                        <th>Month</th>
                        <th>Income (₹)</th>
                        <th>Expense (₹)</th>
                    </tr>
                </thead>
                <tbody>
                    {summary.map((item) => (
                        <tr key={item.month}>
                            <td>{item.month}</td>
                            <td>{item.income}</td>
                            <td>{item.expense}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

export default Dashboard;
