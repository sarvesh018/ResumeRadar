export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080';

export const STATUS_COLORS: Record<string, string> = {
  wishlist: 'bg-gray-100 text-gray-800',
  applied: 'bg-blue-100 text-blue-800',
  screening: 'bg-purple-100 text-purple-800',
  interviewing: 'bg-yellow-100 text-yellow-800',
  offer: 'bg-green-100 text-green-800',
  rejected: 'bg-red-100 text-red-800',
  withdrawn: 'bg-gray-200 text-gray-600',
};

export const STATUS_ORDER = ['wishlist', 'applied', 'screening', 'interviewing', 'offer', 'rejected', 'withdrawn'];