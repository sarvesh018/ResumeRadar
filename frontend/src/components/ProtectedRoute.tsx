import { Navigate, Outlet } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'

export default function ProtectedRoute() {
  const { accessToken } = useAuthStore()
  return accessToken ? <Outlet /> : <Navigate to="/login" replace />
}