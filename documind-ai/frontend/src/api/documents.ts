import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add user headers from localStorage
api.interceptors.request.use((config) => {
  const userId = localStorage.getItem('userId') || 'user-123';
  const userName = localStorage.getItem('userName') || 'Demo User';
  
  if (userId) {
    config.headers['X-User-ID'] = userId;
  }
  if (userName) {
    config.headers['X-User-Name'] = userName;
  }
  
  return config;
});

export interface Document {
  id: string;
  name: string;
  originalName: string;
  mimeType: string;
  size: number;
  status: 'processing' | 'ready' | 'failed';
  uploadedAt: string;
  tags: string[];
  category?: string;
  accessLevel: 'public' | 'private' | 'team';
  embeddings?: {
    indexed: boolean;
    chunkCount: number;
  };
}

export interface QueryResponse {
  answer: string;
  citations: Array<{
    documentId: string;
    documentName: string;
    pageNumber?: number;
    quote: string;
  }>;
  confidence: 'high' | 'medium' | 'low';
  confidenceScore: number;
  sources: Array<{
    documentId: string;
    documentName: string;
    contribution: string;
  }>;
}

export interface SummaryResponse {
  oneLineSummary?: string;
  executiveSummary?: string;
  bulletPoints?: string[];
  keyData?: {
    numbers: string[];
    dates: string[];
    people: string[];
    companies: string[];
  };
  actionItems?: string[];
  risks?: string[];
}

export const documentsApi = {
  // Get all documents
  getAll: async (): Promise<Document[]> => {
    const response = await api.get('/documents');
    return response.data.data;
  },

  // Upload document
  upload: async (file: File, options?: { tags?: string[]; category?: string }): Promise<Document> => {
    const formData = new FormData();
    formData.append('file', file);
    
    if (options?.tags) {
      formData.append('tags', JSON.stringify(options.tags));
    }
    if (options?.category) {
      formData.append('category', options.category);
    }

    const response = await api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data.data;
  },

  // Get document by ID
  getById: async (id: string): Promise<Document> => {
    const response = await api.get(`/documents/${id}`);
    return response.data.data;
  },

  // Delete document
  delete: async (id: string): Promise<void> => {
    await api.delete(`/documents/${id}`);
  },

  // Update document
  update: async (id: string, updates: { tags?: string[]; category?: string }): Promise<Document> => {
    const response = await api.put(`/documents/${id}`, updates);
    return response.data.data;
  },

  // Query documents (RAG)
  query: async (question: string, documentIds?: string[]): Promise<QueryResponse> => {
    const response = await api.post('/documents/query', {
      question,
      documentIds,
    });
    return response.data.data;
  },

  // Summarize document
  summarize: async (documentId: string, summaryType: 'one-line' | 'executive' | 'detailed' = 'executive'): Promise<SummaryResponse> => {
    const response = await api.post(`/documents/${documentId}/summarize`, {
      summaryType,
    });
    return response.data.data;
  },

  // Extract information
  extract: async (documentId: string, extractionType: 'entities' | 'financial' | 'legal' | 'contacts' | 'all' = 'all'): Promise<any> => {
    const response = await api.post(`/documents/${documentId}/extract`, {
      extractionType,
    });
    return response.data.data;
  },

  // Compare documents
  compare: async (documentId1: string, documentId2: string): Promise<any> => {
    const response = await api.post('/documents/compare', {
      documentId1,
      documentId2,
    });
    return response.data.data;
  },

  // Get stats
  getStats: async (): Promise<any> => {
    const response = await api.get('/documents/stats/overview');
    return response.data.data;
  },
};

export default api;
