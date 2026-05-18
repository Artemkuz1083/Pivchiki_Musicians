import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
    ArrowLeft,
    Edit,
    Eye,
    Loader2,
    Heart,
    Users,
    Music2,
} from 'lucide-react'
import { Button } from '../components/ui/button'
import { ProfileCard } from '../components/ProfileCard'
import { UserProfile } from '../types'
import { profileService } from '../../api/profileService'
import { useAuth } from '../../context/AuthContext'
import { groupService } from '../../api/BandService'

export function Profile() {
    const navigate = useNavigate()
    const [profile, setProfile] = useState<UserProfile | null>(null)
    const [isLoading, setIsLoading] = useState(true)
    const { logout } = useAuth()

    useEffect(() => {
        let isMounted = true

        const loadProfile = async () => {
            try {
                const data = await profileService.getMyProfile()

                if (!isMounted) return

                if (!data?.ID) {
                    logout()
                    navigate('/login', { replace: true })
                    return
                }

                setProfile(data)
                setIsLoading(false)
            } catch (error: any) {
                if (!isMounted) return

                if (error?.response?.status === 401) {
                    logout()
                    navigate('/login', { replace: true })
                } else {
                    setIsLoading(false)
                }
            }
        }

        loadProfile()

        return () => {
            isMounted = false
        }
    }, [navigate, logout])

    const calculateProgress = (p: UserProfile | null): number => {
        if (!p) return 0

        const fields = [
            !!p.UserName,
            !!p.AboutUser,
            !!p.City,
            (p.Genres || []).length > 0,
            (p.Instruments || []).length > 0,
            !!p.Contact,
            p.PerformancExperience !== 'NEVER',
        ]
        const completed = fields.filter(Boolean).length
        return Math.round((completed / fields.length) * 100)
    }

    const progress = calculateProgress(profile)

    if (isLoading) {
        return (
            <div className='min-h-screen bg-gray-50 flex items-center justify-center'>
                <Loader2 className='w-8 h-8 text-[#60519B] animate-spin' />
            </div>
        )
    }

    if (!profile) {
        return (
            <div className='min-h-screen bg-gray-50 flex items-center justify-center'>
                <p className='text-gray-500'>Загрузка...</p>
            </div>
        )
    }

    if (!profile.ID) {
        return null
    }

    const handleMyGroup = async () => {
        try {
            const groups = await groupService.getGroupsFeed(10)
            const safeGroups = Array.isArray(groups) ? groups : []

            const myGroup = safeGroups.find(g =>
                g.Members?.some(m => m.UserID === profile.ID),
            )

            if (myGroup && myGroup.ID) {
                navigate(`/groups/${myGroup.ID}`)
                return
            }
        } catch (e) {
            console.error(e)
        }

        // Фоллбек к localStorage
        const savedGroupId = localStorage.getItem('my_group_id')

        if (savedGroupId) {
            navigate(`/groups/${savedGroupId}`)
        } else {
            alert('У вас еще не создана группа или сессия устарела. Направляем на регистрацию.')
            navigate('/BandRegistration')
        }
    }

    return (
        <div className='min-h-screen bg-gray-50 pb-10'>
            <div className='bg-[#60519B] text-white p-4 sticky top-0 z-10 shadow-md'>
                <div className='max-w-md mx-auto flex items-center gap-3'>
                    <button
                        onClick={() => navigate('/')}
                        className='p-1 hover:bg-white/10 rounded-full transition-colors'
                    >
                        <ArrowLeft className='w-6 h-6' />
                    </button>
                    <h1 className='text-xl font-semibold'>Мой профиль</h1>
                </div>
            </div>

            <div className='max-w-md mx-auto p-4'>
                <div className='bg-gradient-to-r from-[#60519B] to-[#31323E] rounded-xl p-5 mb-6 text-white shadow-lg'>
                    <div className='flex items-center justify-between mb-2'>
                        <h2 className='text-lg font-medium opacity-90'>
                            Заполнение анкеты
                        </h2>
                        <div className='text-2xl font-bold'>{progress}%</div>
                    </div>
                    <div className='bg-white/20 rounded-full h-2.5 mb-2 overflow-hidden'>
                        <div
                            className='bg-white h-full transition-all duration-500 ease-out'
                            style={{ width: `${progress}%` }}
                        ></div>
                    </div>
                    <p className='text-xs opacity-70'>
                        {progress < 100
                            ? 'Заполните все данные, чтобы вас чаще находили'
                            : 'Ваш профиль полностью готов!'}
                    </p>
                </div>

                <ProfileCard profile={profile} />

                <div className='space-y-3 mt-6'>
                    <Button
                        onClick={() => navigate('/editProfile')}
                        className='w-full bg-[#60519B] hover:bg-[#4d3f7e] text-white py-7 text-lg rounded-xl shadow-sm'
                    >
                        <Edit className='w-5 h-5 mr-2' />
                        Редактировать
                    </Button>

                    <Button
                        onClick={() => navigate('/matches')}
                        className='w-full bg-[#F3F0FF] hover:bg-[#E5E0FF] text-[#60519B] py-7 text-lg rounded-xl shadow-sm border border-[#D6D1F5]'
                    >
                        <Heart className='w-5 h-5 mr-2' />
                        Мэтчи
                    </Button>

                    <Button
                        onClick={() => navigate('/GroupFeed')}
                        className='w-full bg-[#E6F7FF] hover:bg-[#D6F0FF] text-[#1E88E5] py-7 text-lg rounded-xl shadow-sm border border-[#BFE3FF]'
                    >
                        <Music2 className='w-5 h-5 mr-2' />
                        Поиск групп
                    </Button>

                    <Button
                        onClick={handleMyGroup}
                        className='w-full bg-[#E9E6FF] hover:bg-[#DDD8FF] text-[#60519B] py-7 text-lg rounded-xl shadow-sm border border-[#D6D1F5]'
                    >
                        <Users className='w-5 h-5 mr-2' />
                        Моя группа
                    </Button>

                    <Button
                        onClick={() => navigate('/browse')}
                        className='w-full bg-white text-[#31323E] hover:bg-gray-50 py-7 text-lg rounded-xl border-2 border-[#BFC0D1] transition-colors shadow-sm'
                    >
                        <Eye className='w-5 h-5 mr-2' />
                        Поиск музыкантов
                    </Button>

                    <Button
                        onClick={() => {
                            logout()
                            navigate('/browse')
                        }}
                        className='w-full bg-white text-red-500 hover:bg-red-50 py-6 text-lg rounded-xl border-2 border-red-200 transition-colors shadow-sm'
                    >
                        Выйти из аккаунта
                    </Button>
                </div>
            </div>
        </div>
    )
}