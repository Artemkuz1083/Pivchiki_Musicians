import { useState } from 'react';
import { useNavigate } from 'react-router';
import { User, Search, Filter } from 'lucide-react';
import { Button } from '../components/ui/button';
import { ProfileCard } from '../components/ProfileCard';
import { UserProfile, SkillLevel, PerformancEexperience } from '../types';

const mockProfiles: UserProfile[] = [
  {
    ID: 1, 
    UserName: 'Иван Иванов',
    AboutUser: 'Опытный гитарист, ищу группу для выступлений.',
    Age: 28,
    City: 'Москва',
    Contact: 't.me/ivanov',
    Genres: ['Рок', 'Инди', 'Панк'],
    Instruments: [
      { Instrument: 'Гитара', InstrumentProficiencyLevel: 3 }, 
      { Instrument: 'Вокал', InstrumentProficiencyLevel: 2 },
    ],
    IsVisible: true,
    Link: 'https://youtube.com/ivanovmusic',
    PerformancExperience: 'LOCAL_GIGS', 
    TheoryLevel: 3,
  },
  {
    ID: 2,
    UserName: 'Мария Петрова',
    AboutUser: 'Энергичная барабанщица, люблю джаз и фанк.',
    Age: 24,
    City: 'Москва',
    Contact: 'vk.com/maria',
    Genres: ['Джаз', 'Фанк', 'Соул'],
    Instruments: [
      { Instrument: 'Барабаны', InstrumentProficiencyLevel: 4 },
    ],
    IsVisible: true,
    Link: 'https://soundcloud.com/mariadrums',
    PerformancExperience: 'PROFESSIONAL',
    TheoryLevel: 4,
  },
  {
    ID: 3,
    UserName: 'Алексей Сидоров',
    AboutUser: 'Бас-гитарист, интересуюсь электронщиной и поп-музыкой.',
    Age: 30,
    City: 'Санкт-Петербург',
    Contact: 'email@example.com',
    Genres: ['Электронная музыка', 'Инди', 'Поп'],
    Instruments: [
      { Instrument: 'Бас-гитара', InstrumentProficiencyLevel: 3 },
      { Instrument: 'Синтезатор', InstrumentProficiencyLevel: 2 },
    ],
    IsVisible: true,
    Link: '',
    PerformancExperience: 'TOURS',
    TheoryLevel: 2,
  },
  {
    ID: 4,
    UserName: 'Ольга Кузнецова',
    AboutUser: 'Классическая пианистка и вокалистка. Ищу для дуэта.',
    Age: 35,
    City: 'Екатеринбург',
    Contact: 't.me/olga_piano',
    Genres: ['Классика', 'Джаз', 'Поп'],
    Instruments: [
      { Instrument: 'Фортепиано', InstrumentProficiencyLevel: 4 },
      { Instrument: 'Вокал', InstrumentProficiencyLevel: 3 },
    ],
    IsVisible: true,
    Link: 'https://youtube.com/olgaclassic',
    PerformancExperience: 'PROFESSIONAL',
    TheoryLevel: 5,
  },
  {
    ID: 5,
    UserName: 'Сергей Морозов',
    AboutUser: 'Играю на саксофоне. Люблю джаз и блюз.',
    Age: 27,
    City: 'Казань',
    Contact: 'vk.com/sergeysax',
    Genres: ['Джаз', 'Блюз', 'Соул'],
    Instruments: [
      { Instrument: 'Саксофон', InstrumentProficiencyLevel: 2 },
    ],
    IsVisible: true,
    Link: '',
    PerformancExperience: 'LOCAL_GIGS',
    TheoryLevel: 1,
  },
];


export function Browse() {
  const navigate = useNavigate();
  const [showFilters, setShowFilters] = useState(false);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-[#60519B] text-white p-4 sticky top-0 z-10 shadow-md">
        <div className="max-w-md mx-auto">
          <div className="flex items-center justify-between mb-3">
            <h1 className="text-xl font-semibold">Поиск музыкантов</h1>
            <button onClick={() => navigate('/profile')} className="p-2 hover:bg-[#4d3f7e] rounded-lg">
              <User className="w-6 h-6" />
            </button>
          </div>
          
          <div className="flex gap-2">
            <div className="flex-1 bg-white rounded-lg px-4 py-2 flex items-center gap-2">
              <Search className="w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Поиск по городу, инструменту..."
                className="flex-1 outline-none text-gray-900"
              />
            </div>
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="bg-white text-[#60519B] rounded-lg px-4 py-2 hover:bg-[#BFC0D1]/30"
            >
              <Filter className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-md mx-auto p-4">
        <div className="mb-4">
          <p className="text-gray-600">Найдено музыкантов: {mockProfiles.length}</p>
        </div>

        <div className="space-y-4">
          {mockProfiles.map((profile, idx) => (
            <div key={idx} className="relative">
              <ProfileCard profile={profile} /> 
              <div className="flex gap-2 mt-2">
                <Button className="flex-1 bg-[#60519B] hover:bg-[#4d3f7e] text-white rounded-xl">
                  Написать
                </Button>
                <Button variant="outline" className="flex-1 rounded-xl border-2 border-[#60519B] text-[#60519B] hover:bg-[#60519B]/5">
                  Подробнее
                </Button>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-8 bg-white rounded-xl shadow-md p-6 text-center">
          <p className="text-gray-600 mb-4">
            Хотите найти идеальных музыкантов для вашей группы?
          </p>
          <Button
            onClick={() => navigate('/registration')}
            className="bg-[#60519B] hover:bg-[#4d3f7e] text-white px-6 py-3 rounded-xl"
          >
            Создать профиль
          </Button>
        </div>
      </div>
    </div>
  );
}