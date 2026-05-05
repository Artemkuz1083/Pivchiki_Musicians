import React, { createContext, useContext, useState } from 'react'

interface AuthContextType {
	isLoggedIn: boolean
	token: string | null
	login: (token: string) => void
	logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

const STORAGE_KEY = 'authToken'

export function AuthProvider({ children }: { children: React.ReactNode }) {
	// синхронно читаем токен (без useEffect → нет мигания)
	const [token, setToken] = useState<string | null>(() => {
		if (typeof window === 'undefined') return null
		return localStorage.getItem(STORAGE_KEY)
	})

	const login = (newToken: string) => {
		localStorage.setItem(STORAGE_KEY, newToken)
		setToken(newToken)
	}

	const logout = () => {
		localStorage.removeItem(STORAGE_KEY)
		setToken(null)
	}

	return (
		<AuthContext.Provider
			value={{
				token,
				isLoggedIn: !!token,
				login,
				logout,
			}}
		>
			{children}
		</AuthContext.Provider>
	)
}

export const useAuth = () => {
	const ctx = useContext(AuthContext)
	if (!ctx) throw new Error('useAuth must be used within AuthProvider')
	return ctx
}
