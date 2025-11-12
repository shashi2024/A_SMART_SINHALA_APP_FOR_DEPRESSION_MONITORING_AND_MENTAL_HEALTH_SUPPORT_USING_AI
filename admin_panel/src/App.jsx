import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import UserProfile from './pages/UserProfile';
import Alerts from './pages/Alerts';
import DigitalTwinView from './pages/DigitalTwinView';
import PrivateRoute from './components/PrivateRoute';
import Layout from './components/Layout';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/"
            element={
              <PrivateRoute>
                <Layout />
              </PrivateRoute>
            }
          >
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="users/:userId" element={<UserProfile />} />
            <Route path="alerts" element={<Alerts />} />
            <Route path="digital-twin/:userId" element={<DigitalTwinView />} />
          </Route>
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;

