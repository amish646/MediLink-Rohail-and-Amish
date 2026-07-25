import { Navigate, Outlet } from 'react-router-dom';

export default function AdminPrivateRoute() {
  const isAdmin = localStorage.getItem('adminAuthenticated') === 'true';
  return isAdmin ? <Outlet /> : <Navigate to='/admin-login' />;
}
