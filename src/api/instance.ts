import axios from 'axios'

export const api = axios.create({
	baseURL: '/api/v1',
	headers: {
		'ngrok-skip-browser-warning': 'true',
		'Content-Type': 'application/json',
	},
})

// Автоматическая подстановка токена перед каждым запросом
api.interceptors.request.use(
	config => {
		const token = localStorage.getItem('authToken')

		if (token) {
			config.headers.Authorization = `Bearer ${token}`
		}
		return config
	},
	error => {
		return Promise.reject(error)
	},
)

api.interceptors.response.use(
	response => response,
	error => {
		if (
			error.response &&
			error.response.status === 401 &&
			!error.config.url?.includes('/auth/')
		) {
			console.error(
				'Авторизация недействительна. Очистка токена и перенаправление на страницу входа.',
			)
			localStorage.removeItem('authToken')
		}
		return Promise.reject(error)
	},
)
