import React from 'react';

interface GoogleDriveFolderInputProps {
  folderName?: string; // Make optional
  onFolderNameChange?: (name: string) => void; // Make optional
  onFolderSelect?: (name: string) => void; // Add new prop
  disabled?: boolean; // Add new prop
}

const GoogleDriveFolderInput: React.FC<GoogleDriveFolderInputProps> = ({
  folderName,
  onFolderNameChange,
  onFolderSelect,
  disabled,
}) => {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (onFolderNameChange) {
      onFolderNameChange(e.target.value);
    }
    if (onFolderSelect) {
      onFolderSelect(e.target.value);
    }
  };

  const displayFolderName = folderName !== undefined ? folderName : '';

  return (
    <div className="mb-4">
      <label htmlFor="googleDriveFolderName" className="block text-sm font-medium text-gray-700">
        Google Drive Folder Name:
      </label>
      <input
        type="text"
        id="googleDriveFolderName"
        className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
        placeholder="e.g., Sales Research Output"
        value={displayFolderName}
        onChange={handleChange}
        disabled={disabled}
      />
    </div>
  );
};

export default GoogleDriveFolderInput;