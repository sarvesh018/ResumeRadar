import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Upload, FileSearch, Kanban, BarChart2 } from 'lucide-react';

interface Props {
  isOpen: boolean;
}

const links = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/upload', label: 'Upload Resume', icon: Upload },
  { to: '/match', label: 'Match Analysis', icon: FileSearch },
  { to: '/applications', label: 'Applications', icon: Kanban },
  { to: '/analytics', label: 'Analytics', icon: BarChart2 },
];

export default function Sidebar({ isOpen }: Props) {
  return (
    <aside className={`fixed top-16 left-0 h-full w-64 bg-white border-r border-gray-200 transform transition-transform duration-200 ease-in-out ${isOpen ? 'translate-x-0' : '-translate-x-full'} md:translate-x-0 z-40`}>
      <nav className="p-4 space-y-2">
        {links.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                isActive ? 'bg-indigo-50 text-indigo-700' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              }`
            }
          >
            <Icon size={18} />
            {label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}