import axios from 'axios'

export const api = axios.create({
    baseURL: '/api/v1',
    headers: {
        'ngrok-skip-browser-warning': 'true',
        'Content-Type': 'application/json',
    },
})

// Очередь для запросов, ожидающих обновления токена
let isRefreshing = false
let failedQueue: any[] = []

const processQueue = (error: any, token: string | null = null) => {
    failedQueue.forEach(prom => {
        if (error) {
            prom.reject(error)
        } else {
            prom.resolve(token)
        }
    })
    failedQueue = []
}

// Интерцептор запроса: подставляет короткоживущий токен из localStorage
api.interceptors.request.use(
    config => {
        const token = localStorage.getItem('authToken')
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    },
    error => Promise.reject(error),
)

//ловит 401 и обновляет через HttpOnly Cookies
api.interceptors.response.use(
    response => response,
    async error => {
        const originalRequest = error.config

        // Если сервер ответил 401, и это не был запрос к разделу /auth/
        if (
            error.response &&
            error.response.status === 401 &&
            !originalRequest._retry &&
            !originalRequest.url?.includes('/auth/')
        ) {
            
            if (isRefreshing) {
                return new Promise((resolve, reject) => {
                    failedQueue.push({ resolve, reject })
                })
                    .then(token => {
                        originalRequest.headers.Authorization = `Bearer ${token}`
                        return api(originalRequest)
                    })
                    .catch(err => Promise.reject(err))
            }

            originalRequest._retry = true
            isRefreshing = true

            try {
                console.log('Access-токен протух, обновление через Cookie');

                // Вызываем эндпоинт обновления. 
                // Параметры в body не нужны, но withCredentials ОБЯЗАТЕЛЕН для передачи HttpOnly Cookies
                const response = await axios.post('/api/v1/auth/refresh', {}, {
                    withCredentials: true 
                })

                // Бэкенд возвращает новый токен. 
                // Проверяем возможные варианты названия ключа (token или access_token)
                const newToken = response.data.token || response.data.access_token || response.data[Object.keys(response.data)[0]]

                if (!newToken) {
                    throw new Error('Новый токен не найден в ответе сервера')
                }

                console.log('Ротация токенов выполнена успешно!')
                localStorage.setItem('authToken', newToken)

                // Обновляем заголовок авторизации для текущего запроса
                originalRequest.headers.Authorization = `Bearer ${newToken}`
                
                // Пропускаем все остальные запросы из очереди
                processQueue(null, newToken)
                
                // Повторяем исходный запрос, на котором мы споткнулись
                return api(originalRequest)

            } catch (refreshError) {
                console.error('Кука Refresh-токена истекла или невалидна. Требуется полный перезаход.')
                processQueue(refreshError, null)
                
                // Чистим старый протухший хлам
                localStorage.removeItem('authToken')
                localStorage.removeItem('my_group_id')
                
                // Выкидываем на логин
                window.location.href = '/login'
                
                return Promise.reject(refreshError)
            } finally {
                isRefreshing = false
            }
        }

        return Promise.reject(error)
    },
)