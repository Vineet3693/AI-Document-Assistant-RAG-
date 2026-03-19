import React, { useState } from 'react';
import { DocumentTextIcon, TrashIcon, CheckCircleIcon, ClockIcon, ExclamationCircleIcon } from '@heroicons/react/24/outline';
import { CheckCircleIcon as CheckCircleSolidIcon } from '@heroicons/react/24/solid';
import { Document } from '../../api/documents';
import { useAppStore } from '../../store/appStore';

interface DocumentListProps {
  onDocumentClick?: (doc: Document) => void;
}

export function DocumentList({ onDocumentClick }: DocumentListProps) {
  const documents = useAppStore((state) => state.documents);
  const selectedDocumentIds = useAppStore((state) => state.selectedDocumentIds);
  const toggleDocumentSelection = useAppStore((state) => state.toggleDocumentSelection);
  const removeDocument = useAppStore((state) => state.removeDocument);

  const getStatusIcon = (status: Document['status']) => {
    switch (status) {
      case 'ready':
        return <CheckCircleSolidIcon className="h-5 w-5 text-green-500" />;
      case 'processing':
        return <ClockIcon className="h-5 w-5 text-yellow-500 animate-spin" />;
      case 'failed':
        return <ExclamationCircleIcon className="h-5 w-5 text-red-500" />;
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const handleDelete = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    if (confirm('Are you sure you want to delete this document?')) {
      try {
        await fetch(`/api/documents/${id}`, { method: 'DELETE' });
        removeDocument(id);
      } catch (error) {
        console.error('Delete failed:', error);
      }
    }
  };

  if (documents.length === 0) {
    return (
      <div className="text-center py-12">
        <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-2 text-sm font-medium text-gray-900">No documents</h3>
        <p className="mt-1 text-sm text-gray-500">
          Get started by uploading a document.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {documents.map((doc) => (
        <div
          key={doc.id}
          onClick={() => onDocumentClick?.(doc)}
          className={`
            flex items-center justify-between p-4 rounded-lg border cursor-pointer transition-all
            ${selectedDocumentIds.includes(doc.id)
              ? 'border-primary-500 bg-primary-50'
              : 'border-gray-200 hover:border-primary-300 hover:bg-gray-50'
            }
          `}
        >
          <div className="flex items-center space-x-3 flex-1">
            <input
              type="checkbox"
              checked={selectedDocumentIds.includes(doc.id)}
              onChange={(e) => {
                e.stopPropagation();
                toggleDocumentSelection(doc.id);
              }}
              onClick={(e) => e.stopPropagation()}
              className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
            />
            
            <DocumentTextIcon className="h-8 w-8 text-gray-400" />
            
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">
                {doc.originalName}
              </p>
              <div className="flex items-center space-x-2 mt-1">
                <span className="text-xs text-gray-500">
                  {formatFileSize(doc.size)}
                </span>
                <span className="text-gray-300">•</span>
                <span className="text-xs text-gray-500">
                  {new Date(doc.uploadedAt).toLocaleDateString()}
                </span>
                {doc.embeddings && (
                  <>
                    <span className="text-gray-300">•</span>
                    <span className="text-xs text-gray-500">
                      {doc.embeddings.chunkCount} chunks
                    </span>
                  </>
                )}
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            {getStatusIcon(doc.status)}
            
            <button
              onClick={(e) => handleDelete(e, doc.id)}
              className="p-1 text-gray-400 hover:text-red-500 transition-colors"
              title="Delete document"
            >
              <TrashIcon className="h-5 w-5" />
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
