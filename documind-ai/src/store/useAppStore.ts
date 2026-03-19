import { create } from 'zustand';
import type { Document, ChatSession, Message, ChatMode, AppSettings, UploadProgress } from '../types';

interface AppState {
  // Documents
  documents: Document[];
  selectedDocuments: string[]; // document IDs
  
  // Chat
  chatSessions: ChatSession[];
  currentSessionId: string | null;
  
  // Upload
  uploadProgress: UploadProgress[];
  
  // Settings
  settings: AppSettings;
  
  // UI State
  sidebarOpen: boolean;
  currentMode: ChatMode;
  
  // Actions
  addDocument: (doc: Document) => void;
  removeDocument: (id: string) => void;
  updateDocument: (id: string, updates: Partial<Document>) => void;
  selectDocument: (id: string) => void;
  deselectDocument: (id: string) => void;
  clearSelectedDocuments: () => void;
  
  createChatSession: (title: string, documentIds: string[], mode?: ChatMode) => string;
  addMessage: (sessionId: string, message: Message) => void;
  setCurrentSession: (sessionId: string | null) => void;
  deleteChatSession: (sessionId: string) => void;
  
  setUploadProgress: (progress: UploadProgress[]) => void;
  
  updateSettings: (settings: Partial<AppSettings>) => void;
  
  toggleSidebar: () => void;
  setMode: (mode: ChatMode) => void;
}

export const useAppStore = create<AppState>((set, get) => ({
  // Initial State
  documents: [],
  selectedDocuments: [],
  chatSessions: [],
  currentSessionId: null,
  uploadProgress: [],
  settings: {
    theme: 'system',
    language: 'en',
    defaultChatMode: 'standard',
    notificationsEnabled: true,
    autoSaveChats: true,
  },
  sidebarOpen: true,
  currentMode: 'standard',
  
  // Document Actions
  addDocument: (doc) => set((state) => ({
    documents: [...state.documents, doc]
  })),
  
  removeDocument: (id) => set((state) => ({
    documents: state.documents.filter(d => d.id !== id),
    selectedDocuments: state.selectedDocuments.filter(sid => sid !== id)
  })),
  
  updateDocument: (id, updates) => set((state) => ({
    documents: state.documents.map(d => 
      d.id === id ? { ...d, ...updates } : d
    )
  })),
  
  selectDocument: (id) => set((state) => ({
    selectedDocuments: [...state.selectedDocuments, id]
  })),
  
  deselectDocument: (id) => set((state) => ({
    selectedDocuments: state.selectedDocuments.filter(sid => sid !== id)
  })),
  
  clearSelectedDocuments: () => set({ selectedDocuments: [] }),
  
  // Chat Actions
  createChatSession: (title, documentIds, mode = 'standard') => {
    const sessionId = crypto.randomUUID();
    const newSession: ChatSession = {
      id: sessionId,
      title,
      messages: [],
      documentIds,
      createdAt: new Date(),
      updatedAt: new Date(),
      mode,
    };
    
    set((state) => ({
      chatSessions: [...state.chatSessions, newSession],
      currentSessionId: sessionId,
      currentMode: mode,
    }));
    
    return sessionId;
  },
  
  addMessage: (sessionId, message) => set((state) => ({
    chatSessions: state.chatSessions.map(session =>
      session.id === sessionId
        ? {
            ...session,
            messages: [...session.messages, message],
            updatedAt: new Date(),
          }
        : session
    )
  })),
  
  setCurrentSession: (sessionId) => set({ currentSessionId: sessionId }),
  
  deleteChatSession: (sessionId) => set((state) => ({
    chatSessions: state.chatSessions.filter(s => s.id !== sessionId),
    currentSessionId: state.currentSessionId === sessionId ? null : state.currentSessionId
  })),
  
  // Upload Actions
  setUploadProgress: (progress) => set({ uploadProgress: progress }),
  
  // Settings Actions
  updateSettings: (newSettings) => set((state) => ({
    settings: { ...state.settings, ...newSettings }
  })),
  
  // UI Actions
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  
  setMode: (mode) => set({ currentMode: mode }),
}));
