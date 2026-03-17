import {api} from './instance';
import {UserProfile} from '../app/types'

export const profileService = {
    async getMyProfile(): Promise<UserProfile> {
        const response = await api.get<UserProfile>('/api/v1/profile');
        return response.data;},

    async updateProfile(updates: any): Promise<UserProfile> {
    const { data } = await api.patch<UserProfile>('/api/v1/profile', updates);
    return data;
  }
};