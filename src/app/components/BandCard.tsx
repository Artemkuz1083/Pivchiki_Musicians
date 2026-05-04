import { Users, MapPin, Calendar, Music, Wallet, Star, Loader2, Trash2 } from 'lucide-react';
import { FullGroupProfile, LevelOfSeriousness, FinancialStatus } from "../types/Group";
import { useNavigate } from 'react-router';
import { groupService } from '../../api/BandService';
import { useState } from 'react';

const SERIOUSNESS_LABELS: Record<LevelOfSeriousness, string> = {
  HOBBY: 'Хобби',
  SEMI_PROFESSIONAL: 'Полупрофи',
  PROFESSIONAL: 'Профи'
};

const FINANCIAL_LABELS: Record<FinancialStatus, string> = {
  POOR: 'Без бюджета',
  READY_TO_INVEST: 'Готовы инвестировать',
  LIMITED_BUDGET: 'Ограниченный бюджет'
};

interface GroupCardProps {
  group: FullGroupProfile;
}

export function GroupCard({ group }: GroupCardProps) {
  return (
    <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden mb-6">
      {/* Секция с Фото / Заглушкой */}
      <div className="h-40 bg-gradient-to-br from-[#60519B] to-[#31323E] relative">
        {group.PhotoURL && (
          <img src={group.PhotoURL} alt={group.GroupName} className="w-full h-full object-cover opacity-60" />
        )}
        <div className="absolute bottom-4 left-5 text-white">
          <div className="flex items-center gap-2 mb-1">
            <Users className="w-5 h-5 text-purple-300" />
            <span className="text-xs font-bold uppercase tracking-wider opacity-80">Музыкальная группа</span>
          </div>
          <h2 className="text-2xl font-bold">{group.GroupName}</h2>
        </div>
      </div>

      <div className="p-5 space-y-5">
        {/* Основные метки */}
        <div className="flex flex-wrap gap-2">
          <div className="flex items-center gap-1.5 px-3 py-1 bg-purple-50 text-[#60519B] rounded-full text-xs font-semibold border border-purple-100">
            <Star className="w-3 h-3" />
            {SERIOUSNESS_LABELS[group.LevelOfSerious] || group.LevelOfSerious}
          </div>
          <div className="flex items-center gap-1.5 px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-xs font-semibold border border-blue-100">
            <Wallet className="w-3 h-3" />
            {FINANCIAL_LABELS[group.FinancialStatus] || group.FinancialStatus}
          </div>
        </div>

        {/* Инфо: Город и Год */}
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div className="flex items-center gap-2 text-gray-600">
            <MapPin className="w-4 h-4 text-[#60519B]" />
            <span>{group.City}</span>
          </div>
          <div className="flex items-center gap-2 text-gray-600">
            <Calendar className="w-4 h-4 text-[#60519B]" />
            <span>Основана в {group.YearOfCreation}</span>
          </div>
        </div>

        {/* Описание */}
        {group.AboutGroup && (
          <p className="text-gray-700 text-sm leading-relaxed line-clamp-3">
            {group.AboutGroup}
          </p>
        )}

        {/* Участники группы */}
        <div>
          <h3 className="text-xs font-bold text-gray-400 uppercase mb-3 flex items-center gap-2">
            Состав группы <div className="h-px flex-1 bg-gray-100"></div>
          </h3>
          <div className="space-y-2">
            {group.Members.map((member) => (
              <div key={member.UserID} className="flex justify-between items-center bg-gray-50 p-2 px-3 rounded-xl border border-gray-100">
                <span className="text-sm font-medium text-gray-900">{member.Name}</span>
                <span className="text-xs font-bold text-[#60519B]">{member.Role}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Жанры */}
        <div className="flex items-center gap-2 overflow-x-auto no-scrollbar">
          <Music className="w-4 h-4 text-gray-400 flex-shrink-0" />
          <div className="flex gap-2">
            {group.Genres.map((genre, idx) => (
              <span key={idx} className="whitespace-nowrap px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-[10px] font-bold uppercase">
                {genre}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}


export function DeleteGroupButton({ groupId, groupName }: { groupId: number, groupName: string }) {
  const [isDeleting, setIsDeleting] = useState(false);
  const navigate = useNavigate();

  const handleDelete = async () => {
    if (!window.confirm(`Вы уверены, что хотите полностью удалить группу "${groupName}"? Это действие необратимо.`)) {
      return;
    }

    setIsDeleting(true);
    try {
      await groupService.deleteGroup(groupId);
      alert('Группа успешно удалена');
      navigate('/profile'); // Уводим пользователя в его личный профиль
    } catch (error: any) {
      if (error.response?.status === 403) {
        alert('Ошибка: Только владелец (OWNER) может удалить группу.');
      } else {
        alert('Не удалось удалить группу. Попробуйте позже.');
      }
      console.error(error);
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <button
      onClick={handleDelete}
      disabled={isDeleting}
      className="flex items-center gap-2 px-4 py-2 bg-red-50 text-red-600 hover:bg-red-100 rounded-xl transition-colors font-semibold border border-red-100 disabled:opacity-50"
    >
      {isDeleting ? (
        <Loader2 className="w-4 h-4 animate-spin" />
      ) : (
        <Trash2 className="w-4 h-4" />
      )}
      Удалить группу
    </button>
  );
}
