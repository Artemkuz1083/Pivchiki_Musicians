import { Save, Edit2, X, Loader2 } from 'lucide-react';
import { useState } from 'react';
import { groupService } from '../../api/BandService';
import { FullGroupProfile } from '../types/Group';
import GroupPhotoUpload from './BandPhotoUpload';

export function EditGroupForm({ initialData }: { initialData: FullGroupProfile }) {
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<FullGroupProfile>(initialData);

  const groupId = formData.ID;
  const currentPhoto = formData.PhotoURL || '';

  const handleSave = async () => {
    setLoading(true);
    try {
      // Трансформируем PascalCase из стейта в camelCase для метода сервиса
      const updated = await groupService.updateGroup({
        id: formData.ID,
        groupName: formData.GroupName,
        aboutGroup: formData.AboutGroup,
        city: formData.City,
        yearOfCreation: formData.YearOfCreation,
        levelOfSerious: formData.LevelOfSerious,
        financialStatus: formData.FinancialStatus,
        link: formData.Link,
        isVisible: formData.IsVisible,
        genres: formData.Genres,
        platforms: formData.Platforms,
        photoURL: formData.PhotoURL
      } as any); // Приведение к any снимает строгий конфликт, если метод возвращает старый тип

      alert('Профиль обновлен!');
      setFormData(updated);
      setIsEditing(false);
    } catch (error: any) {
      if (error.response?.status === 403) {
        alert('У вас нет прав администратора для редактирования.');
      } else {
        alert('Ошибка при сохранении.');
      }
    } finally {
      setLoading(false);
    }
  };

  if (!isEditing) {
    return (
      <button 
        onClick={() => setIsEditing(true)}
        className="flex items-center gap-2 text-[#60519B] font-bold"
      >
        <Edit2 className="w-4 h-4" /> Редактировать профиль
      </button>
    );
  }

  return (
    <div className="space-y-4 p-4 border rounded-2xl bg-gray-50 animate-in fade-in duration-200">
      <h3 className="font-bold text-lg">Редактирование профиля</h3>
      
      <div className="bg-white p-4 rounded-xl border border-gray-100 shadow-sm">
        <label className="block text-xs font-bold text-gray-400 text-center uppercase tracking-wider mb-2">
          Логотип группы
        </label>
        
        <GroupPhotoUpload 
          groupId={Number(groupId)} 
          currentPhotoUrl={currentPhoto} 
          onUploadSuccess={(newUrl: string) => {
            setFormData(prev => ({ ...prev, PhotoURL: newUrl }));
          }} 
        />
      </div>

      <div>
        <label className="text-xs font-bold text-gray-400">Название группы</label>
        <input 
          className="w-full p-2 rounded-lg border bg-white"
          value={formData.GroupName || ''}
          onChange={e => setFormData({ ...formData, GroupName: e.target.value })}
        />
      </div>

      <div>
        <label className="text-xs font-bold text-gray-400">О группе</label>
        <textarea 
          rows={3}
          className="w-full p-2 rounded-lg border bg-white resize-none"
          value={formData.AboutGroup || ''}
          onChange={e => setFormData({ ...formData, AboutGroup: e.target.value })}
        />
      </div>

      <div className="flex gap-2 pt-2">
        <button 
          onClick={handleSave}
          disabled={loading}
          className="flex-1 bg-[#60519B] text-white py-2.5 rounded-xl flex justify-center items-center gap-2 font-semibold shadow-md disabled:opacity-50"
        >
          {loading ? <Loader2 className="animate-spin w-4 h-4" /> : <Save className="w-4 h-4" />}
          Сохранить текст
        </button>
        <button 
          onClick={() => setIsEditing(false)}
          className="px-4 py-2.5 border rounded-xl bg-white text-gray-500"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}