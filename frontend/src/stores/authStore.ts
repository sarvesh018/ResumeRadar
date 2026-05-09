import { create } from 'zustand';
import type { User, TokenResponse } from '../types/index';

// interface TokenResponse {
//   access_token: string;
//   refresh_token: string;
//   token_type: string;
//   expires_in: number;
// }

// interface User {
//   id: string;
//   email: string;
//   full_name: string | null;
//   is_active: boolean;
//   is_verified: boolean;
// }


interface AuthState {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  login: (tokenResponse: TokenResponse, user: User) => void;
  logout: () => void;
  setUser: (user: User) => void; // optional, but useful later
}

export const useAuthStore = create<AuthState>((set) => ({
  token: localStorage.getItem('token'),
  user: null,
  isAuthenticated: !!localStorage.getItem('token'),

  login: (tokenResponse, user) => {
    localStorage.setItem('token', tokenResponse.access_token);
    set({ token: tokenResponse.access_token, user, isAuthenticated: true });
  },

  logout: () => {
    localStorage.removeItem('token');
    set({ token: null, user: null, isAuthenticated: false });
  },

  setUser: (user) => set({ user }),
}));