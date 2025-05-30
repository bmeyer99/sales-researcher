'use client';

import { Suspense } from 'react'; // Removed useEffect
import { useSearchParams } from 'next/navigation'; // Removed useRouter, useAuthStore for this component's direct use
// import { useAuthStore } from '../../store/authStore'; // Not directly needed now for isAuthenticated check here
import { API_BASE_URL } from '@/config'; // Use centralized config

function LoginContent() {
  // const router = useRouter(); // Redundant due to AuthRedirectHandler
  const searchParams = useSearchParams();
  // const { isAuthenticated } = useAuthStore(); // Redundant due to AuthRedirectHandler
  const errorMessage = searchParams.get('error');

  // useEffect(() => { // Redundant due to AuthRedirectHandler
  //   if (isAuthenticated) {
  //     router.push('/'); // AuthRedirectHandler pushes to /dashboard
  //   }
  // }, [isAuthenticated, router]);

  const handleLogin = () => {
    if (API_BASE_URL) {
      window.location.href = `${API_BASE_URL}/auth/google/login`;
    } else {
      console.error("API_BASE_URL is not configured. Cannot initiate login.");
      // Optionally, display an error message to the user in the UI
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-100">
      <div className="rounded bg-white p-8 text-center shadow-md">
        <h1 className="mb-4 text-2xl font-bold">Login</h1>
        {errorMessage && (
          <p className="mb-4 text-red-500">
            Authentication failed: {errorMessage}
          </p>
        )}
        <button
          onClick={handleLogin}
          className="rounded bg-blue-500 px-4 py-2 font-bold text-white hover:bg-blue-700"
        >
          Sign in with Google
        </button>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <LoginContent />
    </Suspense>
  );
}
