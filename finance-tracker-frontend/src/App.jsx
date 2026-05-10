import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Transactions from './pages/Transactions';
import Categories from './pages/Categories';
import AIAssistantChat from './components/AIAssistantChat';
import FloatingChat from "./components/FloatingChat";

function App() {
  return (
    <Router>

      {/* Routes */}
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/transactions" element={<Transactions />} />
        <Route path="/categories" element={<Categories />} />
        <Route path="/ai-assistant" element={<AIAssistantChat />} />
      </Routes>
      {/* Floating AI chat visible on every page */}
      <FloatingChat />
    </Router>
  );
}

export default App;
