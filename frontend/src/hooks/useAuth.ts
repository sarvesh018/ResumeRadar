import { useMutation } from '@tanstack/react-query';
import apiClient from '../api/client';
import { useAuthStore } from '../stores/authStore';
import type { LoginRequest, RegisterRequest, TokenResponse, User } from '../types/index';

async function loginUser(data: LoginRequest) {
  const res = await apiClient.post<TokenResponse>('/api/v1/auth/login', data);
  return res.data;
}

async function getMe() {
  const res = await apiClient.get<User>('/api/v1/auth/me');
  return res.data;
}

export function useAuth() {
  const { login } = useAuthStore();

  const loginMutation = useMutation({
    mutationFn: loginUser,
    onSuccess: async (tokenResponse) => {
      // Fetch user details after login
      const user = await getMe();
      login(tokenResponse, user);
    },
  });

  const registerMutation = useMutation({
    mutationFn: (data: RegisterRequest) => apiClient.post('/api/v1/auth/register', data),
  });

  return { loginMutation, registerMutation };
}