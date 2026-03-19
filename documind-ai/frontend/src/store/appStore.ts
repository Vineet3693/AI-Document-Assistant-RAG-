import { create } from 'zustand';
import { Document } from '../api/documents';

interface AppState {
  documents: Document[];
  selectedDocumentIds: string[];
  isUploading: boolean;
  uploadProgress: number;
  currentQuery: string;
  queryResponse: any | null;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  setDocuments: (docs: Document[]) => void;
  addDocument: (doc: Document) => void;
  removeDocument: (id: string) => void;
  toggleDocumentSelection: (id: string) => void;
  clearDocumentSelection: () => void;
  setUploading: (uploading: boolean) => void;
  setUploadProgress: (progress: number) => void;
  setCurrentQuery: (query: string) => void;
  setQueryResponse: (response: any) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useAppStore = create<AppState>((set) => ({
  // Initial state
  documents: [],
  selectedDocumentIds: [],
  isUploading: false,
  uploadProgress: 0,
  currentQuery: '',
  queryResponse: null,
  isLoading: false,
  error: null,

  // Actions
  setDocuments: (docs) => set({ documents: docs }),
  
  addDocument: (doc) => set((state) => ({ 
    documents: [...state.documents, doc] 
  })),
  
  removeDocument: (id) => set((state) => ({ 
    documents: state.documents.filter(d => d.id !== id),
    selectedDocumentIds: state.selectedDocumentIds.filter(sid => sid !== id)
  })),
  
  toggleDocumentSelection: (id) => set((state) => ({
    selectedDocumentIds: state.selectedDocumentIds.includes(id)
      ? state.selectedDocumentIds.filter(sid => sid !== id)
      : [...state.selectedDocumentIds, id]
  })),
  
  clearDocumentSelection: () => set({ selectedDocumentIds: [] }),
  
  setUploading: (uploading) => set({ isUploading: uploading }),
  
  setUploadProgress: (progress) => set({ uploadProgress: progress }),
  
  setCurrentQuery: (query) => set({ currentQuery: query }),
  
  setQueryResponse: (response) => set({ queryResponse: response }),
  
  setLoading: (loading) => set({ isLoading: loading }),
  
  setError: (error) => set({ error }),
}));
