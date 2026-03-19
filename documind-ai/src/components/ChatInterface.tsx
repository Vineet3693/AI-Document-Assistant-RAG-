import React, { useState } from 'react';
import { Send, Paperclip, Loader2 } from 'lucide-react';
import type { Message, ChatMode } from '../types';
import { useAppStore } from '../store/useAppStore';
import { mockServices } from '../services/api';

interface ChatInterfaceProps {
  mode?: ChatMode;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({ mode = 'standard' }) => {
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const currentSessionId = useAppStore((state) => state.currentSessionId);
  const addMessage = useAppStore((state) => state.addMessage);
  const documents = useAppStore((state) => state.documents);
  const selectedDocuments = useAppStore((state) => state.selectedDocuments);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    // Add user message
    if (currentSessionId) {
      addMessage(currentSessionId, userMessage);
    }

    setInput('');
    setIsLoading(true);

    try {
      // Get selected document names
      const selectedDocs = documents.filter(d => selectedDocuments.includes(d.id));
      const docNames = selectedDocs.map(d => d.name);

      // Simulate AI response
      const aiResponse = await mockServices.simulateQA(input, docNames.length > 0 ? docNames : ['No documents selected']);
      
      if (currentSessionId) {
        addMessage(currentSessionId, aiResponse);
      }
    } catch (error) {
      console.error('Error getting response:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getModeLabel = (mode: ChatMode): string => {
    const labels: Record<ChatMode, string> = {
      standard: 'Standard Q&A',
      research: 'Research Mode',
      legal: 'Legal Review',
      financial: 'Financial Analysis',
      summary: 'Summary Only',
      healthcare: 'Healthcare',
      education: 'Education',
    };
    return labels[mode];
  };

  return (
    <div className="flex flex-col h-full bg-white dark:bg-gray-800 rounded-xl shadow-lg">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              Document Assistant
            </h2>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Mode: {getModeLabel(mode)} • {selectedDocuments.length} document(s) selected
            </p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {selectedDocuments.length === 0 && (
          <div className="text-center py-8">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 dark:bg-gray-700 mb-4">
              <Paperclip className="w-8 h-8 text-gray-400" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              No Documents Selected
            </h3>
            <p className="text-gray-500 dark:text-gray-400 max-w-md mx-auto">
              Select one or more documents from the sidebar to start asking questions. 
              You can upload new documents or choose from existing ones.
            </p>
          </div>
        )}

        {selectedDocuments.length > 0 && (
          <>
            <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
              <p className="text-sm text-blue-800 dark:text-blue-200">
                👋 Hi! I'm your AI document assistant. Ask me anything about your selected documents, 
                and I'll provide accurate answers with citations.
              </p>
            </div>

            {/* Sample questions */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {[
                'What are the key points in this document?',
                'Summarize the main findings',
                'Are there any risks mentioned?',
                'What are the action items?',
              ].map((question, index) => (
                <button
                  key={index}
                  onClick={() => setInput(question)}
                  className="text-left px-4 py-3 bg-gray-50 dark:bg-gray-700/50 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg text-sm text-gray-700 dark:text-gray-300 transition-colors"
                >
                  {question}
                </button>
              ))}
            </div>
          </>
        )}
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="p-4 border-t border-gray-200 dark:border-gray-700">
        <div className="flex gap-3">
          <div className="flex-1 relative">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={selectedDocuments.length > 0 ? "Ask a question about your documents..." : "Select documents first..."}
              disabled={isLoading || selectedDocuments.length === 0}
              className="input-field pr-12"
            />
          </div>
          <button
            type="submit"
            disabled={!input.trim() || isLoading || selectedDocuments.length === 0}
            className="btn-primary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
            <span className="hidden sm:inline">Send</span>
          </button>
        </div>
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-2 text-center">
          AI can make mistakes. Always verify important information from source documents.
        </p>
      </form>
    </div>
  );
};
