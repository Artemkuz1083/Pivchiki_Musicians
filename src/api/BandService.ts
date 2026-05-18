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

const EXTRA_MOCK_GROUPS: FullGroupProfile[] = [
  {
    ID: 301,
    GroupName: "Скажи Мне Люблю",
    AboutGroup: "Поп рок группа в поисках своего бас гитариста, обучим, репы каждую неделю",
    City: "Челябинск",
    YearOfCreation: 2024,
    LevelOfSerious: "SEMI_PROFESSIONAL",
    FinancialStatus: "LIMITED_BUDGET",
    PhotoURL: "/mock-images/feed1.jpg",
    Genres: ["Pop rock"],
    Link: "https://t.me/tellmeloveband",
    IsVisible: true,
    Platforms: ["Telegram"],
    Members: [
      { UserID: 3302, Name: "Рома", Role: "Вокал, Ритм-гитара" },
      { UserID: 3301, Name: "Данитч", Role: "Лид-гитара" },
      { UserID: 3300, Name: "Даша", Role: "Барабаны" }
    ]
  },
  {
    ID: 302,
    GroupName: "Моя Фобия",
    AboutGroup: "Создаем Эмо, Эмокор и ищем соло гитариста, играем как свои песни так и каверы, ждем теюя!",
    City: "Челябинск",
    YearOfCreation: 2024,
    LevelOfSerious: "SEMI_PROFESSIONAL",
    FinancialStatus: "POOR",
    PhotoURL: "/mock-images/feed2.jpg",
    Genres: ["Metal", "Emo"],
    Link: "https://t.me/myphobiaband",
    IsVisible: true,
    Platforms: ["Telegram"],
    Members: [
      { UserID: 3300, Name: "Даша", Role: "Вокал" },
      { UserID: 3302, Name: "Рома", Role: "Вокал, Ритм-гитара" },
      { UserID: 3304, Name: "Руслан", Role: "Барабаны" },
      { UserID: 3305, Name: "Леша", Role: "Бас гитара" }
    ]
  },
  {
    ID: 303,
    GroupName: "MOODRAIN",
    AboutGroup: "Поп-панк / Эмо-рок банда. Песни про школу, скейтборды и разбитое сердце. Готовы рвать локальные клубы! Ищем энергичного соло-гитариста, который не боится быстрых темпов.",
    City: "Миасс",
    YearOfCreation: 2025,
    LevelOfSerious: "SEMI_PROFESSIONAL",
    FinancialStatus: "LIMITED_BUDGET",
    PhotoURL: "/mock-images/feed3.jpg",
    Genres: ["Pop-Punk", "Emo Rock"],
    Link: "https://t.me/moodrainband",
    IsVisible: true,
    Platforms: ["Telegram"],
    Members: [
      { UserID: 3307, Name: "Ваня", Role: "Вокал, Ритм-гитара" },
      { UserID: 3308, Name: "Макс", Role: "Барабаны" },
      { UserID: 3309, Name: "Данил", Role: "Бас гитара" }
    ]
  },
  {
    ID: 304,
    GroupName: "Carrion Hearts",
    AboutGroup: "Готик метал группа в поисках барабанщика и клавишника, если тебе по душе мрачная атмосфера и тяжелый труд, ждем тебя",
    City: "Челябинск",
    YearOfCreation: 2026,
    LevelOfSerious: "PROFESSIONAL",
    FinancialStatus: "READY_TO_INVEST",
    PhotoURL: "/mock-images/feed4.jpg",
    Genres: ["Metal"],
    Link: "https://t.me/DCarrionHearts",
    IsVisible: true,
    Platforms: ["Telegram"],
    Members: [
      { UserID: 3310, Name: "Даня", Role: "Вокал, Ритм-гитара" },
      { UserID: 3311, Name: "Даша", Role: "Бас-гитара" },
      { UserID: 3312, Name: "Ярослава", Role: "Лид-гитара" }
    ]
  }
];
export const groupService = {
  createGroup: async (data: CreateGroupRequest): Promise<FullGroupProfile> => {
    const response = await api.post<FullGroupProfile>('/groups', data);
    
    const groupId = response.data?.ID;
    if (groupId) {
      localStorage.setItem('my_group_id', String(groupId));
    }
    
    return response.data;
  },

  getGroupById(id: number | string) {
    return api.get('/groups', { 
        params: {
            id: Number(id) // Передается как: /api/v1/groups?id=10
        }
    }).then(res => {
      if (res.data && !Array.isArray(res.data)) {
        const groupId = res.data.id || res.data.ID;
        if (groupId) {
          localStorage.setItem('my_group_id', String(groupId));
        }
      }
      return res.data;
    });
  },

  //Удаление группы (?id=10)
  deleteGroup: async (id: number): Promise<void> => {
    localStorage.removeItem('my_group_id');
    
    await api.delete('/groups', {
      params: { id: Number(id) } // Передается как: /api/v1/groups?id=10
    });
  },

  updateGroup: async (payload: {
    id: number;
    groupName: string;
    aboutGroup?: string;
    city?: string;
    yearOfCreation?: number;
    levelOfSerious?: string;
    financialStatus?: string;
    link?: string;
    isVisible?: boolean;
    genres?: string[];
    platforms?: string[];
  }): Promise<FullGroupProfile> => {
    const response = await api.patch<FullGroupProfile>('/groups', payload, {
      params: { 
        id: Number(payload.id)
      },
      headers: {
        'Content-Type': 'application/json',
      }
    });
    return response.data;
  },

  //Лента групп (GET /api/v1/groups/feed)
  getGroupsFeed: async (limit: number = 10, cities?: string[]): Promise<FullGroupProfile[]> => {
    let backendGroups: FullGroupProfile[] = [];
    
    try {
      //Пытаемся забрать реальные профили с бэкенда
      const response = await api.get<FullGroupProfile[]>('/groups/feed', {
        params: { limit, city: cities }
      });
      if (Array.isArray(response.data)) {
        backendGroups = response.data;
      }
    } catch (error) {
      console.warn("Бэкенд ленты групп временно недоступен, показываем только моки", error);
    }

    //Фильтруем 4 мока по городу (если фильтр в приложении выбран)
    let filteredMocks = EXTRA_MOCK_GROUPS;
    if (cities && cities.length > 0) {
      filteredMocks = EXTRA_MOCK_GROUPS.filter(mockGroup => cities.includes(mockGroup.City));
    }

    //Объединяем реальные профили от бэка и 4 локальных мока вместе
    console.log(`Лента сформирована: ${backendGroups.length} с бэка + ${filteredMocks.length} моков.`);
    return [...backendGroups, ...filteredMocks];
  },

  // Живой свайп на бэкенд
  async swipeGroup(id: number, action: 'like' | 'dislike'): Promise<{ is_match: boolean }> {
    // Если свайпаем моканую группу (у них ID 301-304), бэк о них не знает — перехватываем
    if (id >= 301 && id <= 304) {
      console.log(`[Мок-Свайп] Группа #${id} -> ${action}`);
      //группа 304 всегда дает взаимный мэтч для теста
      if (action === 'like' && id === 304) {
        return { is_match: true };
      }
      return { is_match: false };
    }

    const response = await api.post<{ is_match: boolean }>(`/groups/feed/${id}/swipe`, { action });
    return response.data;
  },

  //Загрузка фото/медиа (FormData)
  async uploadGroupMedia(groupId: number, file: File) {
    const myForm = new FormData();
    
    myForm.append('group_id', groupId as any); 
    myForm.append('file', file); ;
    console.log("Отправляем group_id как:", groupId, "(тип:", typeof groupId, ")");

    return api.post('/groups/media', myForm, {
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    }).then(res => res.data);
  }
};