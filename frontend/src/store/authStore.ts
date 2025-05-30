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
  token: string | null;
  isLoadingAuth: boolean;
  authError: string | null;
  checkAuthStatus: () => Promise<void>;
  login: (user: User, token: string) => void;
  logout: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  isAuthenticated: false,
  user: null,
  token: null,
  isLoadingAuth: false,
  authError: null,
  checkAuthStatus: async () => {
    set({ isLoadingAuth: true, authError: null });
    try {
      const { API_BASE_URL } = await import('@/config'); // Dynamically import for client-side usage
      if (!API_BASE_URL) throw new Error("API_BASE_URL is not configured");
      const response = await fetch(`${API_BASE_URL}/auth/status`);
      if (response.ok) {
        const { user, token } = await response.json();
        set({ isAuthenticated: true, user, token, isLoadingAuth: false });
      } else {
        // Any non-ok response means not authenticated
        // Removed direct window.location.href, redirection will be handled by a component
        set({ isAuthenticated: false, user: null, token: null, isLoadingAuth: false });
      }
    } catch (error) {
      console.error('Failed to check auth status:', error);
      set({
        isAuthenticated: false,
        user: null,
        token: null,
        isLoadingAuth: false,
        authError: 'Failed to check auth status.',
      });
    }
  },
  login: (user, token) => set({ isAuthenticated: true, user, token, isLoadingAuth: false, authError: null }),
  logout: async () => {
    set({ isLoadingAuth: true, authError: null });
    try {
      const { API_BASE_URL } = await import('@/config'); // Dynamically import for client-side usage
      if (!API_BASE_URL) throw new Error("API_BASE_URL is not configured");
      await fetch(`${API_BASE_URL}/auth/logout`, { method: 'POST' });
    } catch (error) {
      console.error('Failed to logout on backend:', error);
      // Set error state, but still proceed to clear local auth state in finally
      set(state => ({ ...state, authError: 'Failed to logout on backend.' }));
    } finally {
      set({ isAuthenticated: false, user: null, token: null, isLoadingAuth: false });
    }
  },
}));
