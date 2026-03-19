import { ChatOpenAI } from '@langchain/openai';
import { config } from '../config';
import { QueryResponse, SummaryResponse, ComparisonResponse, ExtractionResponse, IndustryMode, ChatMode } from '../types';
import { getPrompt } from '../prompts';

/**
 * AI Service
 * Handles all LLM interactions for Q&A, summarization, and analysis
 */
export class AIService {
  private llm: ChatOpenAI;

  constructor() {
    this.llm = new ChatOpenAI({
      apiKey: config.openai.apiKey,
      model: config.openai.model,
      temperature: config.openai.temperature,
      maxTokens: config.openai.maxTokens,
    });
  }

  /**
   * Answer question using RAG with document context
   */
  async answerQuestion(
    question: string,
    context: string,
    options: {
      documentNames?: string[];
      language?: string;
      userName?: string;
      industry?: IndustryMode;
      mode?: ChatMode;
    } = {}
  ): Promise<QueryResponse> {
    try {
      const prompt = getPrompt('qa', {
        context,
        question,
        doc_names: options.documentNames?.join(', ') || 'No documents',
        language: options.language || 'English',
        user_name: options.userName || 'User',
        industry: options.industry || 'general',
        mode: options.mode || 'standard',
      }, options.industry);

      const response = await this.llm.invoke(prompt);
      const content = response.content as string;

      // Parse response to extract structured data
      const confidence = this.extractConfidence(content);
      const citations = this.extractCitations(content, options.documentNames || []);

      return {
        answer: this.extractAnswer(content),
        citations,
        confidence: confidence.level,
        confidenceScore: confidence.score,
        reasoning: this.extractReasoning(content),
        sources: this.extractSources(content),
        followUpQuestions: this.extractFollowUpQuestions(content),
      };
    } catch (error) {
      console.error('Error answering question:', error);
      throw new Error(`Failed to generate answer: ${(error as Error).message}`);
    }
  }

  /**
   * Generate summary of a document
   */
  async summarizeDocument(
    documentText: string,
    options: {
      documentName: string;
      documentType?: string;
      industry?: IndustryMode;
      summaryType?: 'one-line' | 'executive' | 'detailed' | 'bullet-points';
    }
  ): Promise<SummaryResponse> {
    try {
      // Truncate if too long (keep within token limits)
      const truncatedText = documentText.slice(0, 50000);

      const prompt = getPrompt('summary', {
        document_text: truncatedText,
        document_name: options.documentName,
        document_type: options.documentType || 'Document',
        industry: options.industry || 'general',
      }, options.industry);

      const response = await this.llm.invoke(prompt);
      const content = response.content as string;

      return this.parseSummaryResponse(content);
    } catch (error) {
      console.error('Error summarizing document:', error);
      throw new Error(`Failed to summarize: ${(error as Error).message}`);
    }
  }

  /**
   * Compare two documents
   */
  async compareDocuments(
    doc1Text: string,
    doc2Text: string,
    options: {
      doc1Name: string;
      doc2Name: string;
      comparisonType?: 'general' | 'legal' | 'financial';
    }
  ): Promise<ComparisonResponse> {
    try {
      // Truncate if needed
      const maxPerDoc = 25000;
      const truncatedDoc1 = doc1Text.slice(0, maxPerDoc);
      const truncatedDoc2 = doc2Text.slice(0, maxPerDoc);

      const prompt = getPrompt('comparison', {
        doc1_text: truncatedDoc1,
        doc2_text: truncatedDoc2,
        doc1_name: options.doc1Name,
        doc2_name: options.doc2Name,
      });

      const response = await this.llm.invoke(prompt);
      const content = response.content as string;

      return this.parseComparisonResponse(content);
    } catch (error) {
      console.error('Error comparing documents:', error);
      throw new Error(`Failed to compare: ${(error as Error).message}`);
    }
  }

  /**
   * Extract key information from document
   */
  async extractInformation(
    documentText: string,
    extractionType: 'entities' | 'financial' | 'legal' | 'contacts' | 'all'
  ): Promise<ExtractionResponse> {
    try {
      const prompt = `Extract the following information from the text below.
Return ONLY valid JSON in this exact format:

${this.getExtractionFormat(extractionType)}

TEXT:
${documentText.slice(0, 30000)}`;

      const response = await this.llm.invoke(prompt);
      const content = response.content as string;

      // Try to parse as JSON
      try {
        const jsonMatch = content.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
          return JSON.parse(jsonMatch[0]);
        }
      } catch (e) {
        // Fallback to manual parsing
      }

      return this.parseExtractionResponse(content, extractionType);
    } catch (error) {
      console.error('Error extracting information:', error);
      throw new Error(`Failed to extract: ${(error as Error).message}`);
    }
  }

  /**
   * Get extraction format based on type
   */
  private getExtractionFormat(type: string): string {
    const formats: Record<string, string> = {
      entities: `{
  "entities": {
    "people": ["person1", "person2"],
    "organizations": ["org1", "org2"],
    "dates": ["date1", "date2"],
    "locations": ["location1", "location2"]
  }
}`,
      financial: `{
  "financial": {
    "amounts": ["$1000", "$5000"],
    "currencies": ["USD", "EUR"],
    "metrics": {"revenue": "$X", "profit": "$Y"}
  }
}`,
      legal: `{
  "legal": {
    "clauses": ["clause1", "clause2"],
    "parties": ["party1", "party2"],
    "jurisdiction": "State/Country"
  }
}`,
      contacts: `{
  "contacts": {
    "emails": ["email@example.com"],
    "phones": ["+1-xxx-xxx-xxxx"],
    "addresses": ["address1"]
  }
}`,
      all: `{
  "entities": {
    "people": [],
    "organizations": [],
    "dates": [],
    "locations": []
  },
  "financial": {
    "amounts": [],
    "currencies": [],
    "metrics": {}
  },
  "legal": {
    "clauses": [],
    "parties": [],
    "jurisdiction": ""
  },
  "contacts": {
    "emails": [],
    "phones": [],
    "addresses": []
  }
}`,
    };

    return formats[type] || formats.all;
  }

  /**
   * Helper: Extract confidence level from response
   */
  private extractConfidence(content: string): { level: 'high' | 'medium' | 'low'; score: number } {
    const lower = content.toLowerCase();
    
    if (lower.includes('confidence: high') || lower.includes('🔍 confidence: high')) {
      return { level: 'high', score: 85 };
    } else if (lower.includes('confidence: medium') || lower.includes('🔍 confidence: medium')) {
      return { level: 'medium', score: 60 };
    } else if (lower.includes('confidence: low') || lower.includes('🔍 confidence: low')) {
      return { level: 'low', score: 35 };
    }

    // Default based on content certainty
    if (lower.includes('definitely') || lower.includes('certainly') || lower.includes('clearly')) {
      return { level: 'high', score: 80 };
    } else if (lower.includes('probably') || lower.includes('likely') || lower.includes('appears')) {
      return { level: 'medium', score: 55 };
    }

    return { level: 'medium', score: 65 };
  }

  /**
   * Helper: Extract citations from response
   */
  private extractCitations(content: string, documentNames: string[]): Array<{
    documentId: string;
    documentName: string;
    pageNumber?: number;
    section?: string;
    quote: string;
    confidence: number;
  }> {
    const citations = [];
    
    // Look for citation patterns
    const citationRegex = /📄.*?Document:\s*([^\n]+).*?(?:Page|Section):\s*([^\n]+).*?Quote:\s*"([^"]+)"/gs;
    let match;

    while ((match = citationRegex.exec(content)) !== null) {
      citations.push({
        documentId: match[1].trim(),
        documentName: match[1].trim(),
        pageNumber: parseInt(match[2]) || undefined,
        quote: match[3]?.trim() || '',
        confidence: 0.9,
      });
    }

    return citations.length > 0 ? citations : [];
  }

  /**
   * Helper: Extract main answer from response
   */
  private extractAnswer(content: string): string {
    const answerMatch = content.match(/✅ Direct Answer:([\s\S]*?)(?=📌|📄|🔍|$)/);
    if (answerMatch) {
      return answerMatch[1].trim();
    }

    // Fallback: return first paragraph
    const paragraphs = content.split('\n\n');
    return paragraphs[0]?.trim() || content;
  }

  /**
   * Helper: Extract reasoning from response
   */
  private extractReasoning(content: string): string {
    const reasonMatch = content.match(/Reason:\s*([^\n]+)/i);
    if (reasonMatch) {
      return reasonMatch[1].trim();
    }

    return 'Based on document analysis';
  }

  /**
   * Helper: Extract sources from response
   */
  private extractSources(content: string): Array<{
    documentId: string;
    documentName: string;
    contribution: string;
    relevanceScore: number;
  }> {
    const sources = [];
    const sourceLines = content.split('\n').filter(line => 
      line.includes('Document:') || line.includes('📄')
    );

    sourceLines.forEach((line, idx) => {
      const docMatch = line.match(/Document:\s*([^\n]+)/);
      if (docMatch) {
        sources.push({
          documentId: docMatch[1].trim(),
          documentName: docMatch[1].trim(),
          contribution: 'Referenced in answer',
          relevanceScore: 1 - (idx * 0.1),
        });
      }
    });

    return sources;
  }

  /**
   * Helper: Extract follow-up questions
   */
  private extractFollowUpQuestions(content: string): string[] {
    const questions: string[] = [];
    const questionMatches = content.match(/(?:Would you like to know|Follow-up|Related):\s*([^\n]+)/gi);
    
    if (questionMatches) {
      questionMatches.forEach(q => {
        const cleanQ = q.replace(/(?:Would you like to know|Follow-up|Related):\s*/gi, '').trim();
        if (cleanQ) questions.push(cleanQ);
      });
    }

    return questions.slice(0, 3);
  }

  /**
   * Parse summary response
   */
  private parseSummaryResponse(content: string): SummaryResponse {
    const response: SummaryResponse = {};

    // Extract sections using regex
    const oneLineMatch = content.match(/### 🎯 ONE LINE SUMMARY:([\s\S]*?)(?=###|$)/);
    const executiveMatch = content.match(/### 📋 EXECUTIVE SUMMARY:([\s\S]*?)(?=###|$)/);
    const keyPointsMatch = content.match(/### 🔑 5 KEY POINTS:([\s\S]*?)(?=###|$)/);
    const dataMatch = content.match(/### 📊 IMPORTANT DATA FOUND:([\s\S]*?)(?=###|$)/);
    const actionMatch = content.match(/### ⚡ ACTION ITEMS:([\s\S]*?)(?=###|$)/);
    const risksMatch = content.match(/### ⚠️ RISKS OR CONCERNS:([\s\S]*?)(?=###|$)/);

    if (oneLineMatch) response.oneLineSummary = oneLineMatch[1].trim();
    if (executiveMatch) response.executiveSummary = executiveMatch[1].trim();
    
    if (keyPointsMatch) {
      response.bulletPoints = keyPointsMatch[1]
        .split('\n')
        .filter(line => line.match(/^\d+\./))
        .map(line => line.replace(/^\d+\.\s*/, '').trim());
    }

    if (dataMatch) {
      response.keyData = {
        numbers: this.extractList(dataMatch[1], 'Numbers'),
        dates: this.extractList(dataMatch[1], 'Dates'),
        people: this.extractList(dataMatch[1], 'People'),
        companies: this.extractList(dataMatch[1], 'Companies'),
      };
    }

    if (actionMatch) {
      response.actionItems = this.extractBulletPoints(actionMatch[1]);
    }

    if (risksMatch) {
      response.risks = this.extractBulletPoints(risksMatch[1]);
    }

    return response;
  }

  /**
   * Parse comparison response
   */
  private parseComparisonResponse(content: string): ComparisonResponse {
    return {
      similarities: this.extractBulletPointsFromSection(content, 'WHAT THEY AGREE ON'),
      differences: [],
      criticalDifferences: this.extractBulletPointsFromSection(content, 'CRITICAL DIFFERENCES'),
      minorDifferences: this.extractBulletPointsFromSection(content, 'MINOR DIFFERENCES'),
      recommendation: this.extractSection(content, 'ANALYST RECOMMENDATION'),
      overview: [],
    };
  }

  /**
   * Parse extraction response
   */
  private parseExtractionResponse(content: string, type: string): ExtractionResponse {
    // Basic fallback parsing
    return {
      entities: {
        people: [],
        organizations: [],
        dates: [],
        locations: [],
      },
    };
  }

  /**
   * Helper: Extract list from text
   */
  private extractList(text: string, label: string): string[] {
    const regex = new RegExp(`${label}:\\s*([^\\n]+)`, 'i');
    const match = text.match(regex);
    if (match) {
      return match[1].split(',').map(s => s.trim()).filter(Boolean);
    }
    return [];
  }

  /**
   * Helper: Extract bullet points
   */
  private extractBulletPoints(text: string): string[] {
    return text
      .split('\n')
      .filter(line => line.trim().startsWith('•') || line.trim().startsWith('-'))
      .map(line => line.replace(/^[•-]\s*/, '').trim())
      .filter(Boolean);
  }

  /**
   * Helper: Extract bullet points from section
   */
  private extractBulletPointsFromSection(content: string, sectionName: string): string[] {
    const sectionRegex = new RegExp(`### .*${sectionName}.*:([\\s\\S]*?)(?=###|$)`, 'i');
    const match = content.match(sectionRegex);
    if (match) {
      return this.extractBulletPoints(match[1]);
    }
    return [];
  }

  /**
   * Helper: Extract section content
   */
  private extractSection(content: string, sectionName: string): string {
    const sectionRegex = new RegExp(`### .*${sectionName}.*:([\\s\\S]*?)(?=###|$)`, 'i');
    const match = content.match(sectionRegex);
    return match ? match[1].trim() : '';
  }
}

// Singleton instance
export const aiService = new AIService();
