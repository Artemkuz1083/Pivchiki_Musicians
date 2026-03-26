import { UserProfile, SKILL_LEVELS } from '../types';
import { Music, MapPin, Guitar, User } from 'lucide-react';

interface ProfileCardProps {
  profile: UserProfile;
  isPreview?: boolean;
}

export function ProfileCard({ profile, isPreview = false }: ProfileCardProps) {
  if (!profile) return null;

  const getSkillLabel = (level: number) => {
    return SKILL_LEVELS.find(s => s.value === level)?.label || `Уровень ${level}`;
  };

  return (
    <div className="bg-white rounded-xl shadow-md p-5 mb-6 border border-gray-100">
      {isPreview && (
        <p className="text-sm text-gray-400 mb-4 italic">Предварительный просмотр вашей анкеты:</p>
      )}

      <div className="flex items-center gap-3 mb-6">
        <div className="w-12 h-12 bg-[#60519B] rounded-full flex items-center justify-center text-white">
          <User className="w-6 h-6" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-gray-900">{profile.UserName || 'Имя не указано'}</h2>
          <p className="text-sm text-gray-500">{profile.AboutUser}</p>
        </div>
      </div>

      <div className="space-y-6">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <MapPin className="w-4 h-4 text-[#60519B]" />
            <h3 className="font-semibold text-gray-900">Город</h3>
          </div>
          <div className="flex flex-wrap gap-2">
            <span className="px-3 py-1 bg-[#60519B]/10 text-[#60519B] rounded-full text-sm">
              {profile.City || 'Не указан'}
            </span>
          </div>
        </div>

        <div>
          <div className="flex items-center gap-2 mb-2">
            <Guitar className="w-4 h-4 text-[#60519B]" />
            <h3 className="font-semibold text-gray-900">Инструменты</h3>
          </div>
          <div className="space-y-2">
            {(profile.Instruments || []).map((item, idx) => (
              <div key={idx} className="flex justify-between items-center bg-gray-50 rounded-lg p-2 px-3">
                <span className="text-gray-900 font-medium">{item.Instrument}</span>
                <span className="text-sm text-[#60519B] bg-white px-2 py-0.5 rounded shadow-sm">
                  {getSkillLabel(item.InstrumentProficiencyLevel)}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Жанры */}
        <div>
          <div className="flex items-center gap-2 mb-2">
            <Music className="w-4 h-4 text-[#60519B]" />
            <h3 className="font-semibold text-gray-900">Жанры</h3>
          </div>
          <div className="flex flex-wrap gap-2">
            {(profile.Genres || []).map((genre, idx) => (
              <span
                key={idx}
                className="px-3 py-1 bg-[#BFC0D1]/30 text-[#31323E] rounded-full text-sm"
              >
                {genre}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}