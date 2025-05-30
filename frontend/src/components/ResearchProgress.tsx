import React, { useState, useEffect, memo } from 'react'; // Import memo
import { useAuthStore } from '../store/authStore';
import { API_BASE_URL } from '@/config';

interface ResearchProgressProps {
  jobId: string | null;
}

interface ResearchStatus {
  status: 'PENDING' | 'PROGRESS' | 'SUCCESS' | 'FAILURE';
  message: string;
  phase?: string;
  result_link?: string;
  error?: string;
}

const ResearchProgress: React.FC<ResearchProgressProps> = memo(({ jobId }) => {
  const [progress, setProgress] = useState<ResearchStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const token = useAuthStore(state => state.token); // Reactive token

  useEffect(() => {
    if (!jobId) {
      setProgress(null);
      setError(null);
      return;
    }

    let intervalId: NodeJS.Timeout | undefined = undefined;

    const fetchStatus = async () => {
      if (!token) { // Check reactive token
        setError('Authentication token not found. Polling paused.');
        if (intervalId) clearInterval(intervalId); // Stop polling if token disappears
        return;
      }
      setError(null); // Clear previous "token not found" error if token is now available

      try {
        if (!API_BASE_URL) {
          throw new Error('API_BASE_URL is not configured.');
        }
        const response = await fetch(
          `${API_BASE_URL}/research/status/${jobId}`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          },
        );

        if (!response.ok) {
          let errorDetail = `HTTP error! status: ${response.status}`;
          try {
            const errorData = await response.json();
            errorDetail = errorData.detail || errorDetail;
          } catch (e) { /* Ignore if response is not JSON */ }
          throw new Error(errorDetail);
        }

        const data: ResearchStatus = await response.json();
        setProgress(data);

        if (data.status === 'SUCCESS' || data.status === 'FAILURE') {
          if (intervalId) clearInterval(intervalId);
        }
      } catch (err: any) {
        setError(err.message);
        setProgress(null);
        if (intervalId) clearInterval(intervalId);
      }
    };

    // Initial fetch
    fetchStatus();

    // Set up polling only if token exists
    if (token) {
      intervalId = setInterval(fetchStatus, 3000); // Poll every 3 seconds
    } else {
      setError('Authentication token not found. Polling not started.');
    }
    
    // Cleanup on component unmount or jobId/token change
    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [jobId, token]); // Add token to dependency array

  if (!jobId) {
    return null; // Don't render if no jobId is provided
  }

  if (error) {
    return <div className="text-red-500">Error: {error}</div>;
  }

  if (!progress) {
    return <div>Loading research status...</div>;
  }

  return (
    <div className="rounded-md border bg-white p-4 shadow-sm">
      <h2 className="mb-2 text-lg font-semibold">Research Progress</h2>
      <p>
        <strong>Status:</strong> {progress.status}
      </p>
      <p>
        <strong>Message:</strong> {progress.message}
      </p>
      {progress.phase && (
        <p>
          <strong>Phase:</strong> {progress.phase}
        </p>
      )}

      {progress.status === 'PROGRESS' && (
        <div className="mt-2">
          <div className="h-2.5 w-full rounded-full bg-gray-200 dark:bg-gray-700">
            <div
              className="h-2.5 rounded-full bg-blue-600"
              style={{ width: '100%' }}
            ></div>
          </div>
          <p className="mt-1 text-sm text-gray-500">Processing...</p>
        </div>
      )}

      {progress.status === 'SUCCESS' && progress.result_link && (
        <div className="mt-4">
          <p className="font-medium text-green-600">All tasks complete!</p>
          <p>
            <strong>Google Drive Link:</strong>{' '}
            <a
              href={progress.result_link}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-500 hover:underline"
            >
              Open Folder
            </a>
          </p>
        </div>
      )}

      {progress.status === 'FAILURE' && (
        <div className="mt-4 text-red-500">
          <p>
            <strong>Research Failed:</strong>{' '}
            {progress.error || 'An unknown error occurred.'}
          </p>
        </div>
      )}
    </div>
  );
});

ResearchProgress.displayName = 'ResearchProgress'; // Optional: for better debugging

export default ResearchProgress;
