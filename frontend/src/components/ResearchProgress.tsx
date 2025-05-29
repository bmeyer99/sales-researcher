import React, { useState, useEffect } from 'react';

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

const ResearchProgress: React.FC<ResearchProgressProps> = ({ jobId }) => {
  const [progress, setProgress] = useState<ResearchStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!jobId) {
      setProgress(null);
      setError(null);
      return;
    }

    const fetchStatus = async () => {
      try {
        const token = localStorage.getItem('access_token');
        if (!token) {
          setError('Authentication token not found.');
          return;
        }

        const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/research/status/${jobId}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }

        const data: ResearchStatus = await response.json();
        setProgress(data);

        if (data.status === 'SUCCESS' || data.status === 'FAILURE') {
          clearInterval(intervalId); // Stop polling
        }
      } catch (err: any) {
        setError(err.message);
        setProgress(null);
        clearInterval(intervalId); // Stop polling on error
      }
    };

    // Initial fetch
    fetchStatus();

    // Set up polling
    const intervalId = setInterval(fetchStatus, 3000); // Poll every 3 seconds

    // Cleanup on component unmount or jobId change
    return () => {
      clearInterval(intervalId);
    };
  }, [jobId]);

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
    <div className="p-4 border rounded-md shadow-sm bg-white">
      <h2 className="text-lg font-semibold mb-2">Research Progress</h2>
      <p><strong>Status:</strong> {progress.status}</p>
      <p><strong>Message:</strong> {progress.message}</p>
      {progress.phase && <p><strong>Phase:</strong> {progress.phase}</p>}

      {progress.status === 'PROGRESS' && (
        <div className="mt-2">
          <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700">
            <div className="bg-blue-600 h-2.5 rounded-full" style={{ width: '100%' }}></div>
          </div>
          <p className="text-sm text-gray-500 mt-1">Processing...</p>
        </div>
      )}

      {progress.status === 'SUCCESS' && progress.result_link && (
        <div className="mt-4">
          <p className="text-green-600 font-medium">All tasks complete!</p>
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
          <p><strong>Research Failed:</strong> {progress.error || 'An unknown error occurred.'}</p>
        </div>
      )}
    </div>
  );
};

export default ResearchProgress;