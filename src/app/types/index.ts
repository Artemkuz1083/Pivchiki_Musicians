// types.ts (обновленный)
export type SkillLevel = number; 

export const SKILL_LEVELS = [
  { value: 0, label: 'Новичок' },
  { value: 1, label: 'Любитель' },
  { value: 2, label: 'Продвинутый' },
  { value: 3, label: 'Профессионал' },
];

export type PerformancEexperience = 'NEVER' | 'LOCAL_GIGS' | 'TOURS' | 'PROFESSIONAL';

export interface InstrumentSkill {
  Instrument: string; 
  InstrumentProficiencyLevel: number; 
}

export interface UserProfile {
  ID: number; 
  UserName: string; 
  AboutUser: string; 
  Age: number; 
  City: string; 
  Contact: string; 
  Genres: string[]; 
  Instruments: InstrumentSkill[]; 
  IsVisible: boolean; 
  Link: string; 
  PerformancExperience: PerformancEexperience; 
  TheoryLevel: number; 
}

// Новый DTO для создания профиля (POST /api/v1/profile)
// Согласно Swagger, здесь нет ID, AboutUser, Age, Link, PerformancExperience, TheoryLevel, IsVisible
export interface CreateProfileDto {
  UserName: string; 
  City: string; 
  Contact: string; 
  Genres: string[]; 
  Instruments: InstrumentSkill[]; 
  // Другие поля, если они требуются бэкендом при создании
}

// DTO для обновления профиля (предположительно PATCH /api/v1/profile)
// Если PATCH нет, то этот DTO будет не нужен или придется использовать POST для обновления
export interface UpdateProfileDto {
  UserName?: string; 
  AboutUser?: string; 
  Age?: number; 
  City?: string; 
  Contact?: string; 
  Genres?: string[]; 
  Instruments?: InstrumentSkill[]; // Используем InstrumentSkill
  IsVisible?: boolean; 
  Link?: string; 
  PerformancExperience?: PerformancEexperience; 
  TheoryLevel?: number; 
}

// DTO для запроса авторизации/регистрации
export interface AuthRequestDto {
  login: string;
  password: string;
}

// DTO для ответа авторизации/регистрации
export interface AuthResponseDto {
  is_profile_created: boolean;
  token: string;
}

export const CITIES = [
  'Москва', 'Санкт-Петербург', 'Новосибирск', 'Екатеринбург', 'Казань', 'Нижний Новгород', 
  'Челябинск', 'Самара', 'Омск', 'Ростов-на-Дону', 'Уфа', 'Красноярск', 'Воронеж', 
  'Пермь', 'Волгоград',
];

export const INSTRUMENTS = [
  'Гитара', 'Бас-гитара', 'Барабаны', 'Клавишные', 'Вокал', 'Скрипка', 'Саксофон', 
  'Труба', 'Фортепиано', 'Укулеле', 'Синтезатор', 'DJ/Диджеинг',
];

export const GENRES = [
  'Рок', 'Поп', 'Джаз', 'Блюз', 'Классика', 'Металл', 'Панк', 'Хип-хоп', 
  'Электронная музыка', 'Фолк', 'Кантри', 'Инди', 'Регги', 'Фанк', 'Соул', 'R&B',
];
