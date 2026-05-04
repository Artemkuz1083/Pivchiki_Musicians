import { Save, Edit2, X, Loader2 } from 'lucide-react';
import { useState } from 'react';
import { groupService } from '../../api/BandService';
import { FullGroupProfile } from '../types/Group';

export function EditGroupForm({ initialData }: { initialData: FullGroupProfile }) {
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<FullGroupProfile>(initialData);

  const handleSave = async () => {
    setLoading(true);
    try {
      const updated = await groupService.updateGroup(formData);
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
    <div className="space-y-4 p-4 border rounded-2xl bg-gray-50">
      <h3 className="font-bold text-lg">Редактирование</h3>
      
      <div>
        <label className="text-xs font-bold text-gray-400">Название группы</label>
        <input 
          className="w-full p-2 rounded-lg border"
          value={formData.GroupName}
          onChange={e => setFormData({...formData, GroupName: e.target.value})}
        />
      </div>

      <div>
        <label className="text-xs font-bold text-gray-400">О группе</label>
        <textarea 
          className="w-full p-2 rounded-lg border"
          value={formData.AboutGroup || ''}
          onChange={e => setFormData({...formData, AboutGroup: e.target.value})}
        />
      </div>

      <div className="flex gap-2">
        <button 
          onClick={handleSave}
          disabled={loading}
          className="flex-1 bg-[#60519B] text-white py-2 rounded-xl flex justify-center items-center gap-2"
        >
          {loading ? <Loader2 className="animate-spin w-4 h-4" /> : <Save className="w-4 h-4" />}
          Сохранить
        </button>
        <button 
          onClick={() => setIsEditing(false)}
          className="px-4 py-2 border rounded-xl"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}