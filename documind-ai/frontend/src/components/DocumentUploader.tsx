import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { CloudArrowUpIcon, DocumentIcon, XMarkIcon } from '@heroicons/react/24/outline';
import { documentsApi } from '../../api/documents';
import { useAppStore } from '../../store/appStore';

export function DocumentUploader() {
  const [isUploading, setIsUploading] = useState(false);
  const addDocument = useAppStore((state) => state.addDocument);
  const setUploading = useAppStore((state) => state.setUploading);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    setIsUploading(true);
    setUploading(true);

    try {
      for (const file of acceptedFiles) {
        const document = await documentsApi.upload(file);
        addDocument(document);
      }
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Failed to upload document(s). Please try again.');
    } finally {
      setIsUploading(false);
      setUploading(false);
    }
  }, [addDocument, setUploading]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
      'text/plain': ['.txt'],
      'text/csv': ['.csv'],
    },
    multiple: true,
    disabled: isUploading,
  });

  return (
    <div className="w-full">
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
          ${isDragActive 
            ? 'border-primary-500 bg-primary-50' 
            : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
          }
          ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}
        `}
      >
        <input {...getInputProps()} />
        
        <CloudArrowUpIcon className="mx-auto h-12 w-12 text-gray-400" />
        
        {isDragActive ? (
          <p className="mt-2 text-sm text-primary-600 font-medium">
            Drop the files here...
          </p>
        ) : (
          <>
            <p className="mt-2 text-sm text-gray-600">
              Drag & drop files here, or click to select
            </p>
            <p className="mt-1 text-xs text-gray-500">
              PDF, DOCX, DOC, TXT, CSV (Max 50MB)
            </p>
          </>
        )}

        {isUploading && (
          <div className="mt-4">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className="bg-primary-600 h-2 rounded-full animate-pulse" style={{ width: '100%' }}></div>
            </div>
            <p className="mt-2 text-sm text-gray-600">Uploading...</p>
          </div>
        )}
      </div>
    </div>
  );
}
