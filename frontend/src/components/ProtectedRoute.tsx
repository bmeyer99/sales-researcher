'use client';

import { useAuthStore } from '../store/authStore';
// useRouter might not be needed if AuthRedirectHandler handles all redirects
// import { useRouter } from 'next/navigation';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const isAuthenticated = useAuthStore(state => state.isAuthenticated);
  const isLoadingAuth = useAuthStore(state => state.isLoadingAuth);

  // AuthRedirectHandler in layout.tsx is now responsible for the initial auth check
  // and redirecting unauthenticated users to /login.
  // This component primarily ensures children are only rendered if authenticated,
  // and can show a loading state.

  if (isLoadingAuth) {
    // Or a more sophisticated loading spinner/component
    return <div>Loading authentication details...</div>;
  }

  if (!isAuthenticated) {
    // This case should ideally be handled by AuthRedirectHandler redirecting to /login.
    // If AuthRedirectHandler is working correctly, this path should not be hit often for pages
    // meant to be protected. Returning null will prevent rendering children.
    return null;
  }

  return <>{children}</>;
};

export default ProtectedRoute;
