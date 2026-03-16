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

export const CITIES = [
  'Москва',
  'Санкт-Петербург',
  'Новосибирск',
  'Екатеринбург',
  'Казань',
  'Нижний Новгород',
  'Челябинск',
  'Самара',
  'Омск',
  'Ростов-на-Дону',
  'Уфа',
  'Красноярск',
  'Воронеж',
  'Пермь',
  'Волгоград',
];

export const INSTRUMENTS = [
  'Гитара',
  'Бас-гитара',
  'Барабаны',
  'Клавишные',
  'Вокал',
  'Скрипка',
  'Саксофон',
  'Труба',
  'Фортепиано',
  'Укулеле',
  'Синтезатор',
  'DJ/Диджеинг',
];

export const GENRES = [
  'Рок',
  'Поп',
  'Джаз',
  'Блюз',
  'Классика',
  'Металл',
  'Панк',
  'Хип-хоп',
  'Электронная музыка',
  'Фолк',
  'Кантри',
  'Инди',
  'Регги',
  'Фанк',
  'Соул',
  'R&B',
];

