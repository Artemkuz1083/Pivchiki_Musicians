import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, Check, Loader2, User, Music, ImageIcon } from 'lucide-react'
import { Button } from '../components/ui/button'
import { Checkbox } from '../components/ui/checkbox'
import { Label } from '../components/ui/label'
import { Input } from '../components/ui/input'
import { RadioGroup, RadioGroupItem } from '../components/ui/radio-group'
import { profileService } from '../../api/profileService'

import {
	INSTRUMENTS,
	GENRES,
	SKILL_LEVELS,
	InstrumentSkill,
	PerformanceExperience,
} from '../types'

export const EditProfile = () => {
	const navigate = useNavigate()

	// PROFILE STATE
	const [userName, setUserName] = useState('')
	const [aboutUser, setAboutUser] = useState('')
	const [age, setAge] = useState<number | ''>('')
	const [city, setCity] = useState('')
	const [contact, setContact] = useState('')
	const [link, setLink] = useState('')

	const [isVisible, setIsVisible] = useState(true)
	const [theoryLevel, setTheoryLevel] = useState(1)
	const [experience, setExperience] = useState<PerformanceExperience>('NEVER')

	// music
	const [selectedGenres, setSelectedGenres] = useState<string[]>([])
	const [selectedInstruments, setSelectedInstruments] = useState<string[]>([])
	const [instrumentLevels, setInstrumentLevels] = useState<
		Record<string, number>
	>({})

	// media
	// FILES (новые, которые пользователь выбрал)
	const [photo, setPhoto] = useState<File | null>(null)
	const [audio, setAudio] = useState<File | null>(null)

	// URL (то, что пришло с сервера)
	const [photoURL, setPhotoURL] = useState<string>('')
	const [audioURL, setAudioURL] = useState<string>('')
	const [isSaving, setIsSaving] = useState(false)

	// LOAD PROFILE (PRE-FILL)
	useEffect(() => {
		profileService.getMyProfile().then(profile => {
			setUserName(profile.UserName || '')
			setAboutUser(profile.AboutUser || '')
			setAge(profile.Age ?? 0)
			setCity(profile.City || '')
			setContact(profile.Contact || '')
			setLink(profile.Link || '')
			setIsVisible(profile.IsVisible ?? true)
			setTheoryLevel(profile.TheoryLevel ?? 1)
			setExperience(profile.PerformancExperience || 'NEVER')

			setSelectedGenres(profile.Genres || [])

			const instruments = profile.Instruments || []
			setSelectedInstruments(instruments.map(i => i.Instrument))

			const levels: Record<string, number> = {}
			instruments.forEach(i => {
				levels[i.Instrument] = i.InstrumentProficiencyLevel
			})
			setInstrumentLevels(levels)

			// 👉 если используешь медиа — сразу сюда
			setPhotoURL(profile.PhotoURL || '')
			setAudioURL(profile.AudioURL || '')
		})
	}, [])

	// TOGGLES
	const toggleGenre = (g: string) => {
		setSelectedGenres(prev =>
			prev.includes(g) ? prev.filter(x => x !== g) : [...prev, g],
		)
	}

	const toggleInstrument = (i: string) => {
		setSelectedInstruments(prev =>
			prev.includes(i) ? prev.filter(x => x !== i) : [...prev, i],
		)
	}

	const setInstrumentLevel = (i: string, level: number) => {
		setInstrumentLevels(prev => ({ ...prev, [i]: level }))
	}

	// SUBMIT
	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault()
		setIsSaving(true)

		try {
			await profileService.updateProfile({
				UserName: userName,
				AboutUser: aboutUser,
				Age: age === '' ? undefined : Number(age),
				City: city,
				Contact: contact,
				Genres: selectedGenres,
				Instruments: selectedInstruments.map(inst => ({
					Instrument: inst,
					InstrumentProficiencyLevel: instrumentLevels[inst] || 0,
				})),
				IsVisible: isVisible,
				Link: link,
				PerformancExperience: experience,
				TheoryLevel: theoryLevel,
			})
			if (photo) await profileService.uploadMedia(photo, 'photo')
			if (audio) await profileService.uploadMedia(audio, 'audio')

			navigate('/profile', { replace: true })
		} catch (e) {
			console.error(e)
			alert('Ошибка обновления профиля')
		} finally {
			setIsSaving(false)
		}
	}
	// UI
	return (
		<div className='min-h-screen bg-[#F8F9FD]'>
			{/* HEADER */}
			<div className='bg-[#60519B] text-white p-4 sticky top-0 z-20 shadow-lg'>
				<div className='max-w-md mx-auto flex items-center gap-3'>
					<button
						onClick={() => navigate(-1)}
						className='p-1 hover:bg-white/10 rounded-full'
					>
						<ArrowLeft className='w-6 h-6' />
					</button>
					<h1 className='text-xl font-bold'>Редактирование профиля</h1>
				</div>
			</div>

			<form
				onSubmit={handleSubmit}
				className='max-w-md mx-auto p-4 pb-32 space-y-6'
			>
				{/* BASIC */}
				<div className='bg-white p-5 rounded-2xl shadow-sm space-y-3'>
					<div className='flex items-center gap-2 font-bold'>
						<User className='w-5 h-5 text-[#60519B]' />
						Основное
					</div>

					<Input
						value={userName}
						onChange={e => setUserName(e.target.value)}
						placeholder='Имя'
					/>
					<textarea
						value={aboutUser}
						onChange={e => setAboutUser(e.target.value)}
						placeholder='О себе'
						className='w-full border p-3 rounded-xl'
					/>
					<Input
						value={city}
						onChange={e => setCity(e.target.value)}
						placeholder='Город'
					/>
					<Input
						value={contact}
						onChange={e => setContact(e.target.value)}
						placeholder='Контакт'
					/>
					<Input
						value={link}
						onChange={e => setLink(e.target.value)}
						placeholder='Ссылка'
					/>
					<Input
						type='number'
						value={age}
						onChange={e => setAge(Number(e.target.value))}
						placeholder='Возраст'
					/>
				</div>

				{/* EXPERIENCE */}
				<div className='bg-white p-5 rounded-2xl shadow-sm border border-gray-100'>
					<h2 className='font-bold text-gray-800 mb-4 text-lg'>
						Опыт выступлений
					</h2>

					<RadioGroup
						value={experience}
						onValueChange={val => setExperience(val as PerformanceExperience)}
					>
						<div className='space-y-2'>
							<div className='flex items-center gap-3'>
								<RadioGroupItem value='NEVER' id='exp-never' />
								<Label htmlFor='exp-never'>Нет опыта</Label>
							</div>

							<div className='flex items-center gap-3'>
								<RadioGroupItem value='LOCAL_GIGS' id='exp-local' />
								<Label htmlFor='exp-local'>Локальные выступления</Label>
							</div>

							<div className='flex items-center gap-3'>
								<RadioGroupItem value='TOURS' id='exp-tours' />
								<Label htmlFor='exp-tours'>Туры</Label>
							</div>

							<div className='flex items-center gap-3'>
								<RadioGroupItem value='PROFESSIONAL' id='exp-pro' />
								<Label htmlFor='exp-pro'>Профессионально</Label>
							</div>
						</div>
					</RadioGroup>
				</div>

				{/* GENRES */}
				<div className='bg-white p-5 rounded-2xl'>
					<h2 className='font-bold mb-3'>Жанры</h2>

					<div className='flex flex-wrap gap-2'>
						{GENRES.map(g => (
							<button
								type='button'
								key={g}
								onClick={() => toggleGenre(g)}
								className={`px-3 py-1 rounded-xl text-sm ${
									selectedGenres.includes(g)
										? 'bg-[#60519B] text-white'
										: 'bg-gray-100'
								}`}
							>
								{g}
							</button>
						))}
					</div>
				</div>

				{/* INSTRUMENTS */}
				<div className='bg-white p-5 rounded-2xl'>
					<h2 className='font-bold mb-3'>Инструменты</h2>

					{INSTRUMENTS.map(i => (
						<div key={i} className='mb-3'>
							<label className='flex items-center gap-2'>
								<Checkbox
									checked={selectedInstruments.includes(i)}
									onCheckedChange={() => toggleInstrument(i)}
								/>
								{i}
							</label>

							{selectedInstruments.includes(i) && (
								<RadioGroup
									value={instrumentLevels[i]?.toString() || ''}
									onValueChange={val => setInstrumentLevel(i, Number(val))}
								>
									{SKILL_LEVELS.map(l => (
										<div key={l.value} className='flex items-center gap-2'>
											<RadioGroupItem value={l.value.toString()} />
											{l.label}
										</div>
									))}
								</RadioGroup>
							)}
						</div>
					))}
				</div>

				{/* MEDIA */}
				<div className='space-y-4'>
					<h2 className='text-lg font-semibold px-1'>Медиа</h2>

					{/* ФОТО */}
					<div className='bg-white p-5 rounded-xl shadow-sm space-y-3'>
						<p className='text-sm text-gray-500'>Фотография</p>

						{/* PREVIEW */}
						{(photo || photoURL) && (
							<img
								src={photo ? URL.createObjectURL(photo) : photoURL}
								alt='profile'
								className='w-full h-40 object-cover rounded-xl'
							/>
						)}

						<label className='flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-[#60519B]/30 rounded-xl cursor-pointer hover:bg-[#F3F0FF] transition'>
							<div className='flex flex-col items-center gap-2 text-[#60519B]'>
								<ImageIcon className='w-6 h-6' />
								<span className='text-sm font-medium'>
									{photo
										? photo.name
										: photoURL
											? 'Заменить фото'
											: 'Загрузить фото'}
								</span>
							</div>

							<input
								type='file'
								accept='image/*'
								className='hidden'
								onChange={e => setPhoto(e.target.files?.[0] || null)}
							/>
						</label>
					</div>

					{/* АУДИО */}
					<div className='bg-white p-5 rounded-xl shadow-sm space-y-3'>
						<p className='text-sm text-gray-500'>Аудио</p>

						{/* PLAYER */}
						{(audio || audioURL) && (
							<audio controls className='w-full'>
								<source src={audio ? URL.createObjectURL(audio) : audioURL} />
							</audio>
						)}

						<label className='flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-[#60519B]/30 rounded-xl cursor-pointer hover:bg-[#F3F0FF] transition'>
							<div className='flex flex-col items-center gap-2 text-[#60519B]'>
								<Music className='w-6 h-6' />
								<span className='text-sm font-medium'>
									{audio
										? audio.name
										: audioURL
											? 'Заменить аудио'
											: 'Загрузить аудио'}
								</span>
							</div>

							<input
								type='file'
								accept='audio/*'
								className='hidden'
								onChange={e => setAudio(e.target.files?.[0] || null)}
							/>
						</label>
					</div>
				</div>

				{/* VISIBLE */}
				<div className='bg-white p-5 rounded-2xl shadow-sm border border-gray-100'>
					<h2 className='font-bold text-gray-800 mb-3 text-lg'>
						Видимость профиля
					</h2>

					<div className='flex items-center justify-between'>
						<div>
							<p className='font-medium text-gray-700'>Показывать анкету</p>
							<p className='text-sm text-gray-400'>
								Твоя анкета будет видна другим пользователям
							</p>
						</div>

						<Checkbox
							checked={isVisible}
							onCheckedChange={() => setIsVisible(v => !v)}
						/>
					</div>
				</div>

				{/* SUBMIT */}
				<Button disabled={isSaving} className='w-full bg-[#60519B] text-white'>
					{isSaving ? (
						<Loader2 className='animate-spin' />
					) : (
						<>
							<Check className='w-4 h-4 mr-2' />
							Сохранить изменения
						</>
					)}
				</Button>
			</form>
		</div>
	)
}
