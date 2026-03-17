import { createBrowserRouter } from 'react-router';
import { Welcome } from './pages/Welcome';
import { Registration } from './pages/Registration';
import { RegistrationSuccess } from './pages/RegistrationSuccess';
import { Profile } from './pages/Profile';
import { Browse } from './pages/Browse';

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
]);
