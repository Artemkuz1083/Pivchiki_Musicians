import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Loader2, Info, ArrowLeft } from 'lucide-react'
import { groupService } from '../../api/BandService'
import { Button } from '../components/ui/button'

export default function BandRegistration() {
	const navigate = useNavigate()
	const [loading, setLoading] = useState(false)
	const [formData, setFormData] = useState({
		name: '',
		description: '',
		city: '',
		year: 2024,
		genres: [] as string[],
		financial: 'POOR',
		seriousness: 'HOBBY',
	})

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault()
		setLoading(true)
		try {
			const group = await groupService.createGroup(formData)
			navigate(`/groups/${group.ID}`)
		} catch (err) {
			alert('Ошибка при создании группы')
		} finally {
			setLoading(false)
		}
	}

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
				{/* Info / Hero Card */}
				<div className='bg-gradient-to-r from-[#60519B] to-[#31323E] rounded-xl p-5 mb-6 text-white shadow-lg'>
					<h2 className='text-lg font-medium mb-1'>Новая группа</h2>
					<p className='text-sm opacity-80'>
						Заполни информацию, чтобы музыканты могли найти вас
					</p>
				</div>

				{/* Form */}
				<form onSubmit={handleSubmit} className='space-y-4'>
					{/* Название */}
					<div className='bg-white rounded-xl p-4 shadow-sm'>
						<p className='text-sm text-gray-500 mb-2'>Название группы</p>
						<input
							placeholder='Например: Midnight Echo'
							className='w-full p-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#60519B]'
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
							onChange={e =>
								setFormData({ ...formData, description: e.target.value })
							}
						/>
					</div>

					{/* Уровень */}
					<div className='bg-white rounded-xl p-4 shadow-sm'>
						<p className='text-sm text-gray-500 mb-2'>Уровень</p>
						<select
							className='w-full p-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#60519B]'
							onChange={e =>
								setFormData({ ...formData, seriousness: e.target.value })
							}
						>
							<option value='HOBBY'>Хобби</option>
							<option value='SEMI_PROFESSIONAL'>Полупрофи</option>
							<option value='PROFESSIONAL'>Профи</option>
						</select>
					</div>

					{/* Submit */}
					<Button
						type='submit'
						disabled={loading}
						className='w-full bg-[#60519B] hover:bg-[#4d3f7e] text-white py-7 text-lg rounded-xl shadow-sm'
					>
						{loading ? (
							<Loader2 className='animate-spin w-5 h-5' />
						) : (
							'Создать группу'
						)}
					</Button>
				</form>
			</div>
		</div>
	)
}
