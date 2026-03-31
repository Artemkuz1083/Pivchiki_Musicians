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

  logout() {
    localStorage.removeItem('authToken');
  },

  isAuthenticated(): boolean {
    return !!localStorage.getItem('authToken');
  },
};