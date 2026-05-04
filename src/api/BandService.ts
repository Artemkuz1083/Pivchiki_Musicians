import { FullGroupProfile } from "../app/types/Group";
import { api } from "./instance";


export interface CreateGroupRequest {
  name: string;
  description: string;
  city: string;
  year: number;
  genres: string[];
  financial: string;
  seriousness: string;
}

export const groupService = {
  // Создание новой группы
  createGroup: async (data: CreateGroupRequest): Promise<FullGroupProfile> => {
    const response = await api.post<FullGroupProfile>('/groups', data);
    return response.data;
  },

  // Получение профиля группы по ID
  getGroupById: async (id: string | number): Promise<FullGroupProfile> => {
    const response = await api.get<FullGroupProfile>(`/groups/${id}`);
    return response.data;
  },

  deleteGroup: async (id: number): Promise<void> => {
  // Параметр id передается в query string: ?id=123
  await api.delete('/groups', {
    params: { id }
  });
  },

  updateGroup: async (data: FullGroupProfile): Promise<FullGroupProfile> => {
  // Отправляем объект целиком. Бэкенд проверит права администратора.
  const response = await api.patch<FullGroupProfile>('/groups', data);
  return response.data;
  },

  getGroupsFeed: async (limit: number = 10, cities?: string[]): Promise<FullGroupProfile[]> => {
  const response = await api.get<FullGroupProfile[]>('/groups/feed', {
    params: { 
      limit,
      city: cities // axios развернет это в ?city=Moscow&city=Chelyaba woooooh
    }
  });
  return response.data;
  }
};