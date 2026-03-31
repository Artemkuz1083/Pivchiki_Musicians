import { useState } from 'react';
import { useNavigate } from 'react-router';
import { ArrowLeft, Check, Loader2, User, Lock } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Checkbox } from '../components/ui/checkbox';
import { Label } from '../components/ui/label';
import { Input } from '../components/ui/input';
import { RadioGroup, RadioGroupItem } from '../components/ui/radio-group';
import { ProfileCard } from '../components/ProfileCard';
import { profileService } from '../../api/profileService';
import { authService } from '../../api/AuthService';

import {
  UserProfile,
  CITIES,
  INSTRUMENTS,
  GENRES,
  SKILL_LEVELS,
  CreateProfileDto
} from '../types';

export function Registration() {
  const navigate = useNavigate();

  // 1. Данные аккаунта (для auth/registry)
  const [login, setLogin] = useState("");
  const [password, setPassword] = useState("");

  // 2. Личные данные (для profile)
  const [userName, setUserName] = useState("");
  const [contact, setContact] = useState("");
  const [age, setAge] = useState<number>(20);

  // 3. Музыкальные данные
  const [selectedCities, setSelectedCities] = useState<string[]>([]);
  const [selectedInstruments, setSelectedInstruments] = useState<string[]>([]);
  const [instrumentLevels, setInstrumentLevels] = useState<Record<string, number>>({});
  const [selectedGenres, setSelectedGenres] = useState<string[]>([]);

  // Технические состояния
  const [isSaving, setIsSaving] = useState(false);

  const toggleCity = (city: string) => {
    setSelectedCities(prev =>
      prev.includes(city) ? prev.filter(c => c !== city) : [...prev, city]
    );
  };

  const toggleInstrument = (instrument: string) => {
    setSelectedInstruments(prev => {
      if (prev.includes(instrument)) {
        const newLevels = { ...instrumentLevels };
        delete newLevels[instrument];
        setInstrumentLevels(newLevels);
        return prev.filter(i => i !== instrument);
      }
      return [...prev, instrument];
    });
  };

  const setInstrumentLevel = (instrument: string, level: number) => {
    setInstrumentLevels(prev => ({ ...prev, [instrument]: level }));
  };

  const toggleGenre = (genre: string) => {
    setSelectedGenres(prev =>
      prev.includes(genre) ? prev.filter(g => g !== genre) : [...prev, genre]
    );
  };

  const isFormValid = () => {
    return (
      login.trim().length >= 3 &&
      password.trim().length >= 4 &&
      userName.trim().length > 1 &&
      contact.trim().length > 2 &&
      selectedCities.length > 0 &&
      selectedInstruments.length > 0 &&
      selectedInstruments.every(inst => instrumentLevels[inst] !== undefined) &&
      selectedGenres.length > 0
    );
  };

  const handleSubmit = async () => {
    if (!isFormValid()) {
      alert("Заполните все обязательные поля!");
      return;
    }
    setIsSaving(true);

    try {
      //Регистрация (authService должен сохранить токен в localStorage)
      await authService.register({ login, password });

      //Создание профиля (уже с полученным токеном)
      const payload: CreateProfileDto = {
        UserName: userName,
        City: selectedCities[0] || '',
        Contact: contact,
        Genres: selectedGenres,
        Instruments: selectedInstruments.map(inst => ({
          Instrument: inst,
          InstrumentProficiencyLevel: instrumentLevels[inst],
        })),
      };

      await profileService.createProfile(payload);
      navigate('/registration-success');
    } catch (error: any) {
      console.error("Ошибка при регистрации:", error);
      alert(error.response?.data?.message || "Не удалось завершить регистрацию.");
    } finally {
      setIsSaving(false);
    }
  };

  // Превью для карточки (UserProfile)
  const currentProfile: UserProfile = {
    ID: 0,
    UserName: userName || "Твоё Имя",
    AboutUser: "", 
    Age: age,
    City: selectedCities[0] || 'Город не выбран',
    Contact: contact,
    Link: "",
    IsVisible: true,
    PerformancExperience: "NEVER",
    TheoryLevel: 1,
    Genres: selectedGenres,
    Instruments: selectedInstruments.map(inst => ({
      Instrument: inst,
      InstrumentProficiencyLevel: instrumentLevels[inst] ?? 0,
    })),
  };

  const hasAnyData = userName || selectedCities.length > 0 || selectedInstruments.length > 0;

  return (
    <div className="min-h-screen bg-[#F8F9FD]">
      {/* Хедер */}
      <div className="bg-[#60519B] text-white p-4 sticky top-0 z-20 shadow-lg">
        <div className="max-w-md mx-auto flex items-center gap-3">
          <button onClick={() => navigate('/')} className="p-1 hover:bg-white/10 rounded-full transition-colors">
            <ArrowLeft className="w-6 h-6" />
          </button>
          <h1 className="text-xl font-bold tracking-tight">Регистрация</h1>
        </div>
      </div>

      <div className="max-w-md mx-auto p-4 pb-32">
        
        {/* Данные аккаунта */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5 mb-6 space-y-4">
          <div className="flex items-center gap-2 mb-2">
            <Lock className="w-5 h-5 text-[#60519B]" />
            <h2 className="font-bold text-gray-800 text-lg">Вход в систему</h2>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <Label className="text-xs font-bold uppercase text-gray-400">Логин *</Label>
              <Input
                value={login}
                onChange={(e) => setLogin(e.target.value)}
                placeholder="Твой ник"
                className="rounded-xl border-gray-200"
              />
            </div>
            <div className="space-y-1.5">
              <Label className="text-xs font-bold uppercase text-gray-400">Пароль *</Label>
              <Input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••"
                className="rounded-xl border-gray-200"
              />
            </div>
          </div>
        </div>

        {/* Личная информация */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5 mb-6 space-y-4">
          <div className="flex items-center gap-2 mb-2">
            <User className="w-5 h-5 text-[#60519B]" />
            <h2 className="font-bold text-gray-800 text-lg">Профиль</h2>
          </div>

          <div className="space-y-1.5">
            <Label className="text-xs font-bold uppercase text-gray-400">Имя *</Label>
            <Input
              value={userName}
              onChange={(e) => setUserName(e.target.value)}
              placeholder="Как тебя зовут?"
              className="rounded-xl border-gray-200"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <Label className="text-xs font-bold uppercase text-gray-400">Возраст</Label>
              <Input
                type="number"
                value={age}
                onChange={(e) => setAge(Number(e.target.value))}
                className="rounded-xl border-gray-200"
              />
            </div>
            <div className="space-y-1.5">
              <Label className="text-xs font-bold uppercase text-gray-400">Контакты (ТГ) *</Label>
              <Input
                value={contact}
                onChange={(e) => setContact(e.target.value)}
                placeholder="@username"
                className="rounded-xl border-gray-200"
              />
            </div>
          </div>
        </div>

        {/* 1. Города */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5 mb-6">
          <h2 className="font-bold text-gray-800 mb-4 text-lg">1. Где ищем?</h2>
          <div className="grid grid-cols-1 gap-3">
            {CITIES.map(city => (
              <div key={city} className="flex items-center gap-3 p-3 rounded-xl border border-gray-50 hover:bg-gray-50 transition-colors">
                <Checkbox
                  id={`city-${city}`}
                  checked={selectedCities.includes(city)}
                  onCheckedChange={() => toggleCity(city)}
                />
                <Label htmlFor={`city-${city}`} className="cursor-pointer flex-1 font-medium text-gray-700">{city}</Label>
              </div>
            ))}
          </div>
        </div>

        {/* 2. Инструменты */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5 mb-6">
          <h2 className="font-bold text-gray-800 mb-4 text-lg">2. На чем играешь?</h2>
          <div className="space-y-4">
            {INSTRUMENTS.map(inst => (
              <div key={inst} className="space-y-3 border-b border-gray-50 last:border-0 pb-4">
                <div className="flex items-center gap-3">
                  <Checkbox
                    id={`inst-${inst}`}
                    checked={selectedInstruments.includes(inst)}
                    onCheckedChange={() => toggleInstrument(inst)}
                  />
                  <Label htmlFor={`inst-${inst}`} className="font-bold cursor-pointer flex-1 text-gray-700">{inst}</Label>
                </div>

                {selectedInstruments.includes(inst) && (
                  <div className="ml-7 p-4 bg-[#F8F9FD] rounded-2xl border border-[#60519B]/5">
                    <p className="text-[10px] font-black uppercase text-[#60519B] mb-3 tracking-widest">Уровень владения</p>
                    <RadioGroup
                      value={instrumentLevels[inst]?.toString() || ""}
                      onValueChange={(val) => setInstrumentLevel(inst, Number(val))}
                    >
                      <div className="space-y-2">
                        {SKILL_LEVELS.map(lvl => (
                          <div key={lvl.value} className="flex items-center gap-3">
                            <RadioGroupItem value={lvl.value.toString()} id={`${inst}-${lvl.value}`} />
                            <Label htmlFor={`${inst}-${lvl.value}`} className="text-sm text-gray-600">
                              {lvl.label}
                            </Label>
                          </div>
                        ))}
                      </div>
                    </RadioGroup>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* 3. Жанры */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5 mb-6">
          <h2 className="font-bold text-gray-800 mb-4 text-lg">3. Жанры</h2>
          <div className="flex flex-wrap gap-2">
            {GENRES.map(genre => (
              <button
                key={genre}
                onClick={() => toggleGenre(genre)}
                className={`px-4 py-2 rounded-xl text-sm font-bold transition-all ${
                  selectedGenres.includes(genre)
                    ? 'bg-[#60519B] text-white shadow-md shadow-purple-100'
                    : 'bg-gray-100 text-gray-500 hover:bg-gray-200'
                }`}
              >
                {genre}
              </button>
            ))}
          </div>
        </div>

        {/* Превью */}
        {hasAnyData && (
          <div className="mt-12 mb-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <p className="text-center text-[10px] font-black text-gray-400 mb-4 uppercase tracking-[0.3em]">Твоя карточка в поиске</p>
            <div className="scale-[0.95] origin-top opacity-90 grayscale-[20%]">
              <ProfileCard profile={currentProfile} isPreview />
            </div>
          </div>
        )}

        {/* Кнопка отправки */}
        <div className="fixed bottom-0 left-0 right-0 p-4 bg-white/80 backdrop-blur-xl border-t border-gray-100 z-30">
          <div className="max-w-md mx-auto">
            <Button
              onClick={handleSubmit}
              disabled={!isFormValid() || isSaving}
              className="w-full bg-[#60519B] hover:bg-[#4d3f7e] text-white py-7 text-lg font-bold rounded-2xl shadow-xl shadow-purple-100 transition-all active:scale-[0.98] disabled:opacity-50 disabled:grayscale"
            >
              {isSaving ? (
                <div className="flex items-center gap-2">
                  <Loader2 className="animate-spin" />
                  <span>Создаем аккаунт...</span>
                </div>
              ) : (
                <div className="flex items-center justify-center">
                  <Check className="mr-2 w-6 h-6" />
                  <span>Завершить регистрацию</span>
                </div>
              )}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}