import React, { useState } from 'react';
import { PaperAirplaneIcon, ChatBubbleLeftRightIcon } from '@heroicons/react/24/outline';
import ReactMarkdown from 'react-markdown';
import { documentsApi, QueryResponse } from '../../api/documents';
import { useAppStore } from '../../store/appStore';

export function ChatInterface() {
  const [question, setQuestion] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const selectedDocumentIds = useAppStore((state) => state.selectedDocumentIds);
  const setQueryResponse = useAppStore((state) => state.setQueryResponse);
  const queryResponse = useAppStore((state) => state.queryResponse);
  const setLoading = useAppStore((state) => state.setLoading);
  const setError = useAppStore((state) => state.setError);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!question.trim()) return;

    setIsLoading(true);
    setLoading(true);
    setError(null);

    try {
      const response = await documentsApi.query(
        question,
        selectedDocumentIds.length > 0 ? selectedDocumentIds : undefined
      );
      
      setQueryResponse(response);
      setQuestion('');
    } catch (error) {
      console.error('Query failed:', error);
      setError('Failed to get answer. Please try again.');
    } finally {
      setIsLoading(false);
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Response Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {!queryResponse ? (
          <div className="text-center py-12">
            <ChatBubbleLeftRightIcon className="mx-auto h-16 w-16 text-gray-300" />
            <h3 className="mt-4 text-lg font-medium text-gray-900">Ask a question</h3>
            <p className="mt-2 text-sm text-gray-500">
              {selectedDocumentIds.length > 0
                ? `Asking across ${selectedDocumentIds.length} selected document(s)`
                : 'Select documents or ask about all your uploaded files'}
            </p>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Answer */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">
                  Answer
                </h3>
                <span className={`
                  px-2 py-1 text-xs font-medium rounded-full
                  ${queryResponse.confidence === 'high' 
                    ? 'bg-green-100 text-green-800' 
                    : queryResponse.confidence === 'medium'
                    ? 'bg-yellow-100 text-yellow-800'
                    : 'bg-red-100 text-red-800'
                  }
                `}>
                  {queryResponse.confidence.toUpperCase()} CONFIDENCE ({queryResponse.confidenceScore}%)
                </span>
              </div>
              
              <div className="prose prose-sm max-w-none">
                <ReactMarkdown>{queryResponse.answer}</ReactMarkdown>
              </div>

              {/* Sources */}
              {queryResponse.sources && queryResponse.sources.length > 0 && (
                <div className="mt-6 pt-4 border-t border-gray-200">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Sources:</h4>
                  <ul className="space-y-1">
                    {queryResponse.sources.map((source: any, idx: number) => (
                      <li key={idx} className="text-sm text-gray-600">
                        • {source.documentName}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Citations */}
              {queryResponse.citations && queryResponse.citations.length > 0 && (
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Citations:</h4>
                  <div className="space-y-3">
                    {queryResponse.citations.map((citation: any, idx: number) => (
                      <div key={idx} className="bg-gray-50 rounded p-3 text-sm">
                        <p className="text-gray-600 italic">"{citation.quote}"</p>
                        <p className="mt-1 text-xs text-gray-500">
                          — {citation.documentName}
                          {citation.pageNumber && `, Page ${citation.pageNumber}`}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-200 p-4 bg-white">
        <form onSubmit={handleSubmit} className="flex space-x-3">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask anything about your documents..."
            className="flex-1 input"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !question.trim()}
            className="btn-primary flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <PaperAirplaneIcon className="h-5 w-5" />
            <span>{isLoading ? 'Thinking...' : 'Send'}</span>
          </button>
        </form>
        
        {selectedDocumentIds.length > 0 && (
          <p className="mt-2 text-xs text-gray-500">
            Querying {selectedDocumentIds.length} selected document(s)
          </p>
        )}
      </div>
    </div>
  );
}
