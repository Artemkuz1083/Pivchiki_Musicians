import { useState } from 'react';
import { useAuth } from '../../context/AuthContext';

export function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login } = useAuth();

  const handleFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      // Стучимся в твою ручку из Swagger
      const response = await fetch('https://твой-апи.рф/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (data.token) {
        login(data.token); // Сохраняем токен в наш контекст
        alert('Успешный вход!');
      }
    } catch (error) {
      console.error('Ошибка входа:', error);
    }
  };

  return (
    <form onSubmit={handleFormSubmit} className="p-4 flex flex-col gap-4">
      <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" className="border p-2 rounded" />
      <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Пароль" className="border p-2 rounded" />
      <button type="submit" className="bg-[#60519B] text-white p-3 rounded-xl">Войти</button>
    </form>
  );
}