import React from 'react';

interface GoogleDriveFolderInputProps {
  folderName: string;
  onFolderNameChange: (name: string) => void;
}

const GoogleDriveFolderInput: React.FC<GoogleDriveFolderInputProps> = ({
  folderName,
  onFolderNameChange,
}) => {
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
        value={folderName}
        onChange={(e) => onFolderNameChange(e.target.value)}
      />
    </div>
  );
};

export default GoogleDriveFolderInput;