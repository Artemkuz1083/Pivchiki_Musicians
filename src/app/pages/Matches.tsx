import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, Loader2, User } from 'lucide-react'
import { Button } from '../components/ui/button'
import { profileService } from '../../api/profileService'
import { UserProfile } from '../types'
import { matchService } from '../../api/matchService'

export function Matches() {
	const navigate = useNavigate()
	const [matches, setMatches] = useState<UserProfile[]>([])
	const [isLoading, setIsLoading] = useState(true)

	useEffect(() => {
		const loadMatches = async () => {
			try {
				const data = await matchService.getMatches()
				setMatches(data)
			} catch (e) {
				console.error('Ошибка загрузки мэтчей', e)
			} finally {
				setIsLoading(false)
			}
		}

		loadMatches()
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
			<div className='bg-[#60519B] text-white p-4 sticky top-0 z-10 shadow-md'>
				<div className='max-w-md mx-auto flex items-center gap-3'>
					<button onClick={() => navigate(-1)}>
						<ArrowLeft className='w-6 h-6' />
					</button>
					<h1 className='text-xl font-semibold'>Мэтчи</h1>
				</div>
			</div>

			<div className='max-w-md mx-auto p-4'>
				{matches.length === 0 ? (
					<div className='text-center bg-white p-8 rounded-2xl shadow-sm border'>
						<User className='w-10 h-10 mx-auto mb-3 text-gray-400' />
						<p className='text-gray-600 mb-4'>У вас пока нет мэтчей</p>
						<Button onClick={() => navigate('/browse')}>
							Найти музыкантов
						</Button>
					</div>
				) : (
					<div className='space-y-4'>
						{matches.map(user => (
							<div
								key={user.ID}
								onClick={() => navigate(`/profile/${user.ID}`)}
								className='bg-white p-4 rounded-xl shadow-sm border cursor-pointer hover:shadow-md transition'
							>
								<div className='flex items-center gap-3'>
									<div className='w-12 h-12 rounded-full bg-gray-200 flex items-center justify-center'>
										<User className='w-6 h-6 text-gray-500' />
									</div>

									<div>
										<h3 className='font-semibold'>
											{user.UserName || 'Без имени'}
										</h3>
										<p className='text-sm text-gray-500'>{user.City}</p>
									</div>
								</div>

								<div className='mt-3 text-sm text-gray-600 line-clamp-2'>
									{user.AboutUser}
								</div>
							</div>
						))}
					</div>
				)}
			</div>
		</div>
	)
}
