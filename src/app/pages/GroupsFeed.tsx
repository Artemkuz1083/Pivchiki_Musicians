import React, { useEffect, useState } from 'react';
import { groupService } from '../../api/BandService';
import { Loader2, Music2 } from 'lucide-react';
import { GroupCard } from '../components/BandCard';
import { FullGroupProfile } from '../types/Group';

export default function GroupsFeed() {
  const [groups, setGroups] = useState<FullGroupProfile[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadFeed();
  }, []);

  const loadFeed = async () => {
    setLoading(true);
    try {
      // Загружаем ленту (по умолчанию 10 записей)
      const data = await groupService.getGroupsFeed(20);
      setGroups(data);
    } catch (error) {
      console.error("Ошибка загрузки ленты:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-[#60519B]" />
      </div>
    );
  }

  return (
    <div className="max-w-md mx-auto p-4 pb-24">
      <h1 className="text-2xl font-bold mb-6 flex items-center gap-2">
        <Music2 className="text-[#60519B]" /> Подходящие группы
      </h1>

      {groups.length > 0 ? (
        <div className="space-y-4">
          {groups.map(group => (
            <GroupCard key={group.ID} group={group} />
          ))}
        </div>
      ) : (
        <div className="text-center py-20">
          <p className="text-gray-500">Групп пока нет. Попробуй изменить фильтры или загляни позже!</p>
          <button 
            onClick={loadFeed}
            className="mt-4 text-[#60519B] font-bold underline"
          >
            Обновить ленту
          </button>
        </div>
      )}
    </div>
  );
}