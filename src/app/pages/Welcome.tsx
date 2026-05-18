import { useNavigate } from 'react-router-dom'
import { Music2, Eye, LogIn } from 'lucide-react'
import { Button } from '../components/ui/button'
import { useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';

export function Welcome() {
	const navigate = useNavigate()
	const { isLoggedIn } = useAuth();

	useEffect(() => {
    	if (isLoggedIn) {
        	navigate('/profile', { replace: true });
    	}
	}, [isLoggedIn, navigate]);

	return (
		<div className='min-h-screen bg-gradient-to-br from-[#1E202C] to-[#60519B] flex flex-col items-center justify-center p-4'>
			<div className='w-full max-w-md'>
				<div className='text-center mb-8'>
					<div className='flex justify-center mb-4'>
						<div className='bg-white rounded-full p-4 shadow-xl'>
							<Music2 className='w-12 h-12 text-[#60519B]' />
						</div>
					</div>
					<h1 className='text-3xl font-bold text-white mb-2'>MusicMatch</h1>
					<p className='text-white/90 text-lg'>Найди своих музыкантов</p>
				</div>

				<div className='bg-white rounded-2xl shadow-2xl p-6 space-y-4'>
					<h2 className='text-xl font-semibold text-gray-900 text-center mb-6'>
						Добро пожаловать!
					</h2>

					{/* Кнопка регистрации */}
					<Button
						onClick={() => navigate('/registration')}
						className='w-full bg-[#60519B] hover:bg-[#4d3f7e] text-white py-6 text-lg rounded-xl shadow-lg'
					>
						Регистрация
					</Button>

					{/* Кнопка входа */}
					<Button
						onClick={() => navigate('/login')}
						variant='secondary'
						className='w-full py-6 text-lg rounded-xl border-2 border-[#BFC0D1] hover:bg-gray-50'
					>
						<LogIn className='w-5 h-5 mr-2' />
						Войти в аккаунт
					</Button>

					{/* Предпросмотр */}
					<Button
						onClick={() => navigate('/browse')}
						variant='outline'
						className='w-full py-6 text-lg rounded-xl border-2 border-[#BFC0D1] hover:bg-gray-50'
					>
						<Eye className='w-5 h-5 mr-2' />
						Предварительный просмотр
					</Button>

					<p className='text-sm text-gray-500 text-center mt-4'>
						Создай профиль и найди единомышленников для совместного творчества
					</p>
				</div>
			</div>
		</div>
	)
}
