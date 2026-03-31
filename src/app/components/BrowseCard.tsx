import { UserProfile, SKILL_LEVELS } from '../types';
import { Music, MapPin, Guitar } from 'lucide-react';

interface MusicianFeedCardProps {
  profile: UserProfile;
  imageUrl?: string; // Для ленты фото критично
}

export function BrowseCard({ profile, imageUrl }: MusicianFeedCardProps) {
  if (!profile) return null;

  const getSkillLabel = (level: number) => {
    return SKILL_LEVELS.find(s => s.value === level)?.label || `Уровень ${level}`;
  };

  return (
    <div 
      className="relative w-full max-w-[380px] aspect-[3/4.5] rounded-[2.5rem] overflow-hidden shadow-2xl flex flex-col justify-end p-4 group select-none"
      style={{ 
        backgroundImage: `url(${imageUrl || 'https://images.unsplash.com/photo-1511735111819-9a3f7709049c?auto=format&fit=crop&q=80&w=600'})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center'
      }}
    >
      {/* Градиент для читаемости плашек */}
      <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/10 to-transparent" />

      <div className="relative z-10 space-y-2 mb-4">
        {/* Плашка Жанров */}
        <section className="bg-white/15 backdrop-blur-xl border border-white/20 rounded-2xl p-3 text-white">
          <div className="flex items-center gap-2 text-[10px] font-black uppercase tracking-[0.15em] mb-2 opacity-70">
            <Music size={12} strokeWidth={3} />
            Жанры
          </div>
          <div className="flex flex-wrap gap-1.5">
            {profile.Genres.map((genre, idx) => (
              <span key={idx} className="px-2.5 py-1 bg-white/10 rounded-full text-[11px] font-semibold border border-white/5">
                {genre}
              </span>
            ))}
          </div>
        </section>

        {/* Плашка Города */}
        <section className="bg-white/15 backdrop-blur-xl border border-white/20 rounded-2xl p-3 text-white">
          <div className="flex items-center gap-2 text-[10px] font-black uppercase tracking-[0.15em] mb-2 opacity-70">
            <MapPin size={12} strokeWidth={3} />
            Локация
          </div>
          <div className="flex flex-wrap gap-1.5">
            <span className="px-2.5 py-1 bg-[#7C74AB]/40 rounded-full text-[11px] font-semibold border border-white/10">
              {profile.City}
            </span>
          </div>
        </section>

        {/* Плашка Инструментов */}
        <section className="bg-white/15 backdrop-blur-xl border border-white/20 rounded-2xl p-3 text-white">
          <div className="flex items-center gap-2 text-[10px] font-black uppercase tracking-[0.15em] mb-2 opacity-70">
            <Guitar size={12} strokeWidth={3} />
            Инструменты
          </div>
          <div className="space-y-1.5">
            {profile.Instruments.map((item, idx) => (
              <div key={idx} className="flex justify-between items-center text-[13px]">
                <span className="font-bold opacity-90">{item.Instrument}</span>
                <span className="text-[#D1C4E9] font-black tracking-tight">
                  {getSkillLabel(item.InstrumentProficiencyLevel)}
                </span>
              </div>
            ))}
          </div>
        </section>
      </div>

      {/* Имя (Центральная фигура) */}
      <div className="relative z-10 bg-white/95 backdrop-blur-md py-4 rounded-[1.2rem] shadow-2xl transform transition-transform group-hover:scale-[1.02]">
        <h2 className="text-center text-2xl font-black text-[#1F1F1F] uppercase tracking-tighter italic">
          {profile.UserName}
        </h2>
      </div>
    </div>
  );
}