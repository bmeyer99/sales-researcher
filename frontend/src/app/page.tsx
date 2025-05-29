import React, { useState } from 'react';
import ProtectedRoute from "../components/ProtectedRoute";
import { useAuthStore } from "../store/authStore";
import GoogleDriveFolderInput from "../components/GoogleDriveFolderInput";

export default function HomePage() {
  const { user, logout } = useAuthStore();
  const [googleDriveFolderName, setGoogleDriveFolderName] = useState<string>('');

  const handleFolderNameChange = (name: string) => {
    setGoogleDriveFolderName(name);
  };

  // In a real scenario, you would pass googleDriveFolderName to your backend API
  // For example, when a "Start Research" button is clicked.
  // console.log("Current Google Drive Folder Name:", googleDriveFolderName);

  return (
    <ProtectedRoute>
      <main className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-br from-slate-900 to-slate-700 p-24">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-white sm:text-6xl">
            Sales Prospect Research Tool
          </h1>
          <p className="mt-6 text-lg leading-8 text-slate-300">
            Automated research powered by Gemini.
          </p>
          {user && (
            <div className="mt-4 text-white">
              <p>Welcome, {user.name || user.email}!</p>
              <div className="mt-8 w-full max-w-md mx-auto">
                <GoogleDriveFolderInput
                  folderName={googleDriveFolderName}
                  onFolderNameChange={handleFolderNameChange}
                />
              </div>
              <button
                onClick={logout}
                className="mt-2 px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
              >
                Logout
              </button>
            </div>
          )}
        </div>
      </main>
    </ProtectedRoute>
  );
}
