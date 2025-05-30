import React, { memo } from 'react'; // Import memo

interface GoogleDriveFolderInputProps {
  folderName?: string;
  onFolderChange: (name: string) => void;
  disabled?: boolean;
}

const GoogleDriveFolderInput: React.FC<GoogleDriveFolderInputProps> = memo(({
  folderName,
  onFolderChange,
  disabled,
}) => {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onFolderChange(e.target.value);
  };

  const displayFolderName = folderName !== undefined ? folderName : '';

  return (
    <div className="mb-4">
      <label
        htmlFor="googleDriveFolderName"
        className="block text-sm font-medium text-gray-700"
      >
        Google Drive Folder Name:
      </label>
      <input
        type="text"
        id="googleDriveFolderName"
        className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm"
        placeholder="e.g., Sales Research Output"
        value={displayFolderName}
        onChange={handleChange}
        disabled={disabled}
      />
    </div>
  );
});

GoogleDriveFolderInput.displayName = 'GoogleDriveFolderInput'; // Optional: for better debugging

export default GoogleDriveFolderInput;
