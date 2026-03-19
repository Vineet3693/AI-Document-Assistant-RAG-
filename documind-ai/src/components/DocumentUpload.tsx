import React, { useCallback, useState } from 'react';
import { Upload, FileText, X, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import type { Document } from '../types';
import { useAppStore } from '../store/useAppStore';

interface DocumentUploadProps {
  onUploadComplete?: (doc: Document) => void;
}

export const DocumentUpload: React.FC<DocumentUploadProps> = ({ onUploadComplete }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [uploadingFiles, setUploadingFiles] = useState<Array<{ name: string; progress: number }>>([]);
  const addDocument = useAppStore((state) => state.addDocument);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setIsDragging(false);
  }, []);

  const processFile = async (file: File) => {
    const validTypes = ['application/pdf', 'application/msword', 
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'text/plain', 'application/vnd.ms-excel', 
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'application/vnd.ms-powerpoint',
      'application/vnd.openxmlformats-officedocument.presentationml.presentation'];
    
    if (!validTypes.includes(file.type) && !file.name.match(/\.(pdf|docx|doc|txt|xlsx|xls|pptx|ppt|csv)$/)) {
      alert('Invalid file type. Please upload PDF, Word, Excel, PowerPoint, TXT, or CSV files.');
      return;
    }

    setUploadingFiles(prev => [...prev, { name: file.name, progress: 0 }]);

    // Simulate upload progress
    for (let i = 0; i <= 100; i += 10) {
      await new Promise(resolve => setTimeout(resolve, 200));
      setUploadingFiles(prev => 
        prev.map(f => f.name === file.name ? { ...f, progress: i } : f)
      );
    }

    // Create document object
    const newDoc: Document = {
      id: crypto.randomUUID(),
      name: file.name,
      type: file.name.split('.').pop() as any,
      size: file.size,
      uploadDate: new Date(),
      status: 'ready',
      tags: [],
      version: 1,
      accessLevel: 'private',
      pageCount: Math.floor(Math.random() * 50) + 1,
    };

    addDocument(newDoc);
    setUploadingFiles(prev => prev.filter(f => f.name !== file.name));
    
    if (onUploadComplete) {
      onUploadComplete(newDoc);
    }
  };

  const handleDrop = useCallback(async (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = Array.from(e.dataTransfer.files);
    for (const file of files) {
      await processFile(file);
    }
  }, [onUploadComplete]);

  const handleFileInput = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    for (const file of files) {
      await processFile(file);
    }
    e.target.value = '';
  };

  return (
    <div className="w-full">
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`
          relative border-2 border-dashed rounded-xl p-8 text-center transition-all duration-300
          ${isDragging 
            ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20' 
            : 'border-gray-300 dark:border-gray-600 hover:border-primary-400'
          }
        `}
      >
        <input
          type="file"
          multiple
          accept=".pdf,.doc,.docx,.txt,.xlsx,.xls,.ppt,.pptx,.csv"
          onChange={handleFileInput}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        />
        
        <div className="space-y-4">
          <div className="flex justify-center">
            <div className={`p-4 rounded-full ${isDragging ? 'bg-primary-100' : 'bg-gray-100 dark:bg-gray-700'}`}>
              <Upload className={`w-8 h-8 ${isDragging ? 'text-primary-600' : 'text-gray-400'}`} />
            </div>
          </div>
          
          <div>
            <p className="text-lg font-medium text-gray-900 dark:text-white">
              {isDragging ? 'Drop files here' : 'Drag & drop files here'}
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              or click to browse
            </p>
          </div>
          
          <div className="text-xs text-gray-400 dark:text-gray-500">
            Supported formats: PDF, Word, Excel, PowerPoint, TXT, CSV
          </div>
        </div>
      </div>

      {/* Uploading Files */}
      {uploadingFiles.length > 0 && (
        <div className="mt-4 space-y-2">
          {uploadingFiles.map((file, index) => (
            <div key={index} className="card py-3">
              <div className="flex items-center gap-3">
                <Loader2 className="w-5 h-5 text-primary-600 animate-spin" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                    {file.name}
                  </p>
                  <div className="mt-1 w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${file.progress}%` }}
                    />
                  </div>
                </div>
                <span className="text-sm text-gray-500">{file.progress}%</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
