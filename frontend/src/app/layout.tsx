'use client';

import './globals.css';
import { GoogleOAuthProvider } from '@react-oauth/google';
// Removed useEffect and useAuthStore import as checkAuthStatus is now handled in AuthRedirectHandler
import AuthRedirectHandler from '@/components/AuthRedirectHandler'; // Adjusted path assuming @ is src

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  // const checkAuthStatus = useAuthStore((state) => state.checkAuthStatus); // Moved to AuthRedirectHandler

  // useEffect(() => { // Moved to AuthRedirectHandler
  //   checkAuthStatus();
  // }, [checkAuthStatus]);

  return (
    <html lang="en">
      <body className={`antialiased`}>
        <GoogleOAuthProvider
          clientId={require('@/config').GOOGLE_CLIENT_ID || ''}
        >
          <AuthRedirectHandler>
            {children}
          </AuthRedirectHandler>
        </GoogleOAuthProvider>
      </body>
    </html>
  );
}
