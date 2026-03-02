import React from 'react';
import { Routes, Route, BrowserRouter } from "react-router-dom";
import AuthPage from './pages/authPage';
import Dashboard from './pages/dashboardPage';

const App = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<AuthPage />} />
        <Route path='/dashboard' element={<Dashboard />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
