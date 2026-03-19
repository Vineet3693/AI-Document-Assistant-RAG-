export interface Document {
  id: string;
  name: string;
  originalName: string;
  mimeType: string;
  size: number;
  path: string;
  status: 'processing' | 'ready' | 'failed';
  uploadedAt: Date;
  expiresAt?: Date;
  tags: string[];
  category?: string;
  version: number;
  accessLevel: 'public' | 'private' | 'team';
  teamIds?: string[];
  userId: string;
  metadata: DocumentMetadata;
  embeddings?: {
    indexed: boolean;
    vectorIds?: string[];
    chunkCount: number;
  };
}

export interface DocumentMetadata {
  pageCount?: number;
  wordCount?: number;
  characterCount?: number;
  language?: string;
  author?: string;
  createdDate?: Date;
  modifiedDate?: Date;
  summary?: string;
  keyPoints?: string[];
}

export interface DocumentChunk {
  id: string;
  documentId: string;
  content: string;
  metadata: ChunkMetadata;
  embedding?: number[];
}

export interface ChunkMetadata {
  chunkIndex: number;
  pageNumber?: number;
  startOffset?: number;
  endOffset?: number;
  section?: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  documents?: string[];
  citations?: Citation[];
  confidence?: number;
  mode?: ChatMode;
}

export interface Citation {
  documentId: string;
  documentName: string;
  pageNumber?: number;
  section?: string;
  quote: string;
  confidence: number;
}

export type ChatMode = 
  | 'standard'
  | 'research'
  | 'legal'
  | 'financial'
  | 'summary';

export interface QueryRequest {
  question: string;
  documentIds?: string[];
  mode?: ChatMode;
  industry?: IndustryMode;
  language?: string;
  maxResults?: number;
}

export interface QueryResponse {
  answer: string;
  citations: Citation[];
  confidence: 'high' | 'medium' | 'low';
  confidenceScore: number;
  reasoning: string;
  sources: SourceSummary[];
  followUpQuestions?: string[];
}

export interface SourceSummary {
  documentId: string;
  documentName: string;
  contribution: string;
  relevanceScore: number;
}

export interface SummaryRequest {
  documentId: string;
  summaryType: 'one-line' | 'executive' | 'detailed' | 'bullet-points';
  industry?: IndustryMode;
}

export interface SummaryResponse {
  oneLineSummary?: string;
  executiveSummary?: string;
  detailedSummary?: string;
  bulletPoints?: string[];
  keyData?: KeyData;
  actionItems?: string[];
  risks?: string[];
}

export interface KeyData {
  numbers: string[];
  dates: string[];
  people: string[];
  companies: string[];
}

export interface ComparisonRequest {
  documentId1: string;
  documentId2: string;
  comparisonType: 'general' | 'legal' | 'financial';
}

export interface ComparisonResponse {
  similarities: string[];
  differences: Difference[];
  criticalDifferences: string[];
  minorDifferences: string[];
  recommendation: string;
  overview: DocumentOverview[];
}

export interface Difference {
  topic: string;
  document1Position: string;
  document2Position: string;
  severity: 'critical' | 'major' | 'minor';
}

export interface DocumentOverview {
  mainTopic: string;
  date?: string;
  keyAmount?: string;
  keyPerson?: string;
}

export interface ExtractionRequest {
  documentId: string;
  extractionType: 'entities' | 'financial' | 'legal' | 'contacts' | 'all';
}

export interface ExtractionResponse {
  entities: {
    people: string[];
    organizations: string[];
    dates: string[];
    locations: string[];
  };
  financial?: {
    amounts: string[];
    currencies: string[];
    metrics: Record<string, string>;
  };
  legal?: {
    clauses: string[];
    parties: string[];
    jurisdiction?: string;
  };
  contacts?: {
    emails: string[];
    phones: string[];
    addresses: string[];
  };
}

export type IndustryMode = 'legal' | 'finance' | 'healthcare' | 'education' | 'hr' | 'research';

export interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'editor' | 'viewer';
  teamIds: string[];
  createdAt: Date;
  lastLoginAt?: Date;
  preferences: UserPreferences;
}

export interface UserPreferences {
  defaultIndustry: IndustryMode;
  defaultMode: ChatMode;
  language: string;
  notifications: boolean;
}

export interface Team {
  id: string;
  name: string;
  description?: string;
  memberIds: string[];
  adminIds: string[];
  documentIds: string[];
  createdAt: Date;
}

export interface Analytics {
  totalDocuments: number;
  totalQueries: number;
  totalUsers: number;
  popularQuestions: QuestionStat[];
  popularDocuments: DocumentStat[];
  usageByDay: UsageStat[];
  tokenUsage: TokenUsage;
}

export interface QuestionStat {
  question: string;
  count: number;
}

export interface DocumentStat {
  documentId: string;
  documentName: string;
  accessCount: number;
}

export interface UsageStat {
  date: string;
  queries: number;
  uploads: number;
  users: number;
}

export interface TokenUsage {
  totalTokens: number;
  promptTokens: number;
  completionTokens: number;
  costUSD: number;
}

export interface APIError {
  code: string;
  message: string;
  details?: any;
}
