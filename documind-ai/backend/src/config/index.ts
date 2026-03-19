import dotenv from 'dotenv';

dotenv.config();

export const config = {
  // OpenAI Configuration
  openai: {
    apiKey: process.env.OPENAI_API_KEY || '',
    model: process.env.OPENAI_MODEL || 'gpt-4o',
    embeddingModel: process.env.OPENAI_EMBEDDING_MODEL || 'text-embedding-3-large',
    maxTokens: parseInt(process.env.OPENAI_MAX_TOKENS || '4096'),
    temperature: parseFloat(process.env.OPENAI_TEMPERATURE || '0.1'),
  },

  // Pinecone Configuration
  pinecone: {
    apiKey: process.env.PINECONE_API_KEY || '',
    environment: process.env.PINECONE_ENVIRONMENT || 'us-west1-gcp',
    indexName: process.env.PINECONE_INDEX_NAME || 'documind-index',
  },

  // Server Configuration
  server: {
    port: parseInt(process.env.PORT || '3001'),
    nodeEnv: process.env.NODE_ENV || 'development',
  },

  // JWT Configuration
  jwt: {
    secret: process.env.JWT_SECRET || 'dev-secret-change-in-production',
    expiresIn: process.env.JWT_EXPIRES_IN || '7d',
  },

  // Rate Limiting
  rateLimit: {
    windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS || '900000'),
    maxRequests: parseInt(process.env.RATE_LIMIT_MAX_REQUESTS || '100'),
  },

  // File Upload Configuration
  upload: {
    maxSizeMB: parseInt(process.env.MAX_FILE_SIZE_MB || '50'),
    uploadDir: process.env.UPLOAD_DIR || './uploads',
    allowedMimeTypes: [
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/msword',
      'text/plain',
      'application/vnd.ms-excel',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'text/csv',
      'application/vnd.ms-powerpoint',
      'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    ],
  },

  // Logging Configuration
  logging: {
    level: process.env.LOG_LEVEL || 'info',
    dir: process.env.LOG_DIR || './logs',
  },

  // CORS Configuration
  cors: {
    origins: (process.env.CORS_ORIGINS || 'http://localhost:3000,http://localhost:5173').split(','),
  },

  // Document Configuration
  document: {
    expiryDays: parseInt(process.env.DOCUMENT_EXPIRY_DAYS || '0'),
    chunkSize: parseInt(process.env.CHUNK_SIZE || '1000'),
    chunkOverlap: parseInt(process.env.CHUNK_OVERLAP || '200'),
  },

  // Analytics
  analytics: {
    enabled: process.env.ENABLE_ANALYTICS === 'true',
  },

  // Industry Modes
  industryModes: ['legal', 'finance', 'healthcare', 'education', 'hr', 'research'] as const,
};

// Validate required environment variables
const requiredEnvVars = ['OPENAI_API_KEY'];
const missingEnvVars = requiredEnvVars.filter((envVar) => !process.env[envVar]);

if (missingEnvVars.length > 0 && config.server.nodeEnv !== 'test') {
  console.warn(`⚠️  Warning: Missing required environment variables: ${missingEnvVars.join(', ')}`);
  console.warn('Please copy .env.example to .env and configure the required variables.');
}

export type Config = typeof config;
export type IndustryMode = typeof config.industryModes[number];
