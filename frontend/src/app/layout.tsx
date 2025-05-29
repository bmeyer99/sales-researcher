'use client';

// import { Geist, Geist_Mono } from "next/font/google";
import './globals.css';
import { GoogleOAuthProvider } from '@react-oauth/google';
import { useEffect } from 'react';
import { useAuthStore } from '../store/authStore';

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const checkAuthStatus = useAuthStore((state) => state.checkAuthStatus);

  useEffect(() => {
    checkAuthStatus();
  }, [checkAuthStatus]);

  return (
    <html lang="en">
      <body className={`antialiased`}>
        <GoogleOAuthProvider
          clientId={(() => {
            if (!process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID) {
              throw new Error('NEXT_PUBLIC_GOOGLE_CLIENT_ID is not defined');
            }
            return process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID;
          })()}
        >
          {children}
        </GoogleOAuthProvider>
      </body>
    </html>
  );
}
