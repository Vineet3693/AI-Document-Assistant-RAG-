import React from 'react';
import { FileText, Trash2, CheckCircle, Clock, AlertCircle, Eye, Download, Share2, Tag } from 'lucide-react';
import type { Document } from '../types';
import { useAppStore } from '../store/useAppStore';

export const DocumentList: React.FC = () => {
  const documents = useAppStore((state) => state.documents);
  const selectedDocuments = useAppStore((state) => state.selectedDocuments);
  const selectDocument = useAppStore((state) => state.selectDocument);
  const deselectDocument = useAppStore((state) => state.deselectDocument);
  const removeDocument = useAppStore((state) => state.removeDocument);

  const getStatusIcon = (status: Document['status']) => {
    switch (status) {
      case 'ready':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'processing':
        return <Clock className="w-4 h-4 text-yellow-500 animate-pulse" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      default:
        return <Clock className="w-4 h-4 text-gray-400" />;
    }
  };

  const getFileTypeColor = (type: Document['type']) => {
    const colors: Record<string, string> = {
      pdf: 'bg-red-100 text-red-700',
      docx: 'bg-blue-100 text-blue-700',
      doc: 'bg-blue-100 text-blue-700',
      xlsx: 'bg-green-100 text-green-700',
      xls: 'bg-green-100 text-green-700',
      pptx: 'bg-orange-100 text-orange-700',
      ppt: 'bg-orange-100 text-orange-700',
      txt: 'bg-gray-100 text-gray-700',
      csv: 'bg-purple-100 text-purple-700',
    };
    return colors[type] || 'bg-gray-100 text-gray-700';
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const formatDate = (date: Date): string => {
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    }).format(new Date(date));
  };

  return (
    <div className="space-y-3">
      {documents.length === 0 ? (
        <div className="text-center py-8">
          <FileText className="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-3" />
          <p className="text-gray-500 dark:text-gray-400">No documents uploaded yet</p>
          <p className="text-sm text-gray-400 dark:text-gray-500 mt-1">
            Upload your first document to get started
          </p>
        </div>
      ) : (
        documents.map((doc) => (
          <div
            key={doc.id}
            className={`
              card cursor-pointer transition-all duration-200 hover:shadow-md
              ${selectedDocuments.includes(doc.id) 
                ? 'ring-2 ring-primary-500 bg-primary-50 dark:bg-primary-900/20' 
                : ''
              }
            `}
            onClick={() => {
              if (selectedDocuments.includes(doc.id)) {
                deselectDocument(doc.id);
              } else {
                selectDocument(doc.id);
              }
            }}
          >
            <div className="flex items-start gap-3">
              {/* Checkbox */}
              <div className="mt-1">
                {selectedDocuments.includes(doc.id) ? (
                  <div className="w-5 h-5 rounded bg-primary-500 flex items-center justify-center">
                    <CheckCircle className="w-4 h-4 text-white" />
                  </div>
                ) : (
                  <div className="w-5 h-5 rounded border-2 border-gray-300 dark:border-gray-600" />
                )}
              </div>

              {/* Icon */}
              <div className={`p-2 rounded-lg ${getFileTypeColor(doc.type)}`}>
                <FileText className="w-5 h-5" />
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1 min-w-0">
                    <h3 className="font-medium text-gray-900 dark:text-white truncate">
                      {doc.name}
                    </h3>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-xs text-gray-500">{formatFileSize(doc.size)}</span>
                      <span className="text-gray-300">•</span>
                      <span className="text-xs text-gray-500">{formatDate(doc.uploadDate)}</span>
                      {doc.pageCount && (
                        <>
                          <span className="text-gray-300">•</span>
                          <span className="text-xs text-gray-500">{doc.pageCount} pages</span>
                        </>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-1">
                    {getStatusIcon(doc.status)}
                  </div>
                </div>

                {/* Tags */}
                {doc.tags && doc.tags.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {doc.tags.map((tag, index) => (
                      <span
                        key={index}
                        className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300"
                      >
                        <Tag className="w-3 h-3 mr-1" />
                        {tag}
                      </span>
                    ))}
                  </div>
                )}

                {/* Actions */}
                <div className="flex items-center gap-2 mt-3 pt-3 border-t border-gray-100 dark:border-gray-700">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      // Preview action
                    }}
                    className="flex items-center gap-1 text-xs text-gray-500 hover:text-primary-600 transition-colors"
                  >
                    <Eye className="w-3 h-3" />
                    Preview
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      // Download action
                    }}
                    className="flex items-center gap-1 text-xs text-gray-500 hover:text-primary-600 transition-colors"
                  >
                    <Download className="w-3 h-3" />
                    Download
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      // Share action
                    }}
                    className="flex items-center gap-1 text-xs text-gray-500 hover:text-primary-600 transition-colors"
                  >
                    <Share2 className="w-3 h-3" />
                    Share
                  </button>
                  <div className="flex-1" />
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      removeDocument(doc.id);
                    }}
                    className="flex items-center gap-1 text-xs text-red-500 hover:text-red-700 transition-colors"
                  >
                    <Trash2 className="w-3 h-3" />
                    Delete
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))
      )}

      {documents.length > 0 && (
        <div className="pt-3 border-t border-gray-200 dark:border-gray-700">
          <p className="text-xs text-gray-500 dark:text-gray-400 text-center">
            {selectedDocuments.length} of {documents.length} documents selected
          </p>
        </div>
      )}
    </div>
  );
};
