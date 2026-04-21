import { X, Star, Mic2 } from 'lucide-react';
import { SKILL_LEVELS, PerformancEexperience, CITIES } from '../types';

interface FilterState {
  city: string;
  minSkill: number;
  experience: PerformancEexperience[];
  genres: string[];
}

const EXPERIENCE_LABELS: Record<PerformancEexperience, string> = {
  'NEVER': 'Без опыта',
  'LOCAL_GIGS': 'Клубы / Бары',
  'TOURS': 'Гастроли / Туры',
  'PROFESSIONAL': 'Про-сцена'
};

export function FilterSheet({ isOpen, onClose, filters, setFilters }: any) {
  if (!isOpen) return null;

  const toggleExperience = (exp: PerformancEexperience) => {
    const next = filters.experience.includes(exp)
      ? filters.experience.filter((e: string) => e !== exp)
      : [...filters.experience, exp];
    setFilters({ ...filters, experience: next });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/60 backdrop-blur-sm transition-all">
      <div className="w-full max-w-md bg-white rounded-t-[2.5rem] p-6 shadow-2xl animate-in slide-in-from-bottom duration-300">
        
        {/* Индикатор для свайпа вниз (визуальный) */}
        <div className="w-12 h-1.5 bg-gray-200 rounded-full mx-auto mb-6" />

        <div className="flex justify-between items-center mb-8">
          <h2 className="text-2xl font-black text-[#1F1F1F] uppercase italic tracking-tighter">Настройки поиска</h2>
          <button onClick={onClose} className="p-2 bg-gray-100 rounded-full hover:bg-gray-200 transition-colors">
            <X size={20} />
          </button>
        </div>

        <div className="space-y-8 overflow-y-auto max-h-[65vh] pr-2 custom-scrollbar">
          
          {/* 1. Город */}
          <section>
            <label className="text-[10px] font-black uppercase tracking-[0.2em] text-gray-400 block mb-3">Твой город</label>
            <select 
              value={filters.city}
              onChange={(e) => setFilters({...filters, city: e.target.value})}
              className="w-full bg-gray-50 border-2 border-transparent focus:border-[#60519B]/20 rounded-2xl p-4 font-bold text-[#1F1F1F] outline-none transition-all"
            >
              <option value="">Весь мир (все города)</option>
              {CITIES.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
          </section>

          {/* 2. Уровень владения (Не меньше чем...) */}
          <section>
            <div className="flex items-center gap-2 mb-4">
              <Star size={14} className="text-[#60519B]" fill="currentColor" />
              <label className="text-[10px] font-black uppercase tracking-[0.2em] text-gray-400">Мин. уровень мастерства</label>
            </div>
            <div className="flex bg-gray-100 rounded-2xl p-1.5 gap-1">
              {SKILL_LEVELS.map((level) => (
                <button
                  key={level.value}
                  onClick={() => setFilters({ ...filters, minSkill: level.value })}
                  className={`flex-1 py-3 rounded-xl text-[10px] font-black uppercase transition-all ${
                    filters.minSkill === level.value 
                    ? 'bg-white text-[#60519B] shadow-sm' 
                    : 'text-gray-400 hover:text-gray-600'
                  }`}
                >
                  {level.label}
                </button>
              ))}
            </div>
            <p className="mt-2 text-[10px] text-gray-400 italic text-center">Будем искать музыкантов уровня "{SKILL_LEVELS[filters.minSkill].label}" и выше</p>
          </section>

          {/* 3. Концертный опыт */}
          <section>
            <div className="flex items-center gap-2 mb-4">
              <Mic2 size={14} className="text-[#60519B]" />
              <label className="text-[10px] font-black uppercase tracking-[0.2em] text-gray-400">Опыт выступлений</label>
            </div>
            <div className="grid grid-cols-2 gap-2">
              {(Object.keys(EXPERIENCE_LABELS) as PerformancEexperience[]).map((exp) => {
                const isSelected = filters.experience.includes(exp);
                return (
                  <button
                    key={exp}
                    onClick={() => toggleExperience(exp)}
                    className={`p-3 rounded-2xl text-xs font-bold border-2 transition-all text-left flex items-center justify-between ${
                      isSelected 
                      ? 'border-[#60519B] bg-[#60519B]/5 text-[#60519B]' 
                      : 'border-gray-50 bg-gray-50 text-gray-500'
                    }`}
                  >
                    {EXPERIENCE_LABELS[exp]}
                    {isSelected && <div className="w-2 h-2 bg-[#60519B] rounded-full" />}
                  </button>
                );
              })}
            </div>
          </section>

        </div>

        {/* Кнопка "Погнали" */}
        <button 
          onClick={onClose}
          className="w-full py-5 bg-[#60519B] text-white rounded-[1.5rem] font-black uppercase italic text-lg shadow-xl shadow-[#60519B]/30 hover:shadow-[#60519B]/50 transition-all active:scale-95 mt-8 mb-2"
        >
          Применить фильтры
        </button>
      </div>
    </div>
  );
}