import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router'
import { useAuth } from '../../context/AuthContext'
import { authService } from '../../api/AuthService'

export function LoginPage() {
	const [email, setEmail] = useState('')
	const [password, setPassword] = useState('')
	const { login, isLoggedIn } = useAuth()
	const navigate = useNavigate()

	useEffect(() => {
		if (isLoggedIn!) {
			navigate('/profile', { replace: true })
		}
	}, [isLoggedIn, navigate])

	const handleFormSubmit = async (e: React.FormEvent) => {
		e.preventDefault()

		try {
			const data = await authService.login({
				login: email,
				password,
			})

			if (data.token) {
				login(data.token)
				navigate('/profile', { replace: true })
			}
		} catch (error: any) {
			console.error('Ошибка входа:', error)

			if (error.response?.status === 401) {
				alert('Неверный логин или пароль')
				return
			}

			alert('Ошибка сервера. Попробуйте позже')
		}
	}

	return (
		<div className='min-h-screen flex items-center justify-center bg-gradient-to-br from-[#1E202C] to-[#60519B] p-4'>
			<form
				onSubmit={handleFormSubmit}
				className='w-full max-w-sm bg-white rounded-2xl shadow-2xl p-6 space-y-4'
			>
				<h1 className='text-2xl font-bold text-center text-gray-900'>
					Вход в аккаунт
				</h1>

				<p className='text-sm text-gray-500 text-center'>
					Войди, чтобы продолжить
				</p>

				<input
					type='text'
					value={email}
					onChange={e => setEmail(e.target.value)}
					placeholder='Логин'
					className='w-full border border-gray-300 p-3 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#60519B]'
				/>

				<input
					type='password'
					value={password}
					onChange={e => setPassword(e.target.value)}
					placeholder='Пароль'
					className='w-full border border-gray-300 p-3 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#60519B]'
				/>

				<button
					type='submit'
					className='w-full bg-[#60519B] hover:bg-[#4d3f7e] text-white p-3 rounded-xl font-medium transition'
				>
					Войти
				</button>

				<p className='text-xs text-center text-gray-400'>
					Добро пожаловать обратно 🎵
				</p>
			</form>
		</div>
	)
}
