import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router';
import { ArrowLeft, Edit, Eye, Loader2 } from 'lucide-react';
import { Button } from '../components/ui/button';
import { ProfileCard } from '../components/ProfileCard';
import { UserProfile, PerformancEexperience } from '../types'; 
import { profileService } from '../../api/profileService';

export function Profile() {
  const navigate = useNavigate();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadProfile = async () => {
      try {
        const data = await profileService.getMyProfile();
        setProfile(data);
      } catch (error) {
        console.error("Не удалось загрузить профиль", error);
      } finally {
        setIsLoading(false);
      }
    };
    loadProfile();
  }, []);

  const calculateProgress = (p: UserProfile | null): number => {
    if (!p) return 0;
    
    const fields = [
      !!p.UserName, 
      !!p.AboutUser, 
      !!p.City, 
      (p.Genres || []).length > 0, 
      (p.Instruments || []).length > 0, 
      !!p.Contact, 
      p.PerformancExperience !== 'NEVER' 
    ];
    const completed = fields.filter(Boolean).length;
    return Math.round((completed / fields.length) * 100);
  };

  const progress = calculateProgress(profile);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-[#60519B] animate-spin" />
      </div>
    );
  }

  if (!profile || !profile.ID) { 
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="text-center bg-white p-8 rounded-2xl shadow-sm border border-gray-100">
          <p className="text-gray-600 mb-6 text-lg">У вас пока нет профиля</p>
          <Button 
            onClick={() => navigate('/registration')} 
            className="bg-[#60519B] hover:bg-[#4d3f7e] px-8 py-6 rounded-xl text-lg"
          >
            Создать анкету
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-10">
      <div className="bg-[#60519B] text-white p-4 sticky top-0 z-10 shadow-md">
        <div className="max-w-md mx-auto flex items-center gap-3">
          <button onClick={() => navigate('/browse')} className="p-1 hover:bg-white/10 rounded-full transition-colors">
            <ArrowLeft className="w-6 h-6" />
          </button>
          <h1 className="text-xl font-semibold">Мой профиль</h1>
        </div>
      </div>

      <div className="max-w-md mx-auto p-4">
        {/* Динамический Прогресс-бар */}
        <div className="bg-gradient-to-r from-[#60519B] to-[#31323E] rounded-xl p-5 mb-6 text-white shadow-lg">
          <div className="flex items-center justify-between mb-2">
            <h2 className="text-lg font-medium opacity-90">Заполнение анкеты</h2>
            <div className="text-2xl font-bold">{progress}%</div>
          </div>
          <div className="bg-white/20 rounded-full h-2.5 mb-2 overflow-hidden">
            <div 
              className="bg-white h-full transition-all duration-500 ease-out" 
              style={{ width: `${progress}%` }}
            ></div>
          </div>
          <p className="text-xs opacity-70">
            {progress < 100 ? 'Заполните все данные, чтобы вас чаще находили' : 'Ваш профиль полностью готов!'}
          </p>
        </div>

        <ProfileCard profile={profile} /> 

        <div className="space-y-3 mt-6">
          <Button
            onClick={() => navigate('/registration')} 
            className="w-full bg-[#60519B] hover:bg-[#4d3f7e] text-white py-7 text-lg rounded-xl shadow-sm"
          >
            <Edit className="w-5 h-5 mr-2" />
            Редактировать
          </Button>

          <Button
            onClick={() => navigate('/browse')}
            variant="outline"
            className="w-full py-7 text-lg rounded-xl border-2 border-[#BFC0D1] text-[#31323E] hover:bg-gray-100 transition-colors"
          >
            <Eye className="w-5 h-5 mr-2" />
            Смотреть другие анкеты
          </Button>
        </div>
      </div>
    </div>
  );
}