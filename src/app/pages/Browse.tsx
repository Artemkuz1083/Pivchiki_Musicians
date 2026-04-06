import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router';
import { User, Search, Filter, X, Heart, Loader2 } from 'lucide-react';
import { BrowseCard } from '../components/BrowseCard';
import { UserProfile } from '../types';
import { MOCK_PROFILES } from '../../data/mockProfiles'; 
import { useAuth } from '../../context/AuthContext';

export function Browse() {
  const navigate = useNavigate();
  const [profiles, setProfiles] = useState<UserProfile[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [showFilters, setShowFilters] = useState(false);
  const { isLoggedIn } = useAuth(); // Достаем статус из контекста


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
    {/* Хедер (код хедера остается прежним) */}
    
    <main className="flex-1 flex flex-col items-center justify-center p-4 gap-6">
      <div className="w-full max-w-[380px]">
        
        {isLoggedIn ? (
          /* ВАРИАНТ 1: ПОЛНАЯ КАРТОЧКА (ДЛЯ АВТОРИЗОВАННЫХ) */
          <div className="animate-in fade-in zoom-in duration-300">
            <BrowseCard 
              profile={currentProfile} 
              imageUrl={`https://picsum.photos/seed/${currentProfile.ID}/600/800`}
            />

            <div className="flex gap-4 mt-6">
              <button 
                onClick={handleNext}
                className="flex-1 h-16 bg-white rounded-3xl flex items-center justify-center text-gray-400 shadow-xl hover:text-red-500 transition-all active:scale-95 border border-gray-100"
              >
                <X size={32} strokeWidth={3} />
              </button>
              <button 
                onClick={handleLike}
                className="flex-1 h-16 bg-[#60519B] rounded-3xl flex items-center justify-center text-white shadow-xl shadow-purple-200 hover:bg-[#4d3f7e] transition-all active:scale-95"
              >
                <Heart size={32} strokeWidth={3} fill="currentColor" />
              </button>
            </div>
          </div>
        ) : (
          /* ВАРИАНТ 2: ПРЕДПРОСМОТР (ДЛЯ ГОСТЕЙ) */
          <div className="space-y-6 animate-in slide-in-from-bottom-4 duration-500">
            {/* Контейнер с размытым фото для затравки */}
            <div className="relative h-[200px] w-full rounded-[2rem] overflow-hidden grayscale opacity-40">
               <img 
                src={`https://picsum.photos/seed/${currentProfile.ID}/600/400`} 
                className="w-full h-full object-cover blur-md" 
                alt="Locked profile"
               />
               <div className="absolute inset-0 flex items-center justify-center">
                 <Lock className="text-white w-12 h-12 opacity-50" />
               </div>
            </div>

            <PublicPreviewCard profile={currentProfile} />
            
            <div className="bg-white/80 backdrop-blur-sm p-6 rounded-3xl border border-dashed border-[#60519B]/30 text-center shadow-sm">
              <p className="text-gray-600 text-sm mb-4">
                Хотите увидеть больше информации и связаться с этим музыкантом?
              </p>
              <button 
                onClick={() => navigate('/registration')}
                className="w-full py-4 bg-[#60519B] text-white rounded-2xl font-bold shadow-lg shadow-[#60519B]/20 hover:scale-[1.02] transition-transform active:scale-95"
              >
                Зарегистрироваться
              </button>
              <button 
                onClick={handleNext}
                className="mt-4 text-[#60519B] text-xs font-bold uppercase tracking-widest opacity-60 hover:opacity-100 transition-opacity"
              >
                Посмотреть следующего гостя
              </button>
            </div>
          </div>
        )}
      </div>
    </main>

    <footer className="p-6 text-center text-gray-300 text-[10px] font-bold uppercase tracking-widest">
      Найдено в городе {currentProfile.City}: {profiles.filter(p => p.City === currentProfile.City).length}
    </footer>
  </div>
);