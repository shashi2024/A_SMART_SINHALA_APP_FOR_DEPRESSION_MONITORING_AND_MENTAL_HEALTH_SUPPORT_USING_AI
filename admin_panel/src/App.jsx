import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import UserProfile from './pages/UserProfile';
import Alerts from './pages/Alerts';
import DigitalTwinView from './pages/DigitalTwinView';
import PatientsRiskLevel from './pages/PatientsRiskLevel';
import PrivateRoute from './components/PrivateRoute';
import Layout from './components/Layout';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Default route - redirects to login or dashboard based on auth */}
          <Route path="/" element={<Navigate to="/login" replace />} />
          
          {/* Login route - accessible without authentication */}
          <Route path="/login" element={<Login />} />
          
          {/* All other routes require authentication */}
          <Route
            path="/*"
            element={
              <PrivateRoute>
                <Layout />
              </PrivateRoute>
            }
          >
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="patients-risk" element={<PatientsRiskLevel />} />
            <Route path="users/:userId" element={<UserProfile />} />
            <Route path="alerts" element={<Alerts />} />
            <Route path="connect" element={<div>Connect Page</div>} />
            <Route path="location-track" element={<div>Location Track Page</div>} />
            <Route path="digital-twin" element={<div>Digital Twin Page</div>} />
            <Route path="digital-twin/:userId" element={<DigitalTwinView />} />
            <Route path="settings" element={<div>Settings Page</div>} />
            {/* Catch-all for protected routes */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Route>
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;

