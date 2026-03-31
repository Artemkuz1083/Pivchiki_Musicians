import React, { useState } from 'react';
import { authService } from '../../api/AuthService';
import { useNavigate } from 'react-router';

export const AuthRegistration = () => {
  const [login, setLogin] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await authService.register({ login, password });
      alert('Аккаунт создан! Теперь заполни профиль.');
      navigate('/registration'); 
    } catch (error) {
      console.error('Ошибка регистрации:', error);
    }
  };

  return (
    <div className="auth-container">
      <h2>Регистрация аккаунта</h2>
      <form onSubmit={handleRegister}>
        <input 
          value={login} 
          onChange={(e) => setLogin(e.target.value)} 
          placeholder="Логин" 
          required 
        />
        <input 
          type="password" 
          value={password} 
          onChange={(e) => setPassword(e.target.value)} 
          placeholder="Пароль" 
          required 
        />
        <button type="submit">Создать аккаунт</button>
      </form>
    </div>
  );
};