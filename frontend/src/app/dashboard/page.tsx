'use client';

import { useState } from 'react';
import ProtectedRoute from '@/components/ProtectedRoute';
import GoogleDriveFolderInput from '@/components/GoogleDriveFolderInput';
import ResearchProgress from '@/components/ResearchProgress';
import { useAuthStore } from '@/store/authStore';
import { useRouter } from 'next/navigation';

export default function DashboardPage() {
  const [companyName, setCompanyName] = useState('');
  const [gdriveFolderName, setGdriveFolderName] = useState('');
  const [isResearching, setIsResearching] = useState(false);
  const [jobId, setJobId] = useState<string | null>(null);
  const [error, setError] = useState('');
  const router = useRouter();

  const handleStartResearch = async () => {
    if (!companyName || !gdriveFolderName) {
      setError('Please fill in all fields.');
      return;
    }

    setIsResearching(true);
    setError('');

    const { token } = useAuthStore.getState();
    const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;

    if (!apiBaseUrl) {
      setError('NEXT_PUBLIC_API_BASE_URL is not defined.');
      setIsResearching(false);
      return;
    }

    try {
      const response = await fetch(
        `${apiBaseUrl}/research/start`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            company_name: companyName,
            gdrive_folder_name: gdriveFolderName,
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

  const isButtonDisabled = isResearching || !companyName || !gdriveFolderName;

  return (
    <ProtectedRoute>
      <div className="flex min-h-screen items-center justify-center bg-gray-100 p-4">
        <div className="w-full max-w-md rounded-lg bg-white p-8 shadow-md">
          <h1 className="mb-6 text-center text-2xl font-bold text-gray-800">
            Start New Research
          </h1>

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

          <div className="mb-6">
            <GoogleDriveFolderInput
              onFolderChange={setGdriveFolderName}
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
        </div>
      </div>
    </ProtectedRoute>
  );
}
