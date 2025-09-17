// src/pages/Transactions.jsx
import React, { useEffect, useState } from 'react';
import api from '../api/axios';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import TransactionChart from '../components/TransactionChart';

const Transactions = () => {
    const [filterType, setFilterType] = useState('');
    const [sortOrder, setSortOrder] = useState('newest');
    const [transactions, setTransactions] = useState([]);
    const [categories, setCategories] = useState([]);
    const [loading, setLoading] = useState(true);
    const { register, handleSubmit, reset } = useForm();
    const navigate = useNavigate();

    useEffect(() => {
        const token = localStorage.getItem('access');
        if (!token) {
            navigate('/login');
            return;
        }

        api.get('finance/transactions/', {
            headers: { Authorization: `Bearer ${token}` },
        })
            .then((res) => {
                setTransactions(res.data);
                setLoading(false);
            })
            .catch((err) => {
                console.error('Fetch error:', err);
                setLoading(false);
            });

        api.get('finance/categories/', {
            headers: { Authorization: `Bearer ${token}` },
        })
            .then((res) => {
                setCategories(res.data);
            })
            .catch((err) => {
                console.error('Categories fetch error:', err);
            });
    }, [navigate]);

    const onSubmit = async (data) => {
        const token = localStorage.getItem('access');

        const payload = {
            ...data,
            type: data.type.toUpperCase(),
            category_id: parseInt(data.category),
            amount: parseFloat(data.amount),
        };

        try {
            const response = await api.post('finance/transactions/', payload, {
                headers: { Authorization: `Bearer ${token}` },
            });
            setTransactions([response.data, ...transactions]);
            reset();
        } catch (err) {
            console.error('Post error:', err.response?.data || err.message);
        }
    };

    const filteredTransactions = transactions
        .filter((tx) => (filterType ? tx.type === filterType : true))
        .sort((a, b) => {
            if (sortOrder === 'newest') return new Date(b.date) - new Date(a.date);
            if (sortOrder === 'oldest') return new Date(a.date) - new Date(b.date);
            if (sortOrder === 'high') return b.amount - a.amount;
            if (sortOrder === 'low') return a.amount - b.amount;
            return 0;
        });
    const incomeTotal = filteredTransactions
        .filter(tx => tx.type === 'INCOME')
        .reduce((sum, tx) => sum + parseFloat(tx.amount), 0);

    const expenseTotal = filteredTransactions
        .filter(tx => tx.type === 'EXPENSE')
        .reduce((sum, tx) => sum + parseFloat(tx.amount), 0);

    const balance = incomeTotal - expenseTotal;


    return (
        <div className="container mt-4">
            <h2>My Transactions</h2>
            <div className="row mb-4">
                <div className="col-md-4">
                    <div className="card border-success">
                        <div className="card-body text-success">
                            <h5 className="card-title">Total Income</h5>
                            <p className="card-text">₹{incomeTotal.toFixed(2)}</p>
                        </div>
                    </div>
                </div>
                <div className="col-md-4">
                    <div className="card border-danger">
                        <div className="card-body text-danger">
                            <h5 className="card-title">Total Expense</h5>
                            <p className="card-text">₹{expenseTotal.toFixed(2)}</p>
                        </div>
                    </div>
                </div>
                <div className="col-md-4">
                    <div className="card border-primary">
                        <div className="card-body text-primary">
                            <h5 className="card-title">Balance</h5>
                            <p className="card-text">₹{balance.toFixed(2)}</p>
                        </div>
                    </div>
                </div>
            </div>


            {/* Form */}
            <form onSubmit={handleSubmit(onSubmit)} className="mb-4 border p-3 rounded">
                <div className="row g-3">
                    <div className="col-md-3">
                        <select className="form-select" {...register('type')} required>
                            <option value="">Type</option>
                            <option value="income">Income</option>
                            <option value="expense">Expense</option>
                        </select>
                    </div>

                    <div className="col-md-3">
                        <input
                            className="form-control"
                            type="number"
                            step="0.01"
                            placeholder="Amount"
                            {...register('amount')}
                            required
                        />
                    </div>

                    <div className="col-md-3">
                        <select className="form-select" {...register('category')} required>
                            <option value="">Select Category</option>
                            {categories.map((cat) => (
                                <option key={cat.id} value={cat.id}>
                                    {cat.name}
                                </option>
                            ))}
                        </select>
                    </div>

                    <div className="col-md-3">
                        <input className="form-control" type="date" {...register('date')} required />
                    </div>

                    <div className="col-12 mt-2">
                        <input
                            className="form-control"
                            type="text"
                            placeholder="Description"
                            {...register('description')}
                        />
                    </div>
                </div>

                <button className="btn btn-primary mt-3" type="submit">
                    Add Transaction
                </button>
            </form>



            {/* Filter & Sort Controls */}
            <div className="d-flex gap-3 mb-3">
                <select className="form-select w-auto" value={filterType} onChange={(e) => setFilterType(e.target.value)}>
                    <option value="">All Types</option>
                    <option value="INCOME">Income</option>
                    <option value="EXPENSE">Expense</option>
                </select>

                <select className="form-select w-auto" value={sortOrder} onChange={(e) => setSortOrder(e.target.value)}>
                    <option value="newest">Newest First</option>
                    <option value="oldest">Oldest First</option>
                    <option value="high">Amount: High to Low</option>
                    <option value="low">Amount: Low to High</option>
                </select>
            </div>
            <TransactionChart data={filteredTransactions} />
            {/* Transactions List */}
            {loading ? (
                <p>Loading...</p>
            ) : filteredTransactions.length === 0 ? (
                <p>No transactions found.</p>
            ) : (
                <ul className="list-group">
                    {filteredTransactions.map((tx) => (
                        <li key={tx.id} className="list-group-item">
                            <strong>{tx.type}</strong> — ₹{tx.amount}
                            <br />
                            <small>{tx.category?.name || 'No category'} | {tx.date}</small>
                            <br />
                            <em>{tx.description}</em>
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
};

export default Transactions;
