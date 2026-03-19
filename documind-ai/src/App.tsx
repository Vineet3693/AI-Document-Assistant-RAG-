import React, { useState } from 'react';
import { FileText, MessageSquare, Upload, BarChart3, Shield, Zap, CheckCircle, ArrowRight } from 'lucide-react';
import { DocumentUpload } from './components/DocumentUpload';
import { DocumentList } from './components/DocumentList';
import { ChatInterface } from './components/ChatInterface';
import { Sidebar } from './components/Sidebar';
import { useAppStore } from './store/useAppStore';

type View = 'dashboard' | 'documents' | 'chat' | 'analytics' | 'teams' | 'settings';

function App() {
  const [currentView, setCurrentView] = useState<View>('dashboard');
  const currentMode = useAppStore((state) => state.currentMode);
  const documents = useAppStore((state) => state.documents);
  const toggleSidebar = useAppStore((state) => state.toggleSidebar);

  const features = [
    {
      icon: FileText,
      title: 'Smart Document Analysis',
      description: 'Upload PDFs, Word docs, Excel sheets & more. Get instant insights.',
      color: 'blue',
    },
    {
      icon: MessageSquare,
      title: 'AI-Powered Q&A',
      description: 'Ask anything about your documents. Get accurate, cited answers.',
      color: 'purple',
    },
    {
      icon: Zap,
      title: 'Multi-Document Intelligence',
      description: 'Compare documents, find patterns across files instantly.',
      color: 'yellow',
    },
    {
      icon: Shield,
      title: 'Enterprise Security',
      description: 'GDPR, HIPAA, SOC2 compliant. Your data stays protected.',
      color: 'green',
    },
  ];

  const renderDashboard = () => (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="text-center py-12">
        <h1 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-4">
          Welcome to <span className="text-primary-600">DocuMind AI</span>
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
          Upload any document. Ask anything. Get accurate, cited, instant answers.
          Trusted by legal, finance, healthcare, and enterprise teams worldwide.
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card text-center">
          <FileText className="w-12 h-12 text-primary-600 mx-auto mb-3" />
          <h3 className="text-3xl font-bold text-gray-900 dark:text-white">{documents.length}</h3>
          <p className="text-gray-500 dark:text-gray-400">Documents Uploaded</p>
        </div>
        <div className="card text-center">
          <MessageSquare className="w-12 h-12 text-purple-600 mx-auto mb-3" />
          <h3 className="text-3xl font-bold text-gray-900 dark:text-white">0</h3>
          <p className="text-gray-500 dark:text-gray-400">Questions Asked</p>
        </div>
        <div className="card text-center">
          <BarChart3 className="w-12 h-12 text-green-600 mx-auto mb-3" />
          <h3 className="text-3xl font-bold text-gray-900 dark:text-white">100%</h3>
          <p className="text-gray-500 dark:text-gray-400">Accuracy Rate</p>
        </div>
      </div>

      {/* Features Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {features.map((feature, index) => (
          <div key={index} className="card hover:shadow-lg transition-shadow">
            <div className={`w-14 h-14 rounded-xl bg-${feature.color}-100 dark:bg-${feature.color}-900/20 flex items-center justify-center mb-4`}>
              <feature.icon className={`w-7 h-7 text-${feature.color}-600`} />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              {feature.title}
            </h3>
            <p className="text-gray-600 dark:text-gray-400 text-sm">
              {feature.description}
            </p>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upload Section */}
        <div className="card">
          <div className="flex items-center gap-3 mb-4">
            <Upload className="w-6 h-6 text-primary-600" />
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
              Upload Documents
            </h2>
          </div>
          <DocumentUpload />
        </div>

        {/* Recent Documents */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <FileText className="w-6 h-6 text-primary-600" />
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                Recent Documents
              </h2>
            </div>
            <button 
              onClick={() => setCurrentView('documents')}
              className="text-sm text-primary-600 hover:text-primary-700 flex items-center gap-1"
            >
              View All <ArrowRight className="w-4 h-4" />
            </button>
          </div>
          <DocumentList />
        </div>
      </div>

      {/* Industry Modes */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">
          Choose Your Industry Mode
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
          {[
            { mode: 'standard', label: 'Standard', icon: '💬' },
            { mode: 'legal', label: 'Legal', icon: '⚖️' },
            { mode: 'financial', label: 'Finance', icon: '💰' },
            { mode: 'healthcare', label: 'Healthcare', icon: '🏥' },
            { mode: 'education', label: 'Education', icon: '🎓' },
            { mode: 'research', label: 'Research', icon: '🔬' },
            { mode: 'summary', label: 'Summary', icon: '📋' },
          ].map((item) => (
            <button
              key={item.mode}
              onClick={() => {
                setCurrentView('chat');
              }}
              className={`
                p-4 rounded-xl border-2 transition-all text-center
                ${currentMode === item.mode
                  ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                  : 'border-gray-200 dark:border-gray-700 hover:border-primary-300'
                }
              `}
            >
              <div className="text-2xl mb-2">{item.icon}</div>
              <div className="text-sm font-medium text-gray-900 dark:text-white">
                {item.label}
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );

  const renderContent = () => {
    switch (currentView) {
      case 'dashboard':
        return renderDashboard();
      case 'documents':
        return (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Documents</h1>
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-1">
                <div className="card sticky top-6">
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                    Upload New
                  </h2>
                  <DocumentUpload />
                </div>
              </div>
              <div className="lg:col-span-2">
                <div className="card">
                  <DocumentList />
                </div>
              </div>
            </div>
          </div>
        );
      case 'chat':
        return (
          <div className="h-[calc(100vh-2rem)]">
            <ChatInterface mode={currentMode} />
          </div>
        );
      case 'analytics':
      case 'teams':
      case 'settings':
        return (
          <div className="text-center py-20">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
              Coming Soon
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              This feature is under development and will be available soon.
            </p>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="flex min-h-screen bg-gray-50 dark:bg-gray-900">
      <Sidebar currentView={currentView} onViewChange={setCurrentView} />
      
      <main className="flex-1 flex flex-col min-w-0">
        {/* Mobile Header */}
        <header className="lg:hidden bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 py-3">
          <div className="flex items-center justify-between">
            <button onClick={toggleSidebar} className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            <span className="font-semibold text-gray-900 dark:text-white">DocuMind AI</span>
            <div className="w-10" />
          </div>
        </header>

        {/* Main Content */}
        <div className="flex-1 p-4 md:p-6 lg:p-8 overflow-auto">
          {renderContent()}
        </div>
      </main>
    </div>
  );
}

export default App;
