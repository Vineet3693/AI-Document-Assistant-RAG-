import axios from 'axios';
import type { 
  Document, 
  Message, 
  DocumentSummary, 
  DocumentComparison,
  LegalAnalysis,
  FinancialAnalysis,
  ResumeEvaluation,
  APIResponse,
  UploadProgress 
} from '../types';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Document Services
export const documentService = {
  upload: async (file: File, onProgress?: (progress: number) => void): Promise<Document> => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post<APIResponse<Document>>('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(percentCompleted);
        }
      },
    });
    
    return response.data.data!;
  },

  getAll: async (): Promise<Document[]> => {
    const response = await api.get<APIResponse<Document[]>>('/documents');
    return response.data.data || [];
  },

  getById: async (id: string): Promise<Document> => {
    const response = await api.get<APIResponse<Document>>(`/documents/${id}`);
    return response.data.data!;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/documents/${id}`);
  },

  update: async (id: string, updates: Partial<Document>): Promise<Document> => {
    const response = await api.put<APIResponse<Document>>(`/documents/${id}`, updates);
    return response.data.data!;
  },

  getSummary: async (id: string): Promise<DocumentSummary> => {
    const response = await api.post<APIResponse<DocumentSummary>>(`/documents/${id}/summary`);
    return response.data.data!;
  },

  extractInfo: async (id: string): Promise<any> => {
    const response = await api.post<APIResponse<any>>(`/documents/${id}/extract`);
    return response.data.data!;
  },
};

// Chat & Q&A Services
export const chatService = {
  askQuestion: async (
    question: string, 
    documentIds: string[],
    mode: string = 'standard'
  ): Promise<Message> => {
    const response = await api.post<APIResponse<Message>>('/chat/ask', {
      question,
      documentIds,
      mode,
    });
    return response.data.data!;
  },

  followUp: async (
    sessionId: string,
    question: string
  ): Promise<Message> => {
    const response = await api.post<APIResponse<Message>>('/chat/followup', {
      sessionId,
      question,
    });
    return response.data.data!;
  },
};

// Analysis Services
export const analysisService = {
  compareDocuments: async (doc1Id: string, doc2Id: string): Promise<DocumentComparison> => {
    const response = await api.post<APIResponse<DocumentComparison>>('/analysis/compare', {
      doc1Id,
      doc2Id,
    });
    return response.data.data!;
  },

  legalReview: async (documentId: string): Promise<LegalAnalysis> => {
    const response = await api.post<APIResponse<LegalAnalysis>>('/analysis/legal', {
      documentId,
    });
    return response.data.data!;
  },

  financialAnalysis: async (documentId: string): Promise<FinancialAnalysis> => {
    const response = await api.post<APIResponse<FinancialAnalysis>>('/analysis/financial', {
      documentId,
    });
    return response.data.data!;
  },

  resumeScreening: async (
    resumeId: string,
    jobDescription: string,
    requiredSkills: string[]
  ): Promise<ResumeEvaluation> => {
    const response = await api.post<APIResponse<ResumeEvaluation>>('/analysis/resume', {
      resumeId,
      jobDescription,
      requiredSkills,
    });
    return response.data.data!;
  },
};

// Export Service
export const exportService = {
  exportChatAsPDF: async (sessionId: string): Promise<Blob> => {
    const response = await api.post('/export/chat/pdf', { sessionId }, {
      responseType: 'blob',
    });
    return response.data;
  },

  exportSummaryAsWord: async (documentId: string): Promise<Blob> => {
    const response = await api.post('/export/summary/word', { documentId }, {
      responseType: 'blob',
    });
    return response.data;
  },

  exportComparisonAsExcel: async (doc1Id: string, doc2Id: string): Promise<Blob> => {
    const response = await api.post('/export/comparison/excel', { doc1Id, doc2Id }, {
      responseType: 'blob',
    });
    return response.data;
  },
};

// Mock implementation for development (when backend is not available)
export const mockServices = {
  simulateUpload: async (file: File): Promise<Document> => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          id: crypto.randomUUID(),
          name: file.name,
          type: file.name.split('.').pop() as any,
          size: file.size,
          uploadDate: new Date(),
          status: 'ready',
          tags: [],
          version: 1,
          accessLevel: 'private',
          pageCount: Math.floor(Math.random() * 50) + 1,
        });
      }, 2000);
    });
  },

  simulateQA: async (question: string, documentNames: string[]): Promise<Message> => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          id: crypto.randomUUID(),
          role: 'assistant',
          content: `Based on the documents provided (${documentNames.join(', ')}), I found relevant information about "${question}".\n\n✅ Direct Answer:\nThe answer to your question can be found in the uploaded documents with high confidence.\n\n📌 Key Details:\n• This information was extracted from the primary source document\n• The context suggests this is a key point in the document\n• Multiple sections reference this topic\n\n📄 Source:\nDocument: ${documentNames[0] || 'Sample Document'}\nLocation: Page 3 / Section 2.1\nQuote: "This is a sample quote from the document that relates to your question."\n\n🔍 Confidence: High\nReason: The answer is explicitly stated in the document with clear context.`,
          timestamp: new Date(),
          sources: [{
            documentId: 'mock-1',
            documentName: documentNames[0] || 'Sample Document',
            pageNumber: 3,
            section: '2.1',
            quote: 'This is a sample quote from the document that relates to your question.',
          }],
          confidence: 95,
          followUpQuestions: [
            'Can you elaborate on this point?',
            'What are the implications of this?',
            'Are there any related sections in other documents?',
          ],
        });
      }, 1500);
    });
  },

  simulateSummary: async (documentName: string): Promise<DocumentSummary> => {
    return {
      oneLine: `This document provides a comprehensive overview of ${documentName}.`,
      executive: `The document titled "${documentName}" contains critical information for decision-makers. It outlines key strategies, identifies potential risks, and provides actionable recommendations for stakeholders.`,
      keyPoints: [
        'Primary objective clearly defined with measurable outcomes',
        'Risk assessment completed with mitigation strategies',
        'Timeline established with key milestones',
        'Budget allocation detailed across all departments',
        'Success metrics defined for evaluation',
      ],
      importantData: {
        numbers: ['$1.5M budget', 'Q4 2024 deadline', '15% growth target'],
        dates: ['January 15, 2024', 'March 30, 2024', 'December 31, 2024'],
        people: ['John Smith (CEO)', 'Sarah Johnson (CFO)', 'Michael Chen (CTO)'],
        companies: ['Acme Corp', 'TechStart Inc', 'Global Solutions LLC'],
      },
      actionItems: [
        'Review budget allocation by end of week - Finance Team',
        'Schedule stakeholder meeting for next Monday - Project Manager',
        'Submit compliance documentation by Friday - Legal Team',
      ],
      risks: ['Market volatility may impact Q3 projections', 'Resource constraints in engineering team'],
      bottomLine: 'Proceed with implementation while monitoring identified risks closely.',
    };
  },
};
