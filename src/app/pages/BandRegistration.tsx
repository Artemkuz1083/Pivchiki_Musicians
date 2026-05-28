import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Loader2, ArrowLeft } from 'lucide-react'
import { groupService } from '../../api/BandService'
import { Button } from '../components/ui/button'
import { CITIES } from '../types/index'

export default function BandRegistration() {
    const navigate = useNavigate()
    const [loading, setLoading] = useState(false)

    const [formData, setFormData] = useState({
        name: '',
        description: '',
        city: '',
        year: new Date().getFullYear(),
        genres: [] as string[],
        financial: 'POOR',
        seriousness: 'HOBBY',
    })

    const handleSubmit = async (e: React.FormEvent) => {
        if (e && typeof e.preventDefault === 'function') {
            e.preventDefault();
        }
        
        try {
            setLoading(true);
            console.log('Текущий formData:', formData);

            if (!groupService || !groupService.createGroup) {
                throw new Error('groupService или метод createGroup не импортирован или undefined!');
            }

            const payload = {
                ...formData,
                year: Number(formData.year || new Date().getFullYear()),
            };
            console.log('Отправляем payload:', payload);

            const group = await groupService.createGroup(payload);
            console.log('Бэкенд успешно ответил:', group);
            localStorage.setItem('my_group_id', String(group.ID));
            
            const groupId = group?.ID;
            console.log('Распознанный groupId:', groupId);

            if (groupId) {
                console.log(`Переходим на: /groups/${groupId}`);
                navigate(`/groups/${groupId}`);
            } else {
                console.warn('ID группы пустой в ответе бэкенда! Переходим в профиль.');
                alert('Группа создана, но бэкенд не вернул ID. Переходим в профиль.');
                navigate('/profile');
            }

        } catch (err: any) {
            console.error('КРИТИЧЕСКАЯ ОШИБКА В ТЕЧЕНИИ SUBMIT:', err);
            const errorMessage = err?.message || 'Неизвестная ошибка';
            const serverDetail = err?.response?.data ? JSON.stringify(err.response.data) : '';
            
            alert(`СТОП! Ошибка поймана:\n\nТекст: ${errorMessage}\n\nДетали сервера: ${serverDetail}`);
        } finally {
            console.log('=== END HANDLESUBMIT ===');
            setLoading(false);
        }
    };

    return (
        <div className='min-h-screen bg-gray-50 pb-10'>
            {/* Header */}
            <div className='bg-[#60519B] text-white p-4 sticky top-0 z-10 shadow-md'>
                <div className='max-w-md mx-auto flex items-center gap-3'>
                    <button
                        onClick={() => navigate(-1)}
                        className='p-1 hover:bg-white/10 rounded-full transition-colors'
                    >
                        <ArrowLeft className='w-6 h-6' />
                    </button>
                    <h1 className='text-xl font-semibold'>Создание группы</h1>
                </div>
            </div>

            <div className='max-w-md mx-auto p-4'>
                {/* Hero */}
                <div className='bg-gradient-to-r from-[#60519B] to-[#31323E] rounded-xl p-5 mb-6 text-white shadow-lg'>
                    <h2 className='text-lg font-medium mb-1'>Новая группа</h2>
                    <p className='text-sm opacity-80'>
                        Заполни информацию, чтобы музыканты могли найти вас
                    </p>
                </div>

                <form onSubmit={handleSubmit} className='space-y-4'>
                    {/* Название */}
                    <div className='bg-white rounded-xl p-4 shadow-sm'>
                        <p className='text-sm text-gray-500 mb-2'>Название группы</p>
                        <input
                            placeholder='Например: Midnight Echo'
                            className='w-full p-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#60519B]'
                            value={formData.name}
                            onChange={e => setFormData({ ...formData, name: e.target.value })}
                            required
                        />
                    </div>

                    {/* Описание */}
                    <div className='bg-white rounded-xl p-4 shadow-sm'>
                        <p className='text-sm text-gray-500 mb-2'>Описание</p>
                        <textarea
                            placeholder='Расскажите о стиле, целях и участниках'
                            className='w-full p-3 border border-gray-200 rounded-xl min-h-[100px] resize-none focus:outline-none focus:ring-2 focus:ring-[#60519B]'
                            value={formData.description}
                            onChange={e =>
                                setFormData({
                                    ...formData,
                                    description: e.target.value,
                                })
                            }
                        />
                    </div>

                    {/* Город */}
                    <div className='bg-white rounded-xl p-4 shadow-sm'>
                        <p className='text-sm text-gray-500 mb-2'>Город</p>
                        <select
                            className='w-full p-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#60519B]'
                            value={formData.city}
                            onChange={e => setFormData({ ...formData, city: e.target.value })}
                            required
                        >
                            <option value='' disabled>
                                Выберите город
                            </option>
                            {CITIES.map(city => (
                                <option key={city} value={city}>
                                    {city}
                                </option>
                            ))}
                        </select>
                    </div>

                    {/* Год создания */}
                    <div className='bg-white rounded-xl p-4 shadow-sm'>
                        <p className='text-sm text-gray-500 mb-2'>Год создания группы</p>
                        <input
                            type='number'
                            min='1950'
                            max={new Date().getFullYear()}
                            placeholder='Например: 2024'
                            className='w-full p-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#60519B]'
                            value={formData.year}
                            onChange={e => setFormData({ ...formData, year: Number(e.target.value) })}
                            required
                        />
                    </div>

                    {/* Уровень */}
                    <div className='bg-white rounded-xl p-4 shadow-sm'>
                        <p className='text-sm text-gray-500 mb-2'>Уровень</p>
                        <select
                            className='w-full p-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#60519B]'
                            value={formData.seriousness}
                            onChange={e =>
                                setFormData({ ...formData, seriousness: e.target.value })
                            }
                        >
                            <option value='HOBBY'>Хобби</option>
                            <option value='SEMI_PROFESSIONAL'>Полупрофи</option>
                            <option value='PROFESSIONAL'>Профи</option>
                        </select>
                    </div>

                    {/* Финансы */}
                    <div className='bg-white rounded-xl p-4 shadow-sm'>
                        <p className='text-sm text-gray-500 mb-2'>Финансовый уровень</p>
                        <select
                            className='w-full p-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#60519B]'
                            value={formData.financial}
                            onChange={e =>
                                setFormData({ ...formData, financial: e.target.value })
                            }
                        >
                            <option value='POOR'>Без бюджета</option>
                            <option value='MEDIUM'>Средний</option>
                            <option value='RICH'>Есть бюджет</option>
                        </select>
                    </div>

                    <button
                        type='submit'
                        disabled={loading}
                        className='w-full bg-[#60519B] hover:bg-[#4d3f7e] text-white py-7 text-lg rounded-xl shadow-sm flex items-center justify-center transition-colors disabled:opacity-50'
                    >
                        {loading ? (
                            <Loader2 className='animate-spin w-5 h-5' />
                        ) : (
                            'Создать группу'
                        )}
                    </button>
                </form>
            </div>
        </div>
    )
}