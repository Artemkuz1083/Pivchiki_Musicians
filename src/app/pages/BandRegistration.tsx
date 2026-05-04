import React, { useState } from 'react';
import { useNavigate } from 'react-router';
import { Loader2, Info } from 'lucide-react';
import { groupService } from '../../api/BandService';
import { Button } from '../components/ui/button';

export default function BandRegistration() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    city: '',
    year: 2024,
    genres: [] as string[],
    financial: 'POOR',
    seriousness: 'HOBBY'
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const group = await groupService.createGroup(formData);
      navigate(`/groups/${group.ID}`);
    } catch (err) {
      alert('Ошибка при создании группы');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-lg mx-auto">
      <form onSubmit={handleSubmit} className="space-y-4">
        <h1 className="text-2xl font-bold">Создание группы</h1>
        <input 
          placeholder="Название"
          className="w-full p-3 border rounded-xl"
          onChange={e => setFormData({...formData, name: e.target.value})}
          required 
        />
        <textarea 
          placeholder="Описание"
          className="w-full p-3 border rounded-xl"
          onChange={e => setFormData({...formData, description: e.target.value})}
        />
        <select 
          className="w-full p-3 border rounded-xl"
          onChange={e => setFormData({...formData, seriousness: e.target.value})}
        >
          <option value="HOBBY">Хобби</option>
          <option value="SEMI_PROFESSIONAL">Полупрофи</option>
          <option value="PROFESSIONAL">Профи</option>
        </select>
        
        <Button type="submit" disabled={loading} className="w-full">
          {loading ? <Loader2 className="animate-spin" /> : 'Создать'}
        </Button>
      </form>
    </div>
  );
}