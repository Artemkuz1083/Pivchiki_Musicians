import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { 
    ArrowLeft, 
    Edit2, 
    Save, 
    X, 
    Calendar, 
    MapPin, 
    Music, 
    Wallet, 
    Star, 
    Loader2, 
    Trash2, 
    Users,
    Link2,
    Info,
    ShieldAlert,
    Camera
} from 'lucide-react'
import { 
    FullGroupProfile, 
    LevelOfSeriousness, 
    FinancialStatus 
} from '../types/Group'
import { groupService } from '../../api/BandService'

const SERIOUSNESS_LABELS: Record<LevelOfSeriousness, string> = {
    HOBBY: 'Хобби',
    SEMI_PROFESSIONAL: 'Полупрофи',
    PROFESSIONAL: 'Профи',
}

const FINANCIAL_LABELS: Record<FinancialStatus, string> = {
    POOR: 'Без бюджета',
    READY_TO_INVEST: 'Готовы инвестировать',
    LIMITED_BUDGET: 'Ограниченный бюджет',
}

export function GroupProfilePage() {
    const navigate = useNavigate()
    const { id } = useParams<{ id: string }>()
    const groupId = Number(id)
    const [group, setGroup] = useState<FullGroupProfile | null>(null)
    const [formData, setFormData] = useState<FullGroupProfile | null>(null)
    const [isEditing, setIsEditing] = useState(false)
    const [isLoading, setIsLoading] = useState(true)
    const [isSaving, setIsSaving] = useState(false)
    const [isDeleting, setIsDeleting] = useState(false)
    const [isFileUploading, setIsFileUploading] = useState(false)
    const [errorMsg, setErrorMsg] = useState<string | null>(null)

    //Загрузка данных профиля группы
    useEffect(() => {
        const fetchGroupProfile = async () => {
            try {
                setIsLoading(true)
                const res = await groupService.getGroupById(groupId)
                setGroup(res)
                setFormData(res)
                setErrorMsg(null)
            } catch (err: any) {
                console.error("Ошибка при получении профиля группы:", err)
                setErrorMsg("Не удалось загрузить профиль группы или группы с таким ID не существует.")
            } finally {
                setIsLoading(false)
            }
        }

        if (groupId) {
            fetchGroupProfile()
        }
    }, [groupId])

    //Сохранение текстовых полей формы
    const handleSave = async () => {
        if (!formData) return
        try {
            setIsSaving(true)
            setErrorMsg(null)

            const updatedGroup = await groupService.updateGroup({
                id: formData.ID,
                groupName: formData.GroupName,
                aboutGroup: formData.AboutGroup,
                city: formData.City,
                yearOfCreation: Number(formData.YearOfCreation),
                levelOfSerious: formData.LevelOfSerious,
                financialStatus: formData.FinancialStatus,
                link: formData.Link,
                isVisible: formData.IsVisible,
                genres: formData.Genres,
                platforms: formData.Platforms
            })

            setGroup(updatedGroup)
            setIsEditing(false)
            alert('Профиль группы успешно обновлен!')
        } catch (err: any) {
            console.error("Ошибка сохранения профиля:", err)
            if (err.response?.status === 403) {
                setErrorMsg("Недостаточно прав. Только администраторы группы могут изменять её профиль.")
            } else {
                setErrorMsg(err.response?.data?.message || "Ошибка при обновлении профиля группы.")
            }
        } finally {
            setIsSaving(false)
        }
    }

    //Загрузка файла/фотографии на сервер
    const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0]
        if (!file || !formData) return

        try {
            setIsFileUploading(true)
            setErrorMsg(null)
            
            //Вызываем загрузку медиа
            const responseData = await groupService.uploadGroupMedia(formData.ID, file)
            
            // Если сервер возвращает обновленный профиль с новым PhotoURL
            if (responseData && responseData.PhotoURL) {
                setFormData({ ...formData, PhotoURL: responseData.PhotoURL })
                setGroup({ ...group!, PhotoURL: responseData.PhotoURL })
            } else {
                // Если бэк просто говорит "ок", перезапросим профиль для обновления картинки
                const freshData = await groupService.getGroupById(groupId)
                setGroup(freshData)
                setFormData(freshData)
            }
            
            alert('Фотография группы успешно обновлена!')
        } catch (err: any) {
            console.error("Ошибка при загрузке фото:", err)
            setErrorMsg(err.response?.data?.message || "Не удалось загрузить изображение.")
        } finally {
            setIsFileUploading(false)
        }
    }

    //Удаление группы
    const handleDelete = async () => {
        if (!group) return
        if (!window.confirm(`Вы уверены, что хотите полностью удалить группу "${group.GroupName}"? Это действие необратимо.`)) {
            return
        }

        setIsDeleting(true)
        try {
            await groupService.deleteGroup(groupId)
            alert('Группа успешно удалена')
            navigate('/profile')
        } catch (error: any) {
            if (error.response?.status === 403) {
                alert('Ошибка: Только владелец (OWNER) может удалить эту группу.')
            } else {
                alert('Не удалось удалить группу. Попробуйте позже.')
            }
            console.error(error)
        } finally {
            setIsDeleting(false)
        }
    }

    if (isLoading) {
        return (
            <div className='min-h-screen bg-gray-50 flex items-center justify-center'>
                <div className='flex flex-col items-center gap-2'>
                    <Loader2 className='w-8 h-8 animate-spin text-[#60519B]' />
                    <p className='text-gray-500 text-sm font-medium'>Загрузка группы...</p>
                </div>
            </div>
        )
    }

    if (errorMsg && !group) {
        return (
            <div className='min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4 text-center'>
                <ShieldAlert className='w-12 h-12 text-red-500 mb-2' />
                <p className='text-red-600 font-medium mb-4'>{errorMsg}</p>
                <button 
                    onClick={() => navigate('/profile')} 
                    className='px-4 py-2 bg-[#60519B] text-white rounded-xl font-medium shadow-sm'
                >
                    Вернуться в профиль
                </button>
            </div>
        )
    }

    return (
        <div className='min-h-screen bg-gray-50 pb-12'>
            {/* ШАПКА */}
            <div className='bg-[#60519B] text-white p-4 sticky top-0 z-10 shadow-md'>
                <div className='max-w-md mx-auto flex items-center justify-between'>
                    <div className='flex items-center gap-3'>
                        <button
                            onClick={() => navigate('/profile')}
                            className='p-1 hover:bg-white/10 rounded-full transition-colors'
                        >
                            <ArrowLeft className='w-6 h-6' />
                        </button>
                        <h1 className='text-xl font-semibold'>
                            {isEditing ? 'Редактирование' : 'Профиль группы'}
                        </h1>
                    </div>

                    {group && (
                        <button
                            onClick={() => {
                                if (isEditing) setFormData(group)
                                setIsEditing(!isEditing)
                            }}
                            className='p-2 hover:bg-white/10 rounded-lg text-sm font-medium transition-colors flex items-center gap-1'
                        >
                            {isEditing ? <X className='w-4 h-4' /> : <Edit2 className='w-4 h-4' />}
                            {isEditing ? 'Отмена' : 'Редактировать'}
                        </button>
                    )}
                </div>
            </div>

            {/* КОНТЕНТ СТРАНИЦЫ */}
            <div className='max-w-md mx-auto p-4 mt-2'>
                
                {errorMsg && (
                    <div className='bg-red-50 text-red-600 p-3 rounded-xl mb-4 text-sm border border-red-100 font-medium'>
                        {errorMsg}
                    </div>
                )}

                {formData && (
                    <>
                        {isEditing ? (
                            <div className='bg-white rounded-2xl shadow-lg border border-gray-100 p-5 space-y-4'>
                                
                                {/* ИНТЕРАКТИВНАЯ ЗАГРУЗКА ФОТО (Кнопка поверх аватарки) */}
                                <div className='relative w-full h-40 bg-gradient-to-br from-[#60519B] to-[#31323E] rounded-xl overflow-hidden flex items-center justify-center text-white font-bold group shadow-inner'>
                                    {formData.PhotoURL ? (
                                        <img src={formData.PhotoURL} alt="Аватар группы" className='w-full h-full object-cover opacity-50' />
                                    ) : (
                                        <span className='text-lg opacity-80'>{formData.GroupName}</span>
                                    )}
                                    
                                    {/* Слой с кнопкой выбора файла поверх обложки */}
                                    <label className='absolute inset-0 bg-black/40 flex flex-col items-center justify-center gap-1 cursor-pointer opacity-0 group-hover:opacity-100 transition-opacity text-xs font-semibold'>
                                        {isFileUploading ? (
                                            <Loader2 className='w-6 h-6 animate-spin text-white' />
                                        ) : (
                                            <Camera className='w-6 h-6 text-white' />
                                        )}
                                        <span>{isFileUploading ? 'Загрузка...' : 'Изменить фото'}</span>
                                        <input 
                                            type='file' 
                                            accept='image/*' 
                                            className='hidden' 
                                            onChange={handleFileChange}
                                            disabled={isFileUploading}
                                        />
                                    </label>
                                </div>

                                <div>
                                    <label className='block text-xs font-bold text-gray-400 uppercase mb-1'>Название группы *</label>
                                    <input
                                        type='text'
                                        value={formData.GroupName || ''}
                                        onChange={e => setFormData({ ...formData, GroupName: e.target.value })}
                                        className='w-full p-3 border border-gray-200 rounded-xl focus:outline-none focus:border-[#60519B] text-sm'
                                    />
                                </div>

                                <div className='grid grid-cols-2 gap-3'>
                                    <div>
                                        <label className='block text-xs font-bold text-gray-400 uppercase mb-1'>Город</label>
                                        <input
                                            type='text'
                                            value={formData.City || ''}
                                            onChange={e => setFormData({ ...formData, City: e.target.value })}
                                            className='w-full p-3 border border-gray-200 rounded-xl focus:outline-none focus:border-[#60519B] text-sm'
                                        />
                                    </div>
                                    <div>
                                        <label className='block text-xs font-bold text-gray-400 uppercase mb-1'>Год создания</label>
                                        <input
                                            type='number'
                                            value={formData.YearOfCreation || ''}
                                            onChange={e => setFormData({ ...formData, YearOfCreation: Number(e.target.value) })}
                                            className='w-full p-3 border border-gray-200 rounded-xl focus:outline-none focus:border-[#60519B] text-sm'
                                        />
                                    </div>
                                </div>

                                <div>
                                    <label className='block text-xs font-bold text-gray-400 uppercase mb-1'>Уровень серьезности</label>
                                    <select
                                        value={formData.LevelOfSerious}
                                        onChange={e => setFormData({ ...formData, LevelOfSerious: e.target.value as LevelOfSeriousness })}
                                        className='w-full p-3 border border-gray-200 rounded-xl bg-white text-sm focus:outline-none focus:border-[#60519B]'
                                    >
                                        {Object.entries(SERIOUSNESS_LABELS).map(([key, label]) => (
                                            <option key={key} value={key}>{label}</option>
                                        ))}
                                    </select>
                                </div>

                                <div>
                                    <label className='block text-xs font-bold text-gray-400 uppercase mb-1'>Бюджет группы</label>
                                    <select
                                        value={formData.FinancialStatus}
                                        onChange={e => setFormData({ ...formData, FinancialStatus: e.target.value as FinancialStatus })}
                                        className='w-full p-3 border border-gray-200 rounded-xl bg-white text-sm focus:outline-none focus:border-[#60519B]'
                                    >
                                        {Object.entries(FINANCIAL_LABELS).map(([key, label]) => (
                                            <option key={key} value={key}>{label}</option>
                                        ))}
                                    </select>
                                </div>

                                <div>
                                    <label className='block text-xs font-bold text-gray-400 uppercase mb-1'>Описание / Биография</label>
                                    <textarea
                                        rows={4}
                                        value={formData.AboutGroup || ''}
                                        onChange={e => setFormData({ ...formData, AboutGroup: e.target.value })}
                                        className='w-full p-3 border border-gray-200 rounded-xl focus:outline-none focus:border-[#60519B] text-sm resize-none'
                                    />
                                </div>

                                <div>
                                    <label className='block text-xs font-bold text-gray-400 uppercase mb-1'>Ссылка на соцсети / Сайт</label>
                                    <input
                                        type='text'
                                        value={formData.Link || ''}
                                        onChange={e => setFormData({ ...formData, Link: e.target.value })}
                                        className='w-full p-3 border border-gray-200 rounded-xl focus:outline-none focus:border-[#60519B] text-sm'
                                    />
                                </div>

                                <button
                                    onClick={handleSave}
                                    disabled={isSaving}
                                    className='w-full bg-[#60519B] hover:bg-[#4d3f80] text-white py-3.5 rounded-xl mt-4 font-semibold transition-colors flex items-center justify-center gap-2 disabled:opacity-50'
                                >
                                    {isSaving ? <Loader2 className='w-5 h-5 animate-spin' /> : <Save className='w-5 h-5' />}
                                    {isSaving ? 'Сохранение данных...' : 'Сохранить изменения'}
                                </button>
                            </div>
                        ) : (
                            <div className='space-y-6'>
                                <div className='bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden'>
                                    
                                    <div className='h-40 bg-gradient-to-br from-[#60519B] to-[#31323E] relative'>
                                        {group?.PhotoURL && (
                                            <img
                                                src={group.PhotoURL}
                                                alt={group.GroupName}
                                                className='w-full h-full object-cover opacity-60'
                                            />
                                        )}
                                        <div className='absolute bottom-4 left-5 text-white'>
                                            <div className='flex items-center gap-2 mb-1'>
                                                <Users className='w-5 h-5 text-purple-300' />
                                                <span className='text-xs font-bold uppercase tracking-wider opacity-80'>
                                                    Музыкальная группа
                                                </span>
                                            </div>
                                            <h2 className='text-2xl font-bold'>{group?.GroupName}</h2>
                                        </div>
                                    </div>

                                    <div className='p-5 space-y-5'>
                                        <div className='flex flex-wrap gap-2'>
                                            <div className='flex items-center gap-1.5 px-3 py-1 bg-purple-50 text-[#60519B] rounded-full text-xs font-semibold border border-purple-100'>
                                                <Star className='w-3 h-3' />
                                                {group ? (SERIOUSNESS_LABELS[group.LevelOfSerious] || group.LevelOfSerious) : ''}
                                            </div>
                                            <div className='flex items-center gap-1.5 px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-xs font-semibold border border-blue-100'>
                                                <Wallet className='w-3 h-3' />
                                                {group ? (FINANCIAL_LABELS[group.FinancialStatus] || group.FinancialStatus) : ''}
                                            </div>
                                        </div>

                                        <div className='grid grid-cols-2 gap-4 text-sm'>
                                            <div className='flex items-center gap-2 text-gray-600'>
                                                <MapPin className='w-4 h-4 text-[#60519B]' />
                                                <span>{group?.City || 'Город не указан'}</span>
                                            </div>
                                            <div className='flex items-center gap-2 text-gray-600'>
                                                <Calendar className='w-4 h-4 text-[#60519B]' />
                                                <span>Основана в {group?.YearOfCreation || '—'} г.</span>
                                            </div>
                                        </div>

                                        {group?.AboutGroup && (
                                            <div className='space-y-1'>
                                                <h4 className='text-xs font-bold text-gray-400 uppercase tracking-wider flex items-center gap-1'>
                                                    <Info className='w-3.5 h-3.5 text-gray-400' /> Описание
                                                </h4>
                                                <p className='text-gray-700 text-sm leading-relaxed whitespace-pre-line'>
                                                    {group.AboutGroup}
                                                </p>
                                            </div>
                                        )}

                                        {group?.Link && (
                                            <a
                                                href={group.Link}
                                                target='_blank'
                                                rel='noopener noreferrer'
                                                className='mt-2 w-full p-2.5 bg-gray-50 hover:bg-gray-100 border border-gray-200 rounded-xl font-medium text-xs transition-colors flex items-center justify-center gap-2 text-gray-600'
                                            >
                                                <Link2 className='w-3.5 h-3.5 text-[#60519B]' />
                                                Официальная ссылка
                                            </a>
                                        )}

                                        {group?.Members && group.Members.length > 0 && (
                                            <div>
                                                <h3 className='text-xs font-bold text-gray-400 uppercase mb-3 flex items-center gap-2'>
                                                    Состав группы <div className='h-px flex-1 bg-gray-100'></div>
                                                </h3>
                                                <div className='space-y-2'>
                                                    {group.Members.map(member => (
                                                        <div
                                                            key={member.UserID}
                                                            className='flex justify-between items-center bg-gray-50 p-2 px-3 rounded-xl border border-gray-100'
                                                        >
                                                            <span className='text-sm font-medium text-gray-900'>
                                                                {member.Name}
                                                            </span>
                                                            <span className='text-xs font-bold text-[#60519B]'>
                                                                {member.Role}
                                                            </span>
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>
                                        )}

                                        {group?.Genres && group.Genres.length > 0 && (
                                            <div className='flex items-center gap-2 overflow-x-auto no-scrollbar pt-1'>
                                                <Music className='w-4 h-4 text-gray-400 flex-shrink-0' />
                                                <div className='flex gap-2'>
                                                    {group.Genres.map((genre, idx) => (
                                                        <span
                                                            key={idx}
                                                            className='whitespace-nowrap px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-[10px] font-bold uppercase'
                                                        >
                                                            {genre}
                                                        </span>
                                                    ))}
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                </div>

                                <div className='flex justify-center pt-2'>
                                    <button
                                        onClick={handleDelete}
                                        disabled={isDeleting}
                                        className='flex items-center gap-2 px-4 py-2.5 bg-red-50 text-red-600 hover:bg-red-100 rounded-xl transition-colors text-xs font-bold border border-red-100 disabled:opacity-50 shadow-sm'
                                    >
                                        {isDeleting ? <Loader2 className='w-4 h-4 animate-spin' /> : <Trash2 className='w-4 h-4' />}
                                        Полностью удалить группу
                                    </button>
                                </div>
                            </div>
                        )}
                    </>
                )}
            </div>
        </div>
    )
}