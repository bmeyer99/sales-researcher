"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "../store/authStore";

interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated, checkAuthStatus } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    const checkAuth = async () => {
      if (typeof window !== "undefined") {
        // Only run on client side
        await checkAuthStatus();
        if (!isAuthenticated) {
          router.push("/login");
        }
      }
    };
    checkAuth();
  }, [isAuthenticated, checkAuthStatus, router]);

  if (isAuthenticated) {
    return <>{children}</>;
  }

  return null; // Or a loading spinner/component
};

export default ProtectedRoute;