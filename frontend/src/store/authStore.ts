import { create } from 'zustand';

interface User {
  id: string;
  email: string;
  name?: string;
  picture?: string;
}

interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  checkAuthStatus: () => Promise<void>;
  login: (user: User) => void;
  logout: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  isAuthenticated: false,
  user: null,
  checkAuthStatus: async () => {
    try {
      const response = await fetch('/api/auth/status');
      if (response.ok) {
        const user = await response.json();
        set({ isAuthenticated: true, user });
      } else if (response.status === 401) {
        // If 401, it means the backend invalidated the session (e.g., refresh token failed)
        set({ isAuthenticated: false, user: null });
        // Optionally, redirect to login page if not already there
        if (window.location.pathname !== '/login') {
          window.location.href = '/login';
        }
      } else {
        set({ isAuthenticated: false, user: null });
      }
    } catch (error) {
      console.error('Failed to check auth status:', error);
      set({ isAuthenticated: false, user: null });
    }
  },
  login: (user) => set({ isAuthenticated: true, user }),
  logout: async () => {
    try {
      await fetch('/api/auth/logout', { method: 'POST' });
    } catch (error) {
      console.error('Failed to logout on backend:', error);
    } finally {
      set({ isAuthenticated: false, user: null });
    }
  },
}));