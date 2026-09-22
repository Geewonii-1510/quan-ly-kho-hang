/**
 * Auth Context - Ngữ cảnh xác thực
 * Manages authentication state across the app
 */

import { createContext, useContext, useState, useEffect } from 'react';
import api from '../api/client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check saved auth / Kiểm tra xác thực đã lưu
    const token = localStorage.getItem('wms_token');
    const savedUser = localStorage.getItem('wms_user');

    if (token && savedUser) {
      try {
        setUser(JSON.parse(savedUser));
      } catch {
        localStorage.removeItem('wms_token');
        localStorage.removeItem('wms_user');
      }
    }
    setLoading(false);
  }, []);

  const login = async (username, password) => {
    const response = await api.post('/api/auth/login', { username, password });
    const { access_token, user: userData } = response.data;

    localStorage.setItem('wms_token', access_token);
    localStorage.setItem('wms_user', JSON.stringify(userData));
    setUser(userData);

    return userData;
  };

  const logout = () => {
    localStorage.removeItem('wms_token');
    localStorage.removeItem('wms_user');
    setUser(null);
  };

  const value = {
    user,
    login,
    logout,
    loading,
    isAuthenticated: !!user,
    isAdmin: user?.role?.name === 'admin',
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}

export default AuthContext;
