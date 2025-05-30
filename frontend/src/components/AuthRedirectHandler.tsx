'use client';

import { useEffect } from 'react';
import { useAuthStore } from '@/store/authStore';
import { useRouter, usePathname } from 'next/navigation';

export default function AuthRedirectHandler({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  // Subscribe to specific state slices to prevent unnecessary re-renders
  const isAuthenticated = useAuthStore(state => state.isAuthenticated);
  const token = useAuthStore(state => state.token);
  const isLoadingAuth = useAuthStore(state => state.isLoadingAuth);
  const checkAuthStatus = useAuthStore(state => state.checkAuthStatus);

  useEffect(() => {
    // Call checkAuthStatus on initial load if not already loading and no token
    // This helps re-validate session if user re-opens the app
    if (!isLoadingAuth && !token) {
      checkAuthStatus();
    }
  }, [checkAuthStatus, isLoadingAuth, token]); // Added token to dependencies

  useEffect(() => {
    // Only attempt to redirect if authentication status is not loading
    if (!isLoadingAuth) {
      if (!isAuthenticated && pathname !== '/login') {
        router.push('/login');
      } else if (isAuthenticated && pathname === '/login') {
        // If authenticated and on login page, redirect to dashboard
        router.push('/dashboard');
      }
    }
  }, [isAuthenticated, isLoadingAuth, pathname, router]);

  // Optional: Show a loading spinner or splash screen while checking auth
  // if (isLoadingAuth && !token) { // Or a more sophisticated check
  //   return <div>Loading authentication...</div>; 
  // }

  return <>{children}</>;
}