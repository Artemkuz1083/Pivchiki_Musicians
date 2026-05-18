// api/authService.ts
import { api } from './instance'; 
import { AuthRequestDto, AuthResponseDto } from '../app/types';

export const authService = {
  async login(credentials: AuthRequestDto): Promise<AuthResponseDto> {
    const { data } = await api.post<AuthResponseDto>('/auth/login', credentials);
    if (data.token) {
      localStorage.setItem('authToken', data.token);
    }
    return data; 
  },

  async register(credentials: AuthRequestDto): Promise<AuthResponseDto> {
    const { data } = await api.post<AuthResponseDto>('/auth/registry', credentials);
    if (data.token) {
      localStorage.setItem('authToken', data.token);
    }
    return data;
  },

  //Обновление Access-токена через HttpOnly-куку
  async refresh(): Promise<string | null> {
    try {
      // Отправляем пустой POST-запрос. Кука прикрепится автоматически благодаря withCredentials
      const { data } = await api.post<{ token?: string; access_token?: string }>(
        '/auth/refresh', 
        {}, 
        { withCredentials: true } // КРИТИЧЕСКИ ВАЖНО дляHttpOnly кук!
      );

      // Проверяем, как бэкенд назвал токен (token или access_token)
      const newToken = data.token || data.access_token;

      if (newToken) {
        localStorage.setItem('authToken', newToken);
        return newToken;
      }
      return null;
    } catch (error) {
      console.error('Не удалось обновить токен (сессия истекла):', error);
      // Если рефреш-токен невалиден, чистим всё, чтобы юзер залогинился заново
      this.logout();
      return null;
    }
  },

  logout() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('my_group_id'); // Подчищаем ID группы при выходе
  },

  isAuthenticated(): boolean {
    return !!localStorage.getItem('authToken');
  },
};