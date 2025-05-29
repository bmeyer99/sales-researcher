"use client";

import { useState, useEffect } from "react";
import ProtectedRoute from "@/components/ProtectedRoute";
import GoogleDriveFolderInput from "@/components/GoogleDriveFolderInput";
import ResearchProgress from "@/components/ResearchProgress";
import { useAuthStore } from "@/store/authStore";

export default function DashboardPage() {
  const [companyName, setCompanyName] = useState("");
  const [gdriveFolderName, setGdriveFolderName] = useState("");
  const [isResearching, setIsResearching] = useState(false);
  const [jobId, setJobId] = useState<string | null>(null);
  const [error, setError] = useState("");

  const handleStartResearch = async () => {
    if (!companyName || !gdriveFolderName) {
      setError("Please fill in all fields.");
      return;
    }

    setIsResearching(true);
    setError("");

    const { token } = useAuthStore.getState();

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/research/start`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            company_name: companyName,
            gdrive_folder_name: gdriveFolderName,
          }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to start research.");
      }

      const data = await response.json();
      console.log("Research initiated successfully:", data);
      setJobId(data.job_id);
    } catch (err: any) {
      setError(err.message || "Failed to start research. Please try again.");
      console.error("Research initiation error:", err);
    } finally {
      setIsResearching(false);
    }
  };

  const isButtonDisabled = isResearching || !companyName || !gdriveFolderName;

  return (
    <ProtectedRoute>
      <div className="min-h-screen flex items-center justify-center bg-gray-100 p-4">
        <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
          <h1 className="text-2xl font-bold text-center mb-6 text-gray-800">
            Start New Research
          </h1>

          {error && (
            <div
              className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4"
              role="alert"
            >
              <strong className="font-bold">Error!</strong>
              <span className="block sm:inline"> {error}</span>
            </div>
          )}

          <div className="mb-4">
            <label
              htmlFor="companyName"
              className="block text-gray-700 text-sm font-bold mb-2"
            >
              Prospect Company Name:
            </label>
            <input
              type="text"
              id="companyName"
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              placeholder="e.g., Acme Corp"
              value={companyName}
              onChange={(e) => setCompanyName(e.target.value)}
              disabled={isResearching}
            />
          </div>

          <div className="mb-6">
            <GoogleDriveFolderInput
              onFolderSelect={setGdriveFolderName}
              disabled={isResearching}
            />
          </div>

          <button
            onClick={handleStartResearch}
            className={`w-full bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline transition duration-200 ${
              isButtonDisabled ? "opacity-50 cursor-not-allowed" : ""
            }`}
            disabled={isButtonDisabled}
          >
            {isResearching ? "Initiating Research..." : "Start Research"}
          </button>

          {jobId ? (
            <ResearchProgress jobId={jobId} />
          ) : (
            isResearching && (
              <p className="text-center text-gray-600 mt-4">
                Research is being initiated. Please wait...
              </p>
            )
          )}
        </div>
      </div>
    </ProtectedRoute>
  );
}