import { Link, useNavigate } from 'react-router-dom';
import { LogOut, User, Menu } from 'lucide-react';
import { useAuthStore } from '../../stores/authStore';

interface Props {
  onToggleSidebar: () => void;
}

export default function Navbar({ onToggleSidebar }: Props) {
  const { logout, user } = useAuthStore();
  const navigate = useNavigate();

  return (
    <nav className="fixed top-0 w-full bg-white shadow-sm border-b border-gray-200 z-50">
      <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button onClick={onToggleSidebar} className="md:hidden">
            <Menu size={24} />
          </button>
          <Link to="/dashboard" className="text-xl font-bold text-indigo-600">ResumeRadar</Link>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-600">{user?.email}</span>
          <button onClick={() => navigate('/profile')} className="text-gray-500 hover:text-gray-700">
            <User size={20} />
          </button>
          <button onClick={() => { logout(); navigate('/'); }} className="text-gray-500 hover:text-red-600">
            <LogOut size={20} />
          </button>
        </div>
      </div>
    </nav>
  );
}