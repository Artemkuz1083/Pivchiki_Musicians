import { api } from './instance';
import { UserProfile, CreateProfileDto } from '../app/types';

export const profileService = {
  // GET /api/v1/profile
  async getMyProfile(): Promise<UserProfile> {
    const { data } = await api.get<UserProfile>('/profile');
    return data;
  },

  // POST /api/v1/profile
  async createProfile(profileData: CreateProfileDto): Promise<UserProfile> {
    const { data } = await api.post<UserProfile>('/profile', profileData);
    return data;
  },

  // PATCH /api/v1/profile
  // Используем Partial<UserProfile>, чтобы можно было обновлять только нужные поля
  async updateProfile(updates: Partial<UserProfile>): Promise<UserProfile> {
    const { data } = await api.patch<UserProfile>('/profile', updates);
    return data;
  },

  // GET /api/v1/profile/feed?limit=...
  async getProfileFeed(limit: number = 10): Promise<UserProfile[]> {
    const { data } = await api.get<UserProfile[]>('/profile/feed', {
      params: { limit } // Axios сам добавит ?limit=X в URL
    });
    return data;
  }
};