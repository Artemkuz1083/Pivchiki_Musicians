import { useEffect, useState } from 'react'; 
import { useNavigate } from 'react-router';
import { CheckCircle2, User, Eye, Loader2 } from 'lucide-react'; 
import { Button } from '../components/ui/button';
import { profileService } from '../../api/profileService'; 
import { UserProfile, PerformancEexperience } from '../types';

export function RegistrationSuccess() {
  const navigate = useNavigate();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [progress, setProgress] = useState(0); // Добавлено для хранения прогресса

  useEffect(() => {
    const loadProfileAndCalculateProgress = async () => {
      try {
        const data = await profileService.getMyProfile();
        setProfile(data);
        // Рассчитываем прогресс после загрузки профиля
        const calculatedProgress = calculateProgress(data);
        setProgress(calculatedProgress);
      } catch (error) {
        console.error("Не удалось загрузить профиль для страницы успеха", error);
        // Если профиль не загрузился (например, 401), можно просто показать 0% или дефолтное сообщение
        setProgress(0); 
      } finally {
        setIsLoading(false);
      }
    };
    loadProfileAndCalculateProgress();
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

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-[#60519B] animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-2xl shadow-xl p-6">
          <div className="flex justify-center mb-4">
            <div className="bg-green-100 rounded-full p-4">
              <CheckCircle2 className="w-16 h-16 text-green-600" />
            </div>
          </div>

          <div className="bg-gradient-to-r from-[#60519B] to-[#31323E] rounded-xl p-6 mb-6">
            <h2 className="text-2xl font-bold text-white text-center mb-3">
              Вы прошли регистрацию на {progress}%
            </h2>
            <p className="text-white text-center leading-relaxed">
              {progress < 100 
                ? 'Для того чтобы ваша анкета привлекла больше внимания, мы советуем вам дополнить информацию в ней.' 
                : 'Ваш профиль полностью готов! Теперь вас точно заметят!'}
              Вы всегда можете изменить информацию в вашем профиле.
            </p>
          </div>

          <p className="text-center text-gray-700 mb-8 text-lg">
            Приятного пользования нашим сервисом! 🎵
          </p>

          <div className="space-y-3">
            <Button
              onClick={() => navigate('/profile')}
              className="w-full bg-[#60519B] hover:bg-[#4d3f7e] text-white py-6 text-lg rounded-xl shadow-lg"
            >
              <User className="w-5 h-5 mr-2" />
              Перейти в профиль
            </Button>

            <Button
              onClick={() => navigate('/browse')}
              variant="outline"
              className="w-full py-6 text-lg rounded-xl border-2 border-[#60519B] text-[#60519B] hover:bg-[#60519B]/5"
            >
              <Eye className="w-5 h-5 mr-2" />
              Просмотр анкет
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}