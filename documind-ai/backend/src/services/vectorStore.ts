import { Pinecone } from '@pinecone-database/pinecone';
import { OpenAIEmbeddings } from '@langchain/openai';
import { DocumentChunk } from '../types';
import { config } from '../config';

/**
 * Vector Store Service
 * Handles embedding generation and vector database operations
 */
export class VectorStoreService {
  private pinecone: Pinecone | null = null;
  private embeddings: OpenAIEmbeddings;
  private isInitialized = false;

  constructor() {
    this.embeddings = new OpenAIEmbeddings({
      apiKey: config.openai.apiKey,
      model: config.openai.embeddingModel,
    });
  }

  /**
   * Initialize Pinecone connection
   */
  async initialize(): Promise<void> {
    if (this.isInitialized) {
      return;
    }

    try {
      if (!config.pinecone.apiKey) {
        console.warn('⚠️  Pinecone API key not configured. Using in-memory fallback.');
        this.isInitialized = true;
        return;
      }

      this.pinecone = new Pinecone({
        apiKey: config.pinecone.apiKey,
      });

      // Check if index exists, create if not
      const indexList = await this.pinecone.listIndexes();
      const indexExists = indexList.indexes?.some(
        (idx) => idx.name === config.pinecone.indexName
      );

      if (!indexExists) {
        console.log(`Creating Pinecone index: ${config.pinecone.indexName}`);
        await this.pinecone.createIndex({
          name: config.pinecone.indexName,
          dimension: 1536, // text-embedding-3-large dimension
          metric: 'cosine',
          spec: {
            serverless: {
              cloud: 'aws',
              region: 'us-east-1',
            },
          },
        });

        // Wait for index to be ready
        await this.waitForIndexReady();
      }

      this.isInitialized = true;
      console.log('✅ Vector store initialized successfully');
    } catch (error) {
      console.error('❌ Failed to initialize vector store:', error);
      throw error;
    }
  }

  /**
   * Wait for Pinecone index to be ready
   */
  private async waitForIndexReady(maxAttempts = 30): Promise<void> {
    for (let i = 0; i < maxAttempts; i++) {
      try {
        const index = await this.pinecone!.describeIndex(config.pinecone.indexName);
        if (index.status?.ready) {
          return;
        }
      } catch (error) {
        // Index might still be creating
      }
      await new Promise((resolve) => setTimeout(resolve, 2000));
    }
    throw new Error('Index creation timeout');
  }

  /**
   * Generate embeddings for text chunks
   */
  async generateEmbeddings(chunks: DocumentChunk[]): Promise<number[][]> {
    try {
      const texts = chunks.map((chunk) => chunk.content);
      const embeddings = await this.embeddings.embedDocuments(texts);
      
      if (embeddings.length !== chunks.length) {
        throw new Error('Embedding count mismatch');
      }

      return embeddings;
    } catch (error) {
      console.error('Error generating embeddings:', error);
      throw new Error(`Failed to generate embeddings: ${(error as Error).message}`);
    }
  }

  /**
   * Generate embedding for single text
   */
  async generateEmbedding(text: string): Promise<number[]> {
    try {
      const embedding = await this.embeddings.embedQuery(text);
      return embedding;
    } catch (error) {
      console.error('Error generating embedding:', error);
      throw new Error(`Failed to generate embedding: ${(error as Error).message}`);
    }
  }

  /**
   * Upsert document chunks to vector store
   */
  async upsertChunks(documentId: string, chunks: DocumentChunk[], embeddings: number[][]): Promise<string[]> {
    if (!this.pinecone) {
      console.warn('Pinecone not initialized. Skipping vector storage.');
      return chunks.map((c) => c.id);
    }

    try {
      const index = this.pinecone.Index(config.pinecone.indexName);

      // Prepare vectors for upsert
      const vectors = chunks.map((chunk, idx) => ({
        id: chunk.id,
        values: embeddings[idx],
        metadata: {
          documentId: chunk.documentId,
          chunkIndex: chunk.metadata.chunkIndex,
          content: chunk.content,
          ...chunk.metadata,
        },
      }));

      // Upsert in batches of 100 (Pinecone limit)
      const batchSize = 100;
      const vectorIds: string[] = [];

      for (let i = 0; i < vectors.length; i += batchSize) {
        const batch = vectors.slice(i, i + batchSize);
        await index.upsert(batch);
        vectorIds.push(...batch.map((v) => v.id));
      }

      console.log(`✅ Upserted ${vectorIds.length} vectors for document ${documentId}`);
      return vectorIds;
    } catch (error) {
      console.error('Error upserting chunks:', error);
      throw new Error(`Failed to upsert chunks: ${(error as Error).message}`);
    }
  }

  /**
   * Search for relevant chunks based on query
   */
  async searchSimilar(
    query: string,
    options: {
      documentIds?: string[];
      topK?: number;
      filter?: Record<string, any>;
    } = {}
  ): Promise<Array<{ chunk: DocumentChunk; score: number }>> {
    if (!this.pinecone) {
      console.warn('Pinecone not initialized. Returning empty results.');
      return [];
    }

    try {
      const index = this.pinecone.Index(config.pinecone.indexName);

      // Generate query embedding
      const queryEmbedding = await this.generateEmbedding(query);

      // Build filter
      let filter: Record<string, any> = {};
      if (options.documentIds && options.documentIds.length > 0) {
        filter.documentId = { $in: options.documentIds };
      }
      if (options.filter) {
        filter = { ...filter, ...options.filter };
      }

      // Perform similarity search
      const searchResults = await index.query({
        vector: queryEmbedding,
        topK: options.topK || 10,
        filter: Object.keys(filter).length > 0 ? filter : undefined,
        includeMetadata: true,
        includeValues: false,
      });

      // Format results
      const results = searchResults.matches?.map((match) => ({
        chunk: {
          id: match.id,
          documentId: match.metadata?.documentId as string,
          content: match.metadata?.content as string,
          metadata: match.metadata as any,
        },
        score: match.score || 0,
      })) || [];

      return results;
    } catch (error) {
      console.error('Error searching similar chunks:', error);
      throw new Error(`Failed to search: ${(error as Error).message}`);
    }
  }

  /**
   * Delete document vectors from store
   */
  async deleteDocumentVectors(documentId: string): Promise<void> {
    if (!this.pinecone) {
      console.warn('Pinecone not initialized. Skipping vector deletion.');
      return;
    }

    try {
      const index = this.pinecone.Index(config.pinecone.indexName);

      // Find all vectors for this document
      const filter = { documentId };
      
      // Note: Pinecone doesn't support delete by filter directly in all plans
      // We need to query first, then delete by IDs
      const searchResults = await index.query({
        vector: Array(1536).fill(0),
        topK: 10000,
        filter,
        includeMetadata: false,
      });

      if (searchResults.matches && searchResults.matches.length > 0) {
        const idsToDelete = searchResults.matches.map((m) => m.id);
        
        // Delete in batches
        const batchSize = 100;
        for (let i = 0; i < idsToDelete.length; i += batchSize) {
          const batch = idsToDelete.slice(i, i + batchSize);
          await index.deleteMany(batch);
        }

        console.log(`✅ Deleted ${idsToDelete.length} vectors for document ${documentId}`);
      }
    } catch (error) {
      console.error('Error deleting document vectors:', error);
      throw new Error(`Failed to delete vectors: ${(error as Error).message}`);
    }
  }

  /**
   * Get statistics about the vector store
   */
  async getStats(): Promise<{ totalVectors: number; documentCount: number }> {
    if (!this.pinecone) {
      return { totalVectors: 0, documentCount: 0 };
    }

    try {
      const index = this.pinecone.Index(config.pinecone.indexName);
      const stats = await index.describeIndexStats();

      return {
        totalVectors: stats.totalRecordCount || 0,
        documentCount: stats.namespaces ? Object.keys(stats.namespaces).length : 0,
      };
    } catch (error) {
      console.error('Error getting vector store stats:', error);
      return { totalVectors: 0, documentCount: 0 };
    }
  }
}

// Singleton instance
export const vectorStore = new VectorStoreService();
