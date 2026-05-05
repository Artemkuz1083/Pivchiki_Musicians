import { createBrowserRouter } from 'react-router-dom'

import { Welcome } from './pages/Welcome'
import { Registration } from './pages/Registration'
import { RegistrationSuccess } from './pages/RegistrationSuccess'
import { Profile } from './pages/Profile'
import { Browse } from './pages/Browse'
import { LoginPage as Login } from './pages/Login'
import { Matches } from './pages/Matches'
import { EditProfile } from './pages/EditProfile'
import BandRegistration from './pages/BandRegistration'
import GroupFeed from './pages/GroupsFeed'

import { ProtectedRoute } from './ProtectedRoute'

export const router = createBrowserRouter([
	// PUBLIC
	{
		path: '/',
		Component: Welcome,
	},
	{
		path: '/login',
		Component: Login,
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
		path: '/browse',
		Component: Browse,
	},

	// PROTECTED GROUP
	{
		element: <ProtectedRoute />,
		children: [
			{
				path: '/profile',
				Component: Profile,
			},
			{
				path: '/matches',
				Component: Matches,
			},
			{
				path: '/editProfile',
				Component: EditProfile,
			},
			{
				path: '/BandRegistration',
				Component: BandRegistration,
			},
			{
				path: '/GroupFeed',
				Component: GroupFeed,
			},
		],
	},
])
