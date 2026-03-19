import { Document, QueryRequest, SummaryRequest, ComparisonRequest } from '../types';
import { v4 as uuidv4 } from 'uuid';
import fs from 'fs/promises';
import path from 'path';
import { config } from '../config';
import { documentProcessor } from './documentProcessor';
import { vectorStore } from './vectorStore';
import { aiService } from './aiService';

/**
 * In-memory document store (replace with database in production)
 */
class DocumentStore {
  private documents: Map<string, Document> = new Map();
  private userDocuments: Map<string, string[]> = new Map(); // userId -> documentIds

  async save(document: Document): Promise<void> {
    this.documents.set(document.id, document);
    
    const userDocs = this.userDocuments.get(document.userId) || [];
    if (!userDocs.includes(document.id)) {
      userDocs.push(document.id);
      this.userDocuments.set(document.userId, userDocs);
    }
  }

  async findById(id: string): Promise<Document | undefined> {
    return this.documents.get(id);
  }

  async findByUser(userId: string): Promise<Document[]> {
    const docIds = this.userDocuments.get(userId) || [];
    return docIds
      .map(id => this.documents.get(id))
      .filter((doc): doc is Document => !!doc);
  }

  async update(id: string, updates: Partial<Document>): Promise<Document | undefined> {
    const doc = this.documents.get(id);
    if (!doc) return undefined;
    
    const updated = { ...doc, ...updates };
    this.documents.set(id, updated);
    return updated;
  }

  async delete(id: string): Promise<boolean> {
    const doc = this.documents.get(id);
    if (!doc) return false;
    
    this.documents.delete(id);
    
    const userDocs = this.userDocuments.get(doc.userId) || [];
    const filtered = userDocs.filter(docId => docId !== id);
    this.userDocuments.set(doc.userId, filtered);
    
    return true;
  }

  async getAll(): Promise<Document[]> {
    return Array.from(this.documents.values());
  }
}

/**
 * Document Management Service
 * Handles document CRUD operations and processing pipeline
 */
export class DocumentService {
  private store: DocumentStore;

  constructor() {
    this.store = new DocumentStore();
  }

  /**
   * Create document record and process file
   */
  async createDocument(
    filePath: string,
    originalName: string,
    mimeType: string,
    size: number,
    userId: string,
    options: {
      tags?: string[];
      category?: string;
      accessLevel?: 'public' | 'private' | 'team';
      teamIds?: string[];
    } = {}
  ): Promise<Document> {
    const documentId = uuidv4();
    const now = new Date();

    // Create document record
    const document: Document = {
      id: documentId,
      name: originalName.replace(/\.[^/.]+$/, ''), // Remove extension
      originalName,
      mimeType,
      size,
      path: filePath,
      status: 'processing',
      uploadedAt: now,
      expiresAt: config.document.expiryDays > 0 
        ? new Date(now.getTime() + config.document.expiryDays * 24 * 60 * 60 * 1000)
        : undefined,
      tags: options.tags || [],
      category: options.category,
      version: 1,
      accessLevel: options.accessLevel || 'private',
      teamIds: options.teamIds,
      userId,
      metadata: {},
    };

    // Save initial record
    await this.store.save(document);

    // Process document asynchronously
    this.processDocumentAsync(document).catch(error => {
      console.error(`Failed to process document ${documentId}:`, error);
      this.store.update(documentId, { status: 'failed' });
    });

    return document;
  }

  /**
   * Process document: extract text, chunk, and embed
   */
  private async processDocumentAsync(document: Document): Promise<void> {
    try {
      console.log(`📄 Processing document: ${document.originalName}`);

      // Extract text and create chunks
      const { chunks, metadata } = await documentProcessor.processDocument(
        document,
        document.path
      );

      console.log(`✅ Extracted ${chunks.length} chunks from ${document.originalName}`);

      // Generate embeddings
      const embeddings = await vectorStore.generateEmbeddings(chunks);
      console.log(`✅ Generated ${embeddings.length} embeddings`);

      // Store vectors
      const vectorIds = await vectorStore.upsertChunks(document.id, chunks, embeddings);
      console.log(`✅ Stored ${vectorIds.length} vectors`);

      // Update document with metadata and embedding info
      await this.store.update(document.id, {
        status: 'ready',
        metadata: {
          ...metadata,
        },
        embeddings: {
          indexed: true,
          vectorIds,
          chunkCount: chunks.length,
        },
      });

      console.log(`✅ Document ${document.originalName} processing complete`);
    } catch (error) {
      console.error(`❌ Error processing document ${document.id}:`, error);
      await this.store.update(document.id, {
        status: 'failed',
      });
      throw error;
    }
  }

  /**
   * Get document by ID
   */
  async getDocument(id: string): Promise<Document | undefined> {
    return this.store.findById(id);
  }

  /**
   * Get all documents for a user
   */
  async getUserDocuments(userId: string): Promise<Document[]> {
    return this.store.findByUser(userId);
  }

  /**
   * Get all documents (admin)
   */
  async getAllDocuments(): Promise<Document[]> {
    return this.store.getAll();
  }

  /**
   * Update document metadata
   */
  async updateDocument(
    id: string,
    updates: {
      tags?: string[];
      category?: string;
      accessLevel?: 'public' | 'private' | 'team';
      teamIds?: string[];
    }
  ): Promise<Document | undefined> {
    return this.store.update(id, updates);
  }

  /**
   * Delete document and associated vectors
   */
  async deleteDocument(id: string): Promise<boolean> {
    const document = await this.store.findById(id);
    if (!document) return false;

    try {
      // Delete vectors
      await vectorStore.deleteDocumentVectors(id);

      // Delete file
      await fs.unlink(document.path).catch(err => {
        console.warn(`Failed to delete file ${document.path}:`, err.message);
      });

      // Delete record
      await this.store.delete(id);

      console.log(`✅ Deleted document ${document.originalName}`);
      return true;
    } catch (error) {
      console.error(`Error deleting document ${id}:`, error);
      return false;
    }
  }

  /**
   * Query documents using RAG
   */
  async queryDocuments(
    request: QueryRequest,
    userId: string
  ): Promise<any> {
    const { question, documentIds, mode, industry, language } = request;

    // Get accessible documents
    let accessibleDocIds = documentIds;
    if (!accessibleDocIds || accessibleDocIds.length === 0) {
      const userDocs = await this.getUserDocuments(userId);
      accessibleDocIds = userDocs
        .filter(doc => doc.status === 'ready')
        .map(doc => doc.id);
    }

    if (accessibleDocIds.length === 0) {
      return {
        answer: "I couldn't find any documents to search. Please upload documents first.",
        citations: [],
        confidence: 'low' as const,
        confidenceScore: 0,
        reasoning: 'No documents available',
        sources: [],
      };
    }

    // Search for relevant chunks
    const searchResults = await vectorStore.searchSimilar(question, {
      documentIds: accessibleDocIds,
      topK: 10,
    });

    if (searchResults.length === 0) {
      return {
        answer: `I could not find this in the documents. The documents available are: ${accessibleDocIds.join(', ')}`,
        citations: [],
        confidence: 'low' as const,
        confidenceScore: 0,
        reasoning: 'No relevant content found',
        sources: [],
      };
    }

    // Build context from chunks
    const context = searchResults
      .map((result, idx) => `[Source ${idx + 1}] ${result.chunk.content}`)
      .join('\n\n');

    // Get document names
    const docNames = await Promise.all(
      searchResults.map(async result => {
        const doc = await this.getDocument(result.chunk.documentId);
        return doc?.originalName || 'Unknown';
      })
    );

    // Generate answer using AI
    const response = await aiService.answerQuestion(question, context, {
      documentNames: [...new Set(docNames)],
      language,
      industry,
      mode,
    });

    return response;
  }

  /**
   * Summarize document
   */
  async summarizeDocument(request: SummaryRequest): Promise<any> {
    const document = await this.store.findById(request.documentId);
    if (!document) {
      throw new Error('Document not found');
    }

    // Extract text from document
    const { text } = await documentProcessor.extractText(
      document.path,
      document.mimeType
    );

    // Generate summary
    return aiService.summarizeDocument(text, {
      documentName: document.originalName,
      documentType: document.mimeType,
      industry: request.industry,
      summaryType: request.summaryType,
    });
  }

  /**
   * Compare two documents
   */
  async compareDocuments(request: ComparisonRequest): Promise<any> {
    const [doc1, doc2] = await Promise.all([
      this.store.findById(request.documentId1),
      this.store.findById(request.documentId2),
    ]);

    if (!doc1 || !doc2) {
      throw new Error('One or both documents not found');
    }

    // Extract text from both documents
    const [text1, text2] = await Promise.all([
      documentProcessor.extractText(doc1.path, doc1.mimeType),
      documentProcessor.extractText(doc2.path, doc2.mimeType),
    ]);

    // Generate comparison
    return aiService.compareDocuments(text1.text, text2.text, {
      doc1Name: doc1.originalName,
      doc2Name: doc2.originalName,
      comparisonType: request.comparisonType,
    });
  }

  /**
   * Extract information from document
   */
  async extractInformation(
    documentId: string,
    extractionType: 'entities' | 'financial' | 'legal' | 'contacts' | 'all'
  ): Promise<any> {
    const document = await this.store.findById(documentId);
    if (!document) {
      throw new Error('Document not found');
    }

    // Extract text
    const { text } = await documentProcessor.extractText(
      document.path,
      document.mimeType
    );

    // Extract information
    return aiService.extractInformation(text, extractionType);
  }

  /**
   * Get document statistics
   */
  async getStats(): Promise<{
    totalDocuments: number;
    readyDocuments: number;
    processingDocuments: number;
    failedDocuments: number;
    totalChunks: number;
  }> {
    const documents = await this.store.getAll();
    
    return {
      totalDocuments: documents.length,
      readyDocuments: documents.filter(d => d.status === 'ready').length,
      processingDocuments: documents.filter(d => d.status === 'processing').length,
      failedDocuments: documents.filter(d => d.status === 'failed').length,
      totalChunks: documents.reduce((sum, d) => sum + (d.embeddings?.chunkCount || 0), 0),
    };
  }
}

// Singleton instance
export const documentService = new DocumentService();
