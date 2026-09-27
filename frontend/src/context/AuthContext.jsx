import React, { createContext, useContext, useState, useEffect } from 'react';
import { loginUser, registerUser, getCurrentUser, deleteUserAccount } from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('vizmind_access_token');
      if (token) {
        try {
          const userData = await getCurrentUser();
          setUser(userData);
        } catch (err) {
          console.warn('Failed to verify stored authentication session:', err);
          localStorage.removeItem('vizmind_access_token');
          localStorage.removeItem('vizmind_refresh_token');
          setUser(null);
        }
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  const login = async (email, password) => {
    const tokens = await loginUser(email, password);
    localStorage.setItem('vizmind_access_token', tokens.access_token);
    localStorage.setItem('vizmind_refresh_token', tokens.refresh_token);
    const userData = await getCurrentUser();
    setUser(userData);
    return userData;
  };

  const register = async (email, password) => {
    const response = await registerUser(email, password);
    await login(email, password);
    return response;
  };

  const logout = () => {
    localStorage.removeItem('vizmind_access_token');
    localStorage.removeItem('vizmind_refresh_token');
    setUser(null);
  };

  const deleteAccount = async () => {
    await deleteUserAccount();
    logout();
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        register,
        logout,
        deleteAccount,
        isAuthenticated: !!user,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
