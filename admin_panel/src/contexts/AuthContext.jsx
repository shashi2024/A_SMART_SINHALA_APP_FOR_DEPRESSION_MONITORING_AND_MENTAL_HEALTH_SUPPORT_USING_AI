import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext();

export function useAuth() {
  return useContext(AuthContext);
}

export function AuthProvider({ children }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const checkAdminStatus = async () => {
    try {
      const response = await api.get('/auth/me');
      const userInfo = response.data;
      // Allow both admin and sub-admin access
      const hasAccess = userInfo.is_admin === true || userInfo.is_sub_admin === true;
      setIsAdmin(hasAccess);
      setUser(userInfo); // Store user info
      return hasAccess;
    } catch (error) {
      console.error('Failed to check admin status:', error);
      setIsAdmin(false);
      setUser(null);
      return false;
    }
  };

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem('token');
    if (token) {
      api.setToken(token);
      // Verify token is still valid and user is admin/sub-admin
      checkAdminStatus()
        .then((hasAccess) => {
          if (hasAccess) {
            setIsAuthenticated(true);
          } else {
            // Token exists but user is not admin/sub-admin or token is invalid
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
    // Check admin/sub-admin status after login
    const hasAccess = await checkAdminStatus();
    if (!hasAccess) {
      throw new Error('Access denied: Admin or sub-admin privileges required');
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    api.setToken(null);
    setIsAuthenticated(false);
    setUser(null);
    setIsAdmin(false);
  };

  const value = {
    isAuthenticated,
    isAdmin,
    user,
    loading,
    login,
    logout,
    checkAdminStatus, // Export to refresh user info
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
}

