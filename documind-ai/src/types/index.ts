// Document Types
export interface Document {
  id: string;
  name: string;
  type: 'pdf' | 'docx' | 'txt' | 'xlsx' | 'pptx' | 'csv';
  size: number;
  uploadDate: Date;
  status: 'uploading' | 'processing' | 'ready' | 'error';
  tags: string[];
  category?: string;
  version: number;
  accessLevel: 'public' | 'private' | 'team';
  teamIds?: string[];
  expiryDate?: Date;
  pageCount?: number;
  summary?: string;
}

// Chat & Q&A Types
export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  sources?: Citation[];
  confidence?: number;
  followUpQuestions?: string[];
}

export interface Citation {
  documentId: string;
  documentName: string;
  pageNumber?: number;
  section?: string;
  quote: string;
}

export interface ChatSession {
  id: string;
  title: string;
  messages: Message[];
  documentIds: string[];
  createdAt: Date;
  updatedAt: Date;
  mode: ChatMode;
}

export type ChatMode = 
  | 'standard'
  | 'research'
  | 'legal'
  | 'financial'
  | 'summary'
  | 'healthcare'
  | 'education';

// Analysis Types
export interface DocumentSummary {
  oneLine: string;
  executive: string;
  keyPoints: string[];
  importantData: {
    numbers: string[];
    dates: string[];
    people: string[];
    companies: string[];
  };
  actionItems: string[];
  risks: string[];
  bottomLine: string;
}

export interface ExtractedInfo {
  names: string[];
  organizations: string[];
  dates: string[];
  financialAmounts: string[];
  actionItems: string[];
  legalClauses: string[];
  contactInfo: string[];
}

export interface DocumentComparison {
  doc1Name: string;
  doc2Name: string;
  similarities: string[];
  differences: Array<{
    topic: string;
    doc1Position: string;
    doc2Position: string;
  }>;
  criticalDifferences: string[];
  minorDifferences: string[];
  recommendation: string;
}

// Industry-Specific Types
export interface LegalAnalysis {
  contractType: string;
  parties: string[];
  effectiveDate?: Date;
  expiryDate?: Date;
  value?: string;
  jurisdiction?: string;
  keyClauses: Record<string, string>;
  highRiskClauses: RiskClause[];
  mediumRiskClauses: RiskClause[];
  favorableClauses: string[];
  missingClauses: Array<{ name: string; reason: string }>;
  riskScore: number;
  riskLevel: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  recommendedSteps: string[];
}

export interface RiskClause {
  name: string;
  quote: string;
  reason: string;
  recommendation: string;
}

export interface FinancialMetrics {
  revenue?: string;
  netProfit?: string;
  profitMargin?: string;
  totalAssets?: string;
  totalLiabilities?: string;
  cashEquivalents?: string;
  eps?: string;
}

export interface FinancialAnalysis {
  company: string;
  period: string;
  reportType: string;
  metrics: FinancialMetrics;
  strengths: string[];
  concerns: string[];
  riskFactors: string[];
  managementGuidance?: string;
  keyInsights: string[];
}

export interface ResumeEvaluation {
  candidateName?: string;
  currentRole?: string;
  experienceYears: number;
  education: string;
  skillsMatch: Array<{
    skill: string;
    found: boolean;
    proficiency: string;
  }>;
  strengths: string[];
  gaps: string[];
  scores: {
    skills: number;
    experience: number;
    education: number;
    overall: number;
  };
  recommendation: 'STRONG YES' | 'YES' | 'MAYBE' | 'NO';
  interviewQuestions: string[];
}

// User & Team Types
export interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'editor' | 'viewer';
  avatar?: string;
  createdAt: Date;
}

export interface Team {
  id: string;
  name: string;
  members: User[];
  documents: string[];
  createdAt: Date;
}

export interface Workspace {
  id: string;
  name: string;
  teams: Team[];
  documents: string[];
  settings: WorkspaceSettings;
}

export interface WorkspaceSettings {
  defaultAccessLevel: 'public' | 'private' | 'team';
  autoDeleteDays?: number;
  complianceMode?: 'GDPR' | 'HIPAA' | 'SOC2' | 'none';
}

// Analytics Types
export interface UsageStats {
  documentsUploaded: number;
  questionsAsked: number;
  tokensUsed: number;
  activeUsers: number;
  popularDocuments: Array<{ id: string; name: string; views: number }>;
  popularQuestions: Array<{ question: string; count: number }>;
  costBreakdown: {
    embedding: number;
    llm: number;
    storage: number;
  };
}

// API Response Types
export interface APIResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface UploadProgress {
  fileName: string;
  progress: number;
  status: 'pending' | 'uploading' | 'processing' | 'complete' | 'error';
  error?: string;
}

// Settings Types
export interface AppSettings {
  theme: 'light' | 'dark' | 'system';
  language: string;
  defaultChatMode: ChatMode;
  notificationsEnabled: boolean;
  autoSaveChats: boolean;
}
