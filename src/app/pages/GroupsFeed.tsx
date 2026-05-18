import React, { useEffect, useState } from 'react'
import { groupService } from '../../api/BandService'
import { Loader2, Music2, ArrowLeft, Heart, X, Sparkles, MessageCircle } from 'lucide-react'
import { GroupCard } from '../components/BandCard'
import { FullGroupProfile } from '../types/Group'
import { useNavigate } from 'react-router-dom'

export default function GroupsFeed() {
    const [groups, setGroups] = useState<FullGroupProfile[]>([])
    const [currentIndex, setCurrentIndex] = useState(0)
    const [loading, setLoading] = useState(true)
    const [matchData, setMatchData] = useState<FullGroupProfile | null>(null) // Для экрана Мэтча
    
    const navigate = useNavigate()

    useEffect(() => {
        loadFeed()
    }, [])

    const loadFeed = async () => {
        setLoading(true)
        try {
            // Передаем лимит 25
            const data = await groupService.getGroupsFeed(25)
            setGroups(data)
            setCurrentIndex(0)
        } catch (error) {
            console.error('Ошибка загрузки ленты:', error)
        } finally {
            setLoading(false)
        }
    }

    const handleSwipe = async (action: 'like' | 'dislike') => {
        if (groups.length === 0 || currentIndex >= groups.length) return

        const currentGroup = groups[currentIndex]

        try {
            // Отправляем свайп на бэкенд
            const res = await groupService.swipeGroup(currentGroup.ID, action)
            
            // Если получили взаимный лайк — прерываемся на экран мэтча
            if (action === 'like' && res.is_match) {
                setMatchData(currentGroup)
            }
        } catch (err) {
            console.error('Не удалось обработать свайп:', err)
        }

        // Переходим к следующей карточке
        setCurrentIndex(prev => prev + 1)
    }

    if (loading) {
        return (
            <div className='min-h-screen bg-[#F8F9FD] flex flex-col justify-center items-center'>
                <Loader2 className='w-10 h-10 animate-spin text-[#60519B]' />
            </div>
        )
    }

    const activeGroup = groups[currentIndex]
    const isFeedEmpty = !activeGroup

    return (
        <div className='min-h-screen bg-[#F8F9FD] flex flex-col relative overflow-hidden'>
            {/* HEADER */}
            <div className='bg-[#60519B] text-white p-4 sticky top-0 z-10 shadow-md'>
                <div className='max-w-md mx-auto flex items-center justify-between'>
                    <div className='flex items-center gap-3'>
                        <button
                            onClick={() => navigate(-1)}
                            className='p-2 hover:bg-white/10 rounded-full transition'
                        >
                            <ArrowLeft className='w-6 h-6' />
                        </button>
                        <h1 className='text-lg font-semibold flex items-center gap-2'>
                            <Music2 className='w-5 h-5' />
                            Поиск групп
                        </h1>
                    </div>
                </div>
            </div>

            <main className='flex-1 flex flex-col items-center justify-center p-4 max-w-md mx-auto w-full'>
                {!isFeedEmpty ? (
                    <div className='w-full flex-1 flex flex-col justify-between py-4'>
                        {/* Сама карточка группы */}
                        <div className='relative w-full flex-1 transition-all duration-300 transform scale-100'>
                            <GroupCard group={activeGroup} />
                        </div>

                        {/* ТИНДЕР-КНОПКИ */}
                        <div className='flex items-center justify-center gap-6 mt-6 pb-4'>
                            {/* Кнопка Дизлайк */}
                            <button
                                onClick={() => handleSwipe('dislike')}
                                className='w-16 h-16 bg-white rounded-full flex items-center justify-center text-red-500 shadow-lg hover:scale-110 active:scale-95 border border-red-50 transition'
                            >
                                <X className='w-8 h-8' />
                            </button>

                            {/* Кнопка Лайк */}
                            <button
                                onClick={() => handleSwipe('like')}
                                className='w-16 h-16 bg-[#60519B] rounded-full flex items-center justify-center text-white shadow-lg hover:scale-110 active:scale-95 transition'
                            >
                                <Heart className='w-8 h-8 fill-current' />
                            </button>
                        </div>
                    </div>
                ) : (
                    /* ПУСТАЯ ЛЕНТА */
                    <div className='flex flex-col items-center justify-center text-center py-20 bg-white rounded-3xl shadow-sm border border-gray-100 px-6 w-full'>
                        <Sparkles className='w-12 h-12 text-yellow-400 mb-4 animate-pulse' />
                        <p className='text-gray-600 font-medium text-lg'>Вы посмотрели всех!</p>
                        <p className='text-gray-400 text-sm mt-1 mb-6'>
                            Новые группы появятся, как только кто-то зарегистрируется в вашем регионе.
                        </p>
                        <button
                            onClick={loadFeed}
                            className='px-6 py-3 bg-[#60519B] text-white rounded-xl font-semibold hover:scale-[1.02] transition active:scale-95 shadow-md'
                        >
                            Проверить обновления
                        </button>
                    </div>
                )}
            </main>

            {/* ПОЛНОЭКРАННОЕ ОКНО "IT'S A MATCH!" */}
            {matchData && (
                <div className='absolute inset-0 bg-[#1E1B2E]/95 z-50 flex flex-col items-center justify-center p-6 text-center animate-in fade-in duration-300'>
                    <div className='animate-bounce bg-yellow-400 p-4 rounded-full shadow-lg mb-2'>
                        <Sparkles className='w-10 h-10 text-white' />
                    </div>
                    
                    <h2 className='text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-pink-400 via-purple-400 to-indigo-400 uppercase tracking-widest mb-2'>
                        Это Мэтч!
                    </h2>
                    
                    <p className='text-gray-300 text-md max-w-xs mb-8'>
                        Вы и группа <span className='text-white font-bold'>{matchData.GroupName}</span> лайкнули друг друга!
                    </p>

                    {/* Аватарка или Заглушка группы */}
                    <div className='w-40 h-40 rounded-full border-4 border-[#60519B] shadow-2xl overflow-hidden mb-12 bg-zinc-800 flex items-center justify-center'>
                        {matchData.PhotoURL ? (
                            <img src={matchData.PhotoURL} alt='Group' className='w-full h-full object-cover' />
                        ) : (
                            <Music2 className='w-16 h-16 text-gray-500' />
                        )}
                    </div>

                    <div className='flex flex-col gap-4 w-full max-w-xs'>
                        <button
                            onClick={() => {
                                setMatchData(null);
                                navigate('/matches'); // Отправим на страницу списка взаимных лайков
                            }}
                            className='w-full py-4 bg-gradient-to-r from-[#60519B] to-purple-600 text-white font-bold rounded-xl shadow-lg flex items-center justify-center gap-2 hover:opacity-90 transition'
                        >
                            <MessageCircle className='w-5 h-5' />
                            Посмотреть все мэтчи
                        </button>
                        
                        <button
                            onClick={() => setMatchData(null)}
                            className='w-full py-3 bg-white/10 text-gray-300 font-semibold rounded-xl hover:bg-white/20 transition'
                        >
                            Продолжить поиск
                        </button>
                    </div>
                </div>
            )}
        </div>
    )
}