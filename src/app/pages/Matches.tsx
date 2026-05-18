import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, Loader2, User, Users, Music } from 'lucide-react'
import { Button } from '../components/ui/button'
import { UserProfile } from '../types'
import { FullGroupProfile } from '../types/Group'
import { matchService } from '../../api/matchService'

type TabType = 'musicians' | 'groups'

export function Matches() {
	const navigate = useNavigate()

	// Состояния для вкладок и данных
	const [activeTab, setActiveTab] = useState<TabType>('musicians')
	const [musicianMatches, setMusicianMatches] = useState<UserProfile[]>([])
	const [groupMatches, setGroupMatches] = useState<FullGroupProfile[]>([])

	const [isLoading, setIsLoading] = useState(true)

	// Первоначальная загрузка обоих списков
	useEffect(() => {
		const loadAllMatches = async () => {
			try {
				setIsLoading(true)
				const [musiciansData, groupsData] = await Promise.all([
					matchService.getMatches(),
					matchService.getGroupMatches()
				])
				setMusicianMatches(musiciansData)
				setGroupMatches(groupsData)
			} catch (e) {
				console.error('Ошибка загрузки мэтчей', e)
			} finally {
				setIsLoading(false)
			}
		}

		loadAllMatches()
	}, [])

	if (isLoading) {
		return (
			<div className='min-h-screen flex items-center justify-center bg-gray-50'>
				<Loader2 className='w-8 h-8 animate-spin text-[#60519B]' />
			</div>
		)
	}

	return (
		<div className='min-h-screen bg-gray-50 pb-10'>
			{/* Header */}
			<div className='bg-[#60519B] text-white sticky top-0 z-10 shadow-md'>
				<div className='max-w-md mx-auto p-4 flex items-center gap-3'>
					<button onClick={() => navigate(-1)} className='p-1 hover:bg-white/10 rounded-full transition-colors'>
						<ArrowLeft className='w-6 h-6' />
					</button>
					<h1 className='text-xl font-semibold'>Мэтчи</h1>
				</div>

				{/* Селектор вкладок (Музыканты / Группы) */}
				<div className='max-w-md mx-auto px-4 pb-3 flex gap-2'>
					<button
						onClick={() => setActiveTab('musicians')}
						className={`flex-1 py-2 text-sm font-semibold rounded-xl border transition-all flex items-center justify-center gap-2 ${activeTab === 'musicians'
								? 'bg-white text-[#60519B] border-white shadow-sm'
								: 'bg-[#4d3f80] text-purple-200 border-transparent hover:bg-[#54458c]'
							}`}
					>
						<User className='w-4 h-4' />
						Музыканты ({musicianMatches.length})
					</button>
					<button
						onClick={() => setActiveTab('groups')}
						className={`flex-1 py-2 text-sm font-semibold rounded-xl border transition-all flex items-center justify-center gap-2 ${activeTab === 'groups'
								? 'bg-white text-[#60519B] border-white shadow-sm'
								: 'bg-[#4d3f80] text-purple-200 border-transparent hover:bg-[#54458c]'
							}`}
					>
						<Users className='w-4 h-4' />
						Группы ({groupMatches.length})
					</button>
				</div>
			</div>

			{/* Контент вкладок */}
			<div className='max-w-md mx-auto p-4'>

				{/* ВКЛАДКА 1: МУЗЫКАНТЫ */}
				{activeTab === 'musicians' && (
					musicianMatches.length === 0 ? (
						<div className='text-center bg-white p-8 rounded-2xl shadow-sm border'>
							<User className='w-10 h-10 mx-auto mb-3 text-gray-400' />
							<p className='text-gray-600 mb-4'>У вас пока нет мэтчей с музыкантами</p>
							<Button onClick={() => navigate('/browse')}>
								Найти музыкантов
							</Button>
						</div>
					) : (
						<div className='space-y-4'>
							{musicianMatches.map(user => (
								<div
									key={user.ID || user.ID}
									onClick={() => navigate(`/profile/${user.ID || user.ID}`)}
									className='bg-white p-4 rounded-xl shadow-sm border cursor-pointer hover:shadow-md transition'
								>
									<div className='flex items-center gap-3'>
										<div className='w-12 h-12 rounded-full bg-gray-200 flex items-center justify-center overflow-hidden flex-shrink-0 border'>
											{(user as any).avatarURL ? (
												<img
													src={(user as any).avatarURL}
													alt={user.UserName}
													className='w-full h-full object-cover'
												/>
											) : (
												<User className='w-6 h-6 text-gray-500' />
											)}
										</div>

										<div>
											<h3 className='font-semibold text-gray-950'>
												{user.UserName || 'Без имени'}
											</h3>
											<p className='text-xs text-gray-500'>{user.City || 'Город не указан'}</p>
										</div>
									</div>

									{user.AboutUser && (
										<div className='mt-3 text-sm text-gray-600 line-clamp-2 leading-relaxed'>
											{user.AboutUser}
										</div>
									)}
								</div>
							))}
						</div>
					)
				)}

				{/* ВКЛАДКА 2: ГРУППЫ */}
				{activeTab === 'groups' && (
					groupMatches.length === 0 ? (
						<div className='text-center bg-white p-8 rounded-2xl shadow-sm border'>
							<Users className='w-10 h-10 mx-auto mb-3 text-gray-400' />
							<p className='text-gray-600 mb-4'>У вас пока нет мэтчей с группами</p>
							<Button onClick={() => navigate('/GroupFeed')}>
								Искать группы
							</Button>
						</div>
					) : (
						<div className='space-y-4'>
							{groupMatches.map(group => {
								// Учитываем возможный разный регистр id/ID и картинок из бэка
								const id = group.ID;
								const name = group.GroupName;
								const img = group.PhotoURL;
								const city = group.City;
								const about = group.AboutGroup;
								const genres = group.Genres;

								return (
									<div
										key={id}
										onClick={() => navigate(`/group/${id}`)}
										className='bg-white p-4 rounded-xl shadow-sm border cursor-pointer hover:shadow-md transition'
									>
										<div className='flex items-center justify-between gap-3'>
											<div className='flex items-center gap-3'>
												<div className='w-12 h-12 rounded-xl bg-purple-50 flex items-center justify-center overflow-hidden flex-shrink-0 border border-purple-100'>
													{img ? (
														<img
															src={img}
															alt={name}
															className='w-full h-full object-cover'
														/>
													) : (
														<Users className='w-6 h-6 text-[#60519B]' />
													)}
												</div>

												<div>
													<h3 className='font-semibold text-gray-950'>
														{name || 'Музыкальная группа'}
													</h3>
													<p className='text-xs text-gray-500'>{city || 'Город не указан'}</p>
												</div>
											</div>
										</div>

										{about && (
											<div className='mt-3 text-sm text-gray-600 line-clamp-2 leading-relaxed'>
												{about}
											</div>
										)}

										{/* Дополнительно выведем теги жанров группы для наглядности */}
										{genres && genres.length > 0 && (
											<div className='mt-3 flex items-center gap-1.5 overflow-x-auto no-scrollbar'>
												<Music className='w-3 h-3 text-gray-400 flex-shrink-0' />
												<div className='flex gap-1'>
													{genres.slice(0, 3).map((genre, idx) => (
														<span
															key={idx}
															className='whitespace-nowrap px-1.5 py-0.5 bg-gray-100 text-gray-600 rounded text-[9px] font-bold uppercase'
														>
															{genre}
														</span>
													))}
													{genres.length > 3 && (
														<span className='text-[9px] font-bold text-gray-400 align-middle'>
															+{genres.length - 3}
														</span>
													)}
												</div>
											</div>
										)}
									</div>
								)
							})}
						</div>
					)
				)}

			</div>
		</div>
	)
}