import React from 'react';
import { 
  LayoutDashboard, 
  FileText, 
  MessageSquare, 
  Settings, 
  Users, 
  BarChart3,
  Shield,
  Briefcase,
  Scale,
  GraduationCap,
  HeartPulse,
  Menu,
  X,
  UploadCloud,
  ChevronDown
} from 'lucide-react';
import type { ChatMode } from '../types';
import { useAppStore } from '../store/useAppStore';

interface SidebarProps {
  currentView: string;
  onViewChange: (view: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentView, onViewChange }) => {
  const sidebarOpen = useAppStore((state) => state.sidebarOpen);
  const toggleSidebar = useAppStore((state) => state.toggleSidebar);
  const currentMode = useAppStore((state) => state.currentMode);
  const setMode = useAppStore((state) => state.setMode);
  const documents = useAppStore((state) => state.documents);

  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'documents', label: 'Documents', icon: FileText },
    { id: 'chat', label: 'Chat', icon: MessageSquare },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'teams', label: 'Teams', icon: Users },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  const industryModes: Array<{ id: ChatMode; label: string; icon: any; color: string }> = [
    { id: 'standard', label: 'Standard Q&A', icon: MessageSquare, color: 'text-blue-500' },
    { id: 'legal', label: 'Legal Review', icon: Scale, color: 'text-purple-500' },
    { id: 'financial', label: 'Financial Analysis', icon: Briefcase, color: 'text-green-500' },
    { id: 'healthcare', label: 'Healthcare', icon: HeartPulse, color: 'text-red-500' },
    { id: 'education', label: 'Education', icon: GraduationCap, color: 'text-yellow-500' },
    { id: 'research', label: 'Research Mode', icon: FileText, color: 'text-indigo-500' },
    { id: 'summary', label: 'Summary Only', icon: LayoutDashboard, color: 'text-gray-500' },
  ];

  return (
    <>
      {/* Mobile Overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={toggleSidebar}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed top-0 left-0 z-50 h-full w-72 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700
          transform transition-transform duration-300 ease-in-out
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
          lg:translate-x-0 lg:static lg:z-auto
        `}
      >
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="p-6 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center">
                  <FileText className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-gray-900 dark:text-white">DocuMind AI</h1>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Enterprise v3.0</p>
                </div>
              </div>
              <button
                onClick={toggleSidebar}
                className="lg:hidden p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Scrollable Content */}
          <div className="flex-1 overflow-y-auto p-4 space-y-6">
            {/* Industry Modes */}
            <div>
              <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3 px-2">
                AI Mode
              </h3>
              <div className="space-y-1">
                {industryModes.map((mode) => (
                  <button
                    key={mode.id}
                    onClick={() => setMode(mode.id)}
                    className={`
                      w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors
                      ${currentMode === mode.id
                        ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300'
                        : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
                      }
                    `}
                  >
                    <mode.icon className={`w-5 h-5 ${mode.color}`} />
                    <span>{mode.label}</span>
                    {currentMode === mode.id && (
                      <ChevronDown className="w-4 h-4 ml-auto rotate-[-90deg]" />
                    )}
                  </button>
                ))}
              </div>
            </div>

            {/* Main Navigation */}
            <div>
              <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3 px-2">
                Menu
              </h3>
              <div className="space-y-1">
                {menuItems.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => {
                      onViewChange(item.id);
                      if (window.innerWidth < 1024) {
                        toggleSidebar();
                      }
                    }}
                    className={`
                      w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors
                      ${currentView === item.id
                        ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300'
                        : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
                      }
                    `}
                  >
                    <item.icon className="w-5 h-5" />
                    <span>{item.label}</span>
                    {item.id === 'documents' && documents.length > 0 && (
                      <span className="ml-auto text-xs bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300 px-2 py-0.5 rounded-full">
                        {documents.length}
                      </span>
                    )}
                  </button>
                ))}
              </div>
            </div>

            {/* Quick Stats */}
            <div className="card bg-gradient-to-br from-primary-500 to-primary-700 text-white">
              <div className="flex items-center gap-3 mb-3">
                <UploadCloud className="w-5 h-5" />
                <span className="font-medium">Quick Stats</span>
              </div>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="opacity-80">Documents</span>
                  <span className="font-semibold">{documents.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="opacity-80">Selected</span>
                  <span className="font-semibold">
                    {documents.filter(d => d.status === 'ready').length}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="p-4 border-t border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-3 px-2">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-400 to-pink-400 flex items-center justify-center text-white font-medium text-sm">
                U
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                  User Account
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                  user@company.com
                </p>
              </div>
              <Shield className="w-4 h-4 text-gray-400" />
            </div>
          </div>
        </div>
      </aside>
    </>
  );
};
