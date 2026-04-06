import { UserProfile } from '../types';
import { MapPin, Lock } from 'lucide-react';

export function PublicPreviewCard({ profile }: { profile: UserProfile }) {
  return (
    <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-200 relative overflow-hidden">
      {/* Плашка "Только для своих" */}
      <div className="absolute top-2 right-2 text-[#60519B] opacity-20">
        <Lock size={16} />
      </div>

      <div className="flex flex-col gap-3">
        <div>
          <h3 className="text-lg font-bold text-gray-900 leading-tight">
            Имя скрыто
          </h3>
          <div className="flex items-center gap-1 text-gray-500 text-sm">
            <MapPin size={14} />
            <span>{profile.City}</span>
          </div>
        </div>

        <div className="space-y-2">
          <p className="text-[10px] uppercase tracking-wider font-bold text-gray-400">Инструменты</p>
          <div className="flex flex-wrap gap-2">
            {profile.Instruments.map((i, idx) => (
              <span key={idx} className="px-3 py-1 bg-gray-100 rounded-lg text-xs font-semibold text-gray-700">
                {i.Instrument}
              </span>
            ))}
          </div>
        </div>
        
        <div className="mt-2 text-xs text-[#60519B] font-medium italic">
          Зарегистрируйтесь, чтобы увидеть фото и навыки →
        </div>
      </div>
    </div>
  );
}