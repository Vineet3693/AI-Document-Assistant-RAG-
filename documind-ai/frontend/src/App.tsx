import React, { useEffect } from 'react';
import { DocumentTextIcon, CloudArrowUpIcon, ChatBubbleLeftRightIcon, Bars3Icon } from '@heroicons/react/24/outline';
import { DocumentUploader } from './components/DocumentUploader';
import { DocumentList } from './components/DocumentList';
import { ChatInterface } from './components/ChatInterface';
import { useAppStore } from './store/appStore';
import { documentsApi } from './api/documents';

function App() {
  const setDocuments = useAppStore((state) => state.setDocuments);
  const error = useAppStore((state) => state.error);
  const setError = useAppStore((state) => state.setError);
  
  const [sidebarOpen, setSidebarOpen] = React.useState(true);

  // Load documents on mount
  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      const docs = await documentsApi.getAll();
      setDocuments(docs);
    } catch (error) {
      console.error('Failed to load documents:', error);
      setError('Failed to load documents. Please refresh the page.');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="flex items-center justify-between px-4 py-3">
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 rounded-md hover:bg-gray-100 lg:hidden"
            >
              <Bars3Icon className="h-6 w-6" />
            </button>
            
            <div className="flex items-center space-x-2">
              <DocumentTextIcon className="h-8 w-8 text-primary-600" />
              <div>
                <h1 className="text-xl font-bold text-gray-900">DocuMind AI</h1>
                <p className="text-xs text-gray-500">Enterprise Document Assistant</p>
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-500">v3.0.0 Enterprise</span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex h-[calc(100vh-64px)]">
        {/* Sidebar */}
        <aside
          className={`
            ${sidebarOpen ? 'w-80' : 'w-0'} 
            bg-white border-r border-gray-200 overflow-hidden transition-all duration-300
            fixed lg:relative z-10 h-full
          `}
        >
          <div className="p-4 h-full flex flex-col w-80">
            <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-4">
              Documents
            </h2>
            
            {/* Upload Area */}
            <div className="mb-4">
              <DocumentUploader />
            </div>

            {/* Document List */}
            <div className="flex-1 overflow-y-auto">
              <DocumentList />
            </div>

            {/* Stats */}
            <div className="mt-4 pt-4 border-t border-gray-200">
              <p className="text-xs text-gray-500 text-center">
                Upload PDF, DOCX, TXT, or CSV files
              </p>
            </div>
          </div>
        </aside>

        {/* Main Chat Area */}
        <main className="flex-1 flex flex-col overflow-hidden">
          {error && (
            <div className="bg-red-50 border-b border-red-200 px-4 py-2">
              <p className="text-sm text-red-700">{error}</p>
              <button
                onClick={() => setError(null)}
                className="text-xs text-red-600 hover:text-red-800 mt-1"
              >
                Dismiss
              </button>
            </div>
          )}

          <ChatInterface />
        </main>
      </div>
    </div>
  );
}

export default App;
