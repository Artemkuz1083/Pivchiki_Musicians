import { useState } from 'react';
import { useNavigate } from 'react-router';
import { ArrowLeft, Check, Loader2 } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Checkbox } from '../components/ui/checkbox'; 
import { Label } from '../components/ui/label'; 
import { RadioGroup, RadioGroupItem } from '../components/ui/radio-group';
import { ProfileCard } from '../components/ProfileCard';
import { profileService } from '../../api/profileService';

import { 
  UserProfile, 
  CITIES, 
  INSTRUMENTS, 
  GENRES, 
  SKILL_LEVELS, 
  PerformancEexperience} from '../types';
import { UpdateProfileDto } from "../types/UpdateProfileDto";

export function Registration() {
  const navigate = useNavigate();
  
  const [selectedCities, setSelectedCities] = useState<string[]>([]);
  const [selectedInstruments, setSelectedInstruments] = useState<string[]>([]);
  const [instrumentLevels, setInstrumentLevels] = useState<Record<string, number>>({}); 
  const [selectedGenres, setSelectedGenres] = useState<string[]>([]);
  const [isSaving, setIsSaving] = useState(false);
  const [userName] = useState("Музыкант"); 
  const [aboutUser] = useState("Новый пользователь"); 
  const [age] = useState(20); 
  const [contact] = useState("Не указан"); 
  const [link] = useState(""); 
  const [isVisible] = useState(true); 
  const [performanceExperience] = useState<PerformancEexperience>("NEVER"); 
  const [theoryLevel] = useState(1); 

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
      selectedCities.length > 0 &&
      selectedInstruments.length > 0 &&
      selectedInstruments.every(inst => instrumentLevels[inst] !== undefined) && 
      selectedGenres.length > 0
    );
  };

  const handleSubmit = async () => {
    if (!isFormValid()) {
      alert("Пожалуйста, заполните все обязательные поля (город, инструменты и их уровень, жанры).");
      return;
    }
    setIsSaving(true);

    const payload: UpdateProfileDto = {
      UserName: userName, 
      AboutUser: aboutUser,
      Age: age,
      City: selectedCities[0] || '', 
      Contact: contact,
      Link: link,
      Genres: selectedGenres,
      Instruments: selectedInstruments.map(inst => ({
        Instrument: inst,
        InstrumentProficiencyLevel: instrumentLevels[inst], 
      })),
      IsVisible: isVisible,
      PerformancExperience: performanceExperience, 
      TheoryLevel: theoryLevel,
    };

    try {
      await profileService.updateProfile(payload);
      navigate('/registration-success');
    } catch (error) {
      console.error("Ошибка при сохранении:", error);
      alert("Ошибка при сохранении данных.");
    } finally {
      setIsSaving(false);
    }
  };

  const currentProfile: UserProfile = {
    ID: 0, 
    UserName: userName,
    AboutUser: aboutUser,
    Age: age,
    City: selectedCities[0] || 'Не выбран',
    Contact: contact,
    Link: link,
    IsVisible: isVisible,
    PerformancExperience: performanceExperience, 
    TheoryLevel: theoryLevel,
    Genres: selectedGenres,
    Instruments: selectedInstruments.map(inst => ({
      Instrument: inst,
      InstrumentProficiencyLevel: instrumentLevels[inst] !== undefined ? instrumentLevels[inst] : 0, 
    })),
  };

  const hasAnyData = selectedCities.length > 0 || selectedInstruments.length > 0 || selectedGenres.length > 0;

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-[#60519B] text-white p-4 sticky top-0 z-10 shadow-md">
        <div className="max-w-md mx-auto flex items-center gap-3">
          <button onClick={() => navigate('/')} className="p-1">
            <ArrowLeft className="w-6 h-6" />
          </button>
          <h1 className="text-xl font-semibold">Регистрация</h1>
        </div>
      </div>

      <div className="max-w-md mx-auto p-4 pb-24">
        {/* Секция 1: Города */}
        <div className="bg-white rounded-xl shadow-md p-5 mb-6">
          <h2 className="font-semibold text-gray-900 mb-4 text-lg">1. Города</h2>
          <div className="space-y-3">
            {CITIES.map(city => (
              <div key={city} className="flex items-center gap-3">
                <Checkbox 
                  id={`city-${city}`} 
                  checked={selectedCities.includes(city)} 
                  onCheckedChange={() => toggleCity(city)} 
                />
                <Label htmlFor={`city-${city}`} className="cursor-pointer flex-1">{city}</Label>
              </div>
            ))}
          </div>
        </div>

        {/* Секция 2: Инструменты */}
        <div className="bg-white rounded-xl shadow-md p-5 mb-6">
          <h2 className="font-semibold text-gray-900 mb-4 text-lg">2. Инструменты</h2>
          <div className="space-y-4">
            {INSTRUMENTS.map(inst => (
              <div key={inst} className="space-y-3 border-b last:border-0 pb-3">
                <div className="flex items-center gap-3">
                  <Checkbox 
                    id={`inst-${inst}`} 
                    checked={selectedInstruments.includes(inst)} 
                    onCheckedChange={() => toggleInstrument(inst)} 
                  />
                  <Label htmlFor={`inst-${inst}`} className="font-medium cursor-pointer flex-1">{inst}</Label>
                </div>
                {selectedInstruments.includes(inst) && (
                  <div className="ml-7 p-3 bg-gray-50 rounded-lg">
                    <RadioGroup
                      value={instrumentLevels[inst]?.toString() || ""}
                      onValueChange={(val) => setInstrumentLevel(inst, Number(val))}
                    >
                      <div className="grid grid-cols-1 gap-2">
                        {SKILL_LEVELS.map(lvl => ( 
                          <div key={lvl.value} className="flex items-center gap-2">
                            <RadioGroupItem value={lvl.value.toString()} id={`${inst}-${lvl.value}`} />
                            <Label htmlFor={`${inst}-${lvl.value}`} className="text-sm">
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

        {/* Секция 3: Жанры */}
        <div className="bg-white rounded-xl shadow-md p-5 mb-6">
          <h2 className="font-semibold text-gray-900 mb-4 text-lg">3. Жанры</h2>
          <div className="flex flex-wrap gap-2">
            {GENRES.map(genre => (
              <button
                key={genre}
                onClick={() => toggleGenre(genre)}
                className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
                  selectedGenres.includes(genre)
                    ? 'bg-[#60519B] text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {genre}
              </button>
            ))}
          </div>
        </div>

        {hasAnyData && (
          <div className="mt-8 opacity-80">
            <p className="text-center text-xs text-gray-400 mb-4 uppercase tracking-widest">Превью анкеты</p>
            <ProfileCard profile={currentProfile} isPreview />
          </div>
        )}

        <div className="fixed bottom-0 left-0 right-0 p-4 bg-white/80 backdrop-blur-md border-t">
          <div className="max-w-md mx-auto">
            <Button
              onClick={handleSubmit}
              disabled={!isFormValid() || isSaving}
              className="w-full bg-[#60519B] hover:bg-[#4d3f7e] text-white py-6 text-lg rounded-xl shadow-lg"
            >
              {isSaving ? (
                <Loader2 className="animate-spin" />
              ) : (
                <div className="flex items-center justify-center">
                  <Check className="mr-2" /> 
                  <span>Сохранить</span>
                </div>
              )}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}