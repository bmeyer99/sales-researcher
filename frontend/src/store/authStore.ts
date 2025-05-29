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
  token: string | null; // Add token to the state
  checkAuthStatus: () => Promise<void>;
  login: (user: User, token: string) => void; // Modify login to accept token
  logout: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  isAuthenticated: false,
  user: null,
  token: null, // Initialize token as null
  checkAuthStatus: async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/auth/status`);
      if (response.ok) {
        const { user, token } = await response.json(); // Assuming API returns user and token
        set({ isAuthenticated: true, user, token });
      } else if (response.status === 401) {
        // If 401, it means the backend invalidated the session (e.g., refresh token failed)
        set({ isAuthenticated: false, user: null, token: null });
        // Optionally, redirect to login page if not already there
        if (typeof window !== 'undefined' && window.location.pathname !== '/login') {
          window.location.href = '/login';
        }
      } else {
        set({ isAuthenticated: false, user: null, token: null });
      }
    } catch (error) {
      console.error('Failed to check auth status:', error);
      set({ isAuthenticated: false, user: null, token: null });
    }
  },
  login: (user, token) => set({ isAuthenticated: true, user, token }), // Update login action
  logout: async () => {
    try {
      await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/auth/logout`, { method: 'POST' });
    } catch (error) {
      console.error('Failed to logout on backend:', error);
    } finally {
      set({ isAuthenticated: false, user: null, token: null });
    }
  },
}));
