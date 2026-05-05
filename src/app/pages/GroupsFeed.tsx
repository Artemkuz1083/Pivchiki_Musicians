import React, { useEffect, useState } from 'react'
import { groupService } from '../../api/BandService'
import { Loader2, Music2, ArrowLeft } from 'lucide-react'
import { GroupCard } from '../components/BandCard'
import { FullGroupProfile } from '../types/Group'
import { useNavigate } from 'react-router-dom'

export default function GroupsFeed() {
	const [groups, setGroups] = useState<FullGroupProfile[]>([])
	const [loading, setLoading] = useState(true)
	const navigate = useNavigate()

	useEffect(() => {
		loadFeed()
	}, [])

	const loadFeed = async () => {
		setLoading(true)
		try {
			const data = await groupService.getGroupsFeed(20)
			setGroups(data)
		} catch (error) {
			console.error('Ошибка загрузки ленты:', error)
		} finally {
			setLoading(false)
		}
	}

	if (loading) {
		return (
			<div className='min-h-screen bg-[#F8F9FD] flex flex-col'>
				{/* HEADER */}
				<div className='bg-[#60519B] text-white p-4 sticky top-0 z-10 shadow-md'>
					<div className='max-w-md mx-auto flex items-center gap-3'>
						<button
							onClick={() => navigate(-1)}
							className='p-2 hover:bg-white/10 rounded-full transition'
						>
							<ArrowLeft className='w-6 h-6' />
						</button>
						<h1 className='text-lg font-semibold'>Подходящие группы</h1>
					</div>
				</div>

				<div className='flex-1 flex items-center justify-center'>
					<Loader2 className='w-10 h-10 animate-spin text-[#60519B]' />
				</div>
			</div>
		)
	}

	return (
		<div className='min-h-screen bg-[#F8F9FD] flex flex-col'>
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
							Группы
						</h1>
					</div>
				</div>
			</div>

			{/* CONTENT */}
			<main className='flex-1 p-4'>
				<div className='max-w-md mx-auto'>
					{groups.length > 0 ? (
						<div className='space-y-4'>
							{groups.map(group => (
								<div key={group.ID} className='animate-in fade-in duration-300'>
									<GroupCard group={group} />
								</div>
							))}
						</div>
					) : (
						<div className='flex flex-col items-center justify-center text-center py-20 bg-white rounded-3xl shadow-sm border border-gray-100'>
							<Music2 className='w-12 h-12 text-gray-300 mb-4' />

							<p className='text-gray-600 font-medium'>Групп пока нет</p>

							<p className='text-gray-400 text-sm mt-1 mb-6'>
								Попробуй изменить фильтры или загляни позже
							</p>

							<button
								onClick={loadFeed}
								className='px-5 py-3 bg-[#60519B] text-white rounded-xl font-semibold hover:scale-[1.02] transition active:scale-95'
							>
								Обновить ленту
							</button>
						</div>
					)}
				</div>
			</main>
		</div>
	)
}
