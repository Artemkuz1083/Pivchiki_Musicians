import { createBrowserRouter } from 'react-router'
import { Welcome } from './pages/Welcome'
import { Registration } from './pages/Registration'
import { RegistrationSuccess } from './pages/RegistrationSuccess'
import { Profile } from './pages/Profile'
import { Browse } from './pages/Browse'
import { LoginPage as Login } from './pages/Login'
import { Matches } from './pages/Matches'
import { EditProfile } from './pages/EditProfile'

export const router = createBrowserRouter([
	{
		path: '/',
		Component: Welcome,
	},
	{
		path: '/registration',
		Component: Registration,
	},
	{
		path: '/registration-success',
		Component: RegistrationSuccess,
	},
	{
		path: '/profile',
		Component: Profile,
	},
	{
		path: '/browse',
		Component: Browse,
	},
	{
		path: '/login',
		Component: Login,
	},
	{
		path: '/matches',
		Component: Matches,
	},
	{
		path: '/editProfile',
		Component: EditProfile,
	},
])
