import { DocumentChunk, Document } from '../types';
import { config } from '../config';
import { RecursiveCharacterTextSplitter } from '@langchain/textsplitters';
import pdfParse from 'pdf-parse';
import mammoth from 'mammoth';
import fs from 'fs/promises';
import path from 'path';

/**
 * Document Processing Service
 * Handles parsing, chunking, and text extraction from various file formats
 */
export class DocumentProcessor {
  private textSplitter: RecursiveCharacterTextSplitter;

  constructor() {
    this.textSplitter = new RecursiveCharacterTextSplitter({
      chunkSize: config.document.chunkSize,
      chunkOverlap: config.document.chunkOverlap,
      lengthFunction: (text) => text.length,
      separators: ['\n\n', '\n', '. ', ' ', ''],
    });
  }

  /**
   * Extract text from uploaded file based on MIME type
   */
  async extractText(filePath: string, mimeType: string): Promise<{ text: string; metadata: any }> {
    try {
      const fileBuffer = await fs.readFile(filePath);

      switch (mimeType) {
        case 'application/pdf':
          return this.extractFromPDF(fileBuffer);
        case 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        case 'application/msword':
          return this.extractFromWord(fileBuffer);
        case 'text/plain':
          return this.extractFromText(fileBuffer);
        case 'text/csv':
          return this.extractFromCSV(fileBuffer);
        default:
          throw new Error(`Unsupported file type: ${mimeType}`);
      }
    } catch (error) {
      console.error('Error extracting text from file:', error);
      throw new Error(`Failed to extract text: ${(error as Error).message}`);
    }
  }

  /**
   * Extract text from PDF
   */
  private async extractFromPDF(buffer: Buffer): Promise<{ text: string; metadata: any }> {
    try {
      const data = await pdfParse(buffer);
      
      return {
        text: data.text,
        metadata: {
          pageCount: data.numpages,
          info: data.info,
          version: data.version,
        },
      };
    } catch (error) {
      throw new Error(`PDF parsing failed: ${(error as Error).message}`);
    }
  }

  /**
   * Extract text from Word document
   */
  private async extractFromWord(buffer: Buffer): Promise<{ text: string; metadata: any }> {
    try {
      const result = await mammoth.extractRawText({ buffer });
      
      return {
        text: result.value,
        metadata: {
          messages: result.messages,
        },
      };
    } catch (error) {
      throw new Error(`Word document parsing failed: ${(error as Error).message}`);
    }
  }

  /**
   * Extract text from plain text file
   */
  private async extractFromText(buffer: Buffer): Promise<{ text: string; metadata: any }> {
    return {
      text: buffer.toString('utf-8'),
      metadata: {},
    };
  }

  /**
   * Extract text from CSV file
   */
  private async extractFromCSV(buffer: Buffer): Promise<{ text: string; metadata: any }> {
    const text = buffer.toString('utf-8');
    
    // Basic CSV parsing - count rows and columns
    const lines = text.split('\n');
    const columns = lines[0]?.split(',').length || 0;
    
    return {
      text: text,
      metadata: {
        rowCount: lines.length,
        columnCount: columns,
      },
    };
  }

  /**
   * Chunk document text into smaller pieces for embedding
   */
  async chunkText(
    text: string,
    documentId: string,
    metadata?: Record<string, any>
  ): Promise<DocumentChunk[]> {
    try {
      const splits = await this.textSplitter.splitText(text);
      
      const chunks: DocumentChunk[] = splits.map((content, index) => ({
        id: `${documentId}-chunk-${index}`,
        documentId,
        content,
        metadata: {
          chunkIndex: index,
          totalChunks: splits.length,
          ...metadata,
        },
      }));

      return chunks;
    } catch (error) {
      console.error('Error chunking text:', error);
      throw new Error(`Text chunking failed: ${(error as Error).message}`);
    }
  }

  /**
   * Process document: extract text and create chunks
   */
  async processDocument(
    document: Document,
    filePath: string
  ): Promise<{ chunks: DocumentChunk[]; metadata: any }> {
    try {
      // Extract text from file
      const { text, metadata: extractionMetadata } = await this.extractText(
        filePath,
        document.mimeType
      );

      // Update document metadata
      const wordCount = text.split(/\s+/).length;
      const characterCount = text.length;

      const combinedMetadata = {
        ...extractionMetadata,
        wordCount,
        characterCount,
        language: this.detectLanguage(text),
      };

      // Chunk the text
      const chunks = await this.chunkText(text, document.id, {
        originalName: document.originalName,
        uploadDate: document.uploadedAt.toISOString(),
      });

      return {
        chunks,
        metadata: combinedMetadata,
      };
    } catch (error) {
      console.error('Error processing document:', error);
      throw error;
    }
  }

  /**
   * Simple language detection based on common words
   */
  private detectLanguage(text: string): string {
    const sample = text.toLowerCase().slice(0, 500);
    
    const languageIndicators: Record<string, string[]> = {
      en: ['the', 'and', 'is', 'are', 'was', 'were', 'have', 'has'],
      es: ['el', 'la', 'los', 'las', 'de', 'que', 'en', 'es'],
      fr: ['le', 'la', 'les', 'de', 'et', 'est', 'en', 'que'],
      de: ['der', 'die', 'das', 'und', 'ist', 'ein', 'eine'],
      it: ['il', 'la', 'i', 'le', 'di', 'che', 'e', 'del'],
      pt: ['o', 'a', 'os', 'as', 'de', 'que', 'e', 'do'],
    };

    let maxCount = 0;
    let detectedLanguage = 'en';

    Object.entries(languageIndicators).forEach(([lang, words]) => {
      const count = words.reduce((acc, word) => {
        const regex = new RegExp(`\\b${word}\\b`, 'g');
        return acc + ((sample.match(regex) || []).length);
      }, 0);

      if (count > maxCount) {
        maxCount = count;
        detectedLanguage = lang;
      }
    });

    return detectedLanguage;
  }

  /**
   * Count tokens in text (approximate)
   */
  countTokens(text: string): number {
    // Rough approximation: 1 token ≈ 4 characters in English
    return Math.ceil(text.length / 4);
  }

  /**
   * Truncate text to fit within token limit
   */
  truncateToTokenLimit(text: string, maxTokens: number): string {
    const maxChars = maxTokens * 4;
    
    if (text.length <= maxChars) {
      return text;
    }

    return text.slice(0, maxChars - 3) + '...';
  }
}

// Singleton instance
export const documentProcessor = new DocumentProcessor();
