import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router';
import { User, Search, Filter, X, Heart, Loader2 } from 'lucide-react';
import { BrowseCard } from '../components/BrowseCard';
import { UserProfile } from '../types';
import { MOCK_PROFILES } from '../../data/mockProfiles'; 

export function Browse() {
  const navigate = useNavigate();
  const [profiles, setProfiles] = useState<UserProfile[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    const fetchFeed = async () => {
      try {
        setIsLoading(true);
        // const fetchedProfiles = await profileService.getProfileFeed(10);
        // setProfiles(fetchedProfiles);
        
        setProfiles(MOCK_PROFILES); 
        
      } catch (error) {
        console.error("Ошибка при загрузке ленты:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchFeed();
  }, []);

  // Логика переключения карточек
  const handleNext = () => {
    if (currentIndex < profiles.length - 1) {
      setCurrentIndex(prev => prev + 1);
    } else {
      // Если карточки кончились, можно либо загрузить новые, либо зациклить
      setCurrentIndex(0); 
    }
  };

  const handleLike = () => {
    console.log("Понравился пользователь:", profiles[currentIndex].ID);
    // Тут в будущем будет вызов matchService.like(profiles[currentIndex].id)
    handleNext();
  };

  // Состояние загрузки
  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#F8F9FD] flex flex-col items-center justify-center">
        <Loader2 className="w-12 h-12 text-[#60519B] animate-spin mb-4" />
        <p className="text-gray-500 font-medium">Ищем музыкантов поблизости...</p>
      </div>
    );
  }

  // Если список пуст
  if (profiles.length === 0) {
    return (
      <div className="min-h-screen bg-[#F8F9FD] flex flex-col items-center justify-center p-6 text-center">
        <div className="bg-white p-8 rounded-3xl shadow-sm border border-gray-100 max-w-sm">
          <Search className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-gray-800 mb-2">Никого не нашли</h2>
          <p className="text-gray-500 mb-6">Попробуйте изменить фильтры или загляните позже.</p>
          <button 
            onClick={() => window.location.reload()}
            className="text-[#60519B] font-bold uppercase text-sm tracking-widest"
          >
            Обновить поиск
          </button>
        </div>
      </div>
    );
  }

  const currentProfile = profiles[currentIndex];

  return (
    <div className="min-h-screen bg-[#F8F9FD] flex flex-col">
      {/* Хедер */}
      <header className="bg-[#60519B] text-white p-4 sticky top-0 z-20 shadow-lg">
        <div className="max-w-md mx-auto">
          <div className="flex items-center justify-between mb-3">
            <h1 className="text-xl font-bold tracking-tight">Музыканты</h1>
            <button 
              onClick={() => navigate('/profile')} 
              className="p-2 hover:bg-white/10 rounded-full transition-colors"
            >
              <User className="w-6 h-6" />
            </button>
          </div>
          
          <div className="flex gap-2">
            <div className="flex-1 bg-white rounded-2xl px-4 py-2.5 flex items-center gap-2 shadow-inner">
              <Search className="w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Поиск по инструментам..."
                className="flex-1 outline-none text-gray-900 bg-transparent text-sm"
              />
            </div>
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`bg-white/20 backdrop-blur-md text-white rounded-2xl px-4 py-2 transition-all ${showFilters ? 'bg-white/40' : ''}`}
            >
              <Filter className="w-5 h-5" />
            </button>
          </div>
        </div>
      </header>

      {/* Основной контент (Карточка) */}
      <main className="flex-1 flex flex-col items-center justify-center p-4 gap-6">
        <div className="w-full max-w-[380px]">
          <BrowseCard 
            profile={currentProfile} 
            // Используем ID для генерации уникальной картинки, пока нет реальных фото
            imageUrl={`https://picsum.photos/seed/${currentProfile.ID}/600/800`}
          />

          {/* Кнопки управления */}
          <div className="flex gap-4 mt-6">
            <button 
              onClick={handleNext}
              className="flex-1 h-16 bg-white rounded-3xl flex items-center justify-center text-gray-400 shadow-xl hover:text-red-500 transition-all active:scale-95 border border-gray-100"
              title="Пропустить"
            >
              <X size={32} strokeWidth={3} />
            </button>
            <button 
              onClick={handleLike}
              className="flex-1 h-16 bg-[#60519B] rounded-3xl flex items-center justify-center text-white shadow-xl shadow-purple-200 hover:bg-[#4d3f7e] transition-all active:scale-95"
              title="В группу!"
            >
              <Heart size={32} strokeWidth={3} fill="currentColor" />
            </button>
          </div>
        </div>
      </main>

      {/* Футер с краткой статистикой */}
      <footer className="p-6 text-center text-gray-300 text-[10px] font-bold uppercase tracking-widest">
        Найдено в городе {currentProfile.City}: {profiles.filter(p => p.City === currentProfile.City).length}
      </footer>
    </div>
  );
}