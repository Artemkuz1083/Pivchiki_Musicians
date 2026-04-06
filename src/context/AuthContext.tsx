import React, { createContext, useContext, useState, useEffect } from 'react';

interface AuthContextType {
  isLoggedIn: boolean;
  token: string | null;
  login: (token: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(localStorage.getItem('api_token'));

  const login = (newToken: string) => {
    localStorage.setItem('api_token', newToken);
    setToken(newToken);
  };

  const logout = () => {
    localStorage.removeItem('api_token');
    setToken(null);
  };

  const isLoggedIn = !!token; // превращаем наличие токена в true/false

  return (
    <AuthContext.Provider value={{ isLoggedIn, token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

// Хук для удобного использования в компонентах
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};