import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext();

export function useAuth() {
  return useContext(AuthContext);
}

export function AuthProvider({ children }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);
  const [loading, setLoading] = useState(true);

  const checkAdminStatus = async () => {
    try {
      const response = await api.get('/auth/me');
      const userInfo = response.data;
      setIsAdmin(userInfo.is_admin === true);
      return userInfo.is_admin === true;
    } catch (error) {
      console.error('Failed to check admin status:', error);
      setIsAdmin(false);
      return false;
    }
  };

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem('token');
    if (token) {
      api.setToken(token);
      // Verify token is still valid and user is admin
      checkAdminStatus()
        .then((isAdmin) => {
          if (isAdmin) {
            setIsAuthenticated(true);
          } else {
            // Token exists but user is not admin or token is invalid
            localStorage.removeItem('token');
            api.setToken(null);
            setIsAuthenticated(false);
          }
        })
        .catch(() => {
          // Token validation failed
          localStorage.removeItem('token');
          api.setToken(null);
          setIsAuthenticated(false);
        })
        .finally(() => {
          setLoading(false);
        });
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (username, password) => {
    const response = await api.post('/auth/login', { username, password });
    const token = response.data.access_token;
    localStorage.setItem('token', token);
    api.setToken(token);
    setIsAuthenticated(true);
    // Check admin status after login
    const adminStatus = await checkAdminStatus();
    if (!adminStatus) {
      throw new Error('Access denied: Admin privileges required');
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    api.setToken(null);
    setIsAuthenticated(false);
  };

  const value = {
    isAuthenticated,
    isAdmin,
    loading,
    login,
    logout,
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
}

