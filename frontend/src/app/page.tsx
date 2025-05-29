'use client';

import React, { useState } from 'react';
import ProtectedRoute from '../components/ProtectedRoute';
import { useAuthStore } from '../store/authStore';
import GoogleDriveFolderInput from '../components/GoogleDriveFolderInput';

export default function HomePage() {
  const { user, logout } = useAuthStore();
  const [googleDriveFolderName, setGoogleDriveFolderName] = useState<string>('');
  const [companyName, setCompanyName] = useState<string>('');
  const [isResearching, setIsResearching] = useState(false);
  const [jobId, setJobId] = useState<string | null>(null);
  const [error, setError] = useState('');

  const handleFolderNameChange = (name: string) => {
    setGoogleDriveFolderName(name);
  };

  const handleStartResearch = async () => {
    if (!companyName || !googleDriveFolderName) {
      setError('Please fill in all fields.');
      return;
    }

    setIsResearching(true);
    setError('');

    const { token } = useAuthStore.getState();

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/research/start`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            company_name: companyName,
            gdrive_folder_name: googleDriveFolderName,
          }),
        },
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to start research.');
      }

      const data = await response.json();
      console.log('Research initiated successfully:', data);
      setJobId(data.job_id);
    } catch (err: any) {
      setError(err.message || 'Failed to start research. Please try again.');
      console.error('Research initiation error:', err);
    } finally {
      setIsResearching(false);
    }
  };

  const isButtonDisabled = isResearching || !companyName || !googleDriveFolderName;

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
              <div className="mx-auto mt-8 w-full max-w-md">
                <GoogleDriveFolderInput
                  folderName={googleDriveFolderName}
                  onFolderChange={handleFolderNameChange}
                />
              </div>
              {error && (
                <div
                  className="relative mb-4 rounded border border-red-400 bg-red-100 px-4 py-3 text-red-700"
                  role="alert"
                >
                  <strong className="font-bold">Error!</strong>
                  <span className="block sm:inline"> {error}</span>
                </div>
              )}
              <div className="mb-4">
                <label
                  htmlFor="companyName"
                  className="mb-2 block text-sm font-bold text-gray-700"
                >
                  Prospect Company Name:
                </label>
                <input
                  type="text"
                  id="companyName"
                  className="focus:shadow-outline w-full appearance-none rounded border px-3 py-2 leading-tight text-gray-700 shadow focus:outline-none"
                  placeholder="e.g., Acme Corp"
                  value={companyName}
                  onChange={(e) => setCompanyName(e.target.value)}
                  disabled={isResearching}
                />
              </div>
              <button
                onClick={handleStartResearch}
                className={`focus:shadow-outline w-full rounded bg-blue-500 px-4 py-2 font-bold text-white transition duration-200 hover:bg-blue-700 focus:outline-none ${
                  isButtonDisabled ? 'cursor-not-allowed opacity-50' : ''
                }`}
                disabled={isButtonDisabled}
              >
                {isResearching ? 'Initiating Research...' : 'Start Research'}
              </button>
              {jobId ? (
                <ResearchProgress jobId={jobId} />
              ) : (
                isResearching && (
                  <p className="mt-4 text-center text-gray-600">
                    Research is being initiated. Please wait...
                  </p>
                )
              )}
              <button
                onClick={logout}
                className="mt-2 rounded bg-red-500 px-4 py-2 text-white hover:bg-red-600"
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
