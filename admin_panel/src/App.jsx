import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import UserProfile from './pages/UserProfile';
import AdminProfile from './pages/AdminProfile';
import Alerts from './pages/Alerts';
import DigitalTwin from './pages/DigitalTwin';
import DigitalTwinView from './pages/DigitalTwinView';
import PatientsRiskLevel from './pages/PatientsRiskLevel';
import Notifications from './pages/Notifications';
import Reports from './pages/Reports';
import Connect from './pages/Connect';
import LocationTracking from './pages/LocationTracking';
import Settings from './pages/Settings';
import UserManagement from './pages/UserManagement';
import TwitterAnalysis from './pages/TwitterAnalysis';

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
            <Route path="notifications" element={<Notifications />} />
            <Route path="reports" element={<Reports />} />
            <Route path="admin-profile" element={<AdminProfile />} />
            <Route path="connect" element={<Connect />} />
            <Route path="location-track" element={<LocationTracking />} />
            <Route path="digital-twin" element={<DigitalTwin />} />
            <Route path="digital-twin/:userId" element={<DigitalTwinView />} />
            <Route path="user-management" element={<UserManagement />} />
            <Route path="twitter-analysis" element={<TwitterAnalysis />} />

            <Route path="settings" element={<Settings />} />
            {/* Catch-all for protected routes */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Route>
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;

