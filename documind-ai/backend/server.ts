import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';
import path from 'path';
import { config } from './config';
import documentRoutes from './routes/documents';
import { vectorStore } from './services/vectorStore';

const app = express();

// Security middleware
app.use(helmet());

// CORS configuration
app.use(cors({
  origin: config.cors.origins,
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-User-ID', 'X-User-Name'],
}));

// Rate limiting
const limiter = rateLimit({
  windowMs: config.rateLimit.windowMs,
  max: config.rateLimit.maxRequests,
  message: {
    success: false,
    error: 'Too many requests',
    message: 'Please try again later',
  },
});
app.use('/api/', limiter);

// Body parsing middleware
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Request logging middleware
app.use((req, res, next) => {
  const start = Date.now();
  res.on('finish', () => {
    const duration = Date.now() - start;
    console.log(`${req.method} ${req.path} ${res.statusCode} - ${duration}ms`);
  });
  next();
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    version: '3.0.0',
    environment: config.server.nodeEnv,
  });
});

// API routes
app.use('/api/documents', documentRoutes);

// API documentation endpoint
app.get('/api', (req, res) => {
  res.json({
    name: 'DocuMind AI API',
    version: '3.0.0',
    description: 'Enterprise AI Document Assistant with RAG capabilities',
    endpoints: {
      documents: {
        'GET /api/documents': 'Get all documents for current user',
        'POST /api/documents/upload': 'Upload a new document (multipart/form-data)',
        'GET /api/documents/:id': 'Get document by ID',
        'PUT /api/documents/:id': 'Update document metadata',
        'DELETE /api/documents/:id': 'Delete document',
        'POST /api/documents/:id/summarize': 'Generate summary of document',
        'POST /api/documents/:id/extract': 'Extract information from document',
        'POST /api/documents/query': 'Query documents using RAG',
        'POST /api/documents/compare': 'Compare two documents',
        'GET /api/documents/stats/overview': 'Get document statistics',
      },
    },
    healthCheck: '/health',
  });
});

// Error handling middleware
app.use((err: any, req: express.Request, res: express.Response, next: express.NextFunction) => {
  console.error('Unhandled error:', err);

  // Multer errors
  if (err.code === 'LIMIT_FILE_SIZE') {
    return res.status(400).json({
      success: false,
      error: 'File too large',
      message: `Maximum file size is ${config.upload.maxSizeMB}MB`,
    });
  }

  // Default error response
  res.status(err.status || 500).json({
    success: false,
    error: err.message || 'Internal server error',
    ...(config.server.nodeEnv === 'development' && { stack: err.stack }),
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    success: false,
    error: 'Not found',
    message: `Route ${req.method} ${req.path} not found`,
  });
});

/**
 * Initialize and start server
 */
async function startServer() {
  try {
    console.log('🚀 Starting DocuMind AI Server...');
    
    // Initialize vector store
    console.log('📦 Initializing vector store...');
    await vectorStore.initialize();
    
    // Start server
    app.listen(config.server.port, () => {
      console.log(`
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║           🎉 DocuMind AI Server Started!                 ║
║                                                          ║
║   Environment : ${config.server.nodeEnv.padEnd(42)}║
║   Port        : ${String(config.server.port).padEnd(42)}║
║   API Base    : http://localhost:${String(config.server.port).padEnd(32)}║
║   Health      : http://localhost:${String(config.server.port).padEnd(32)}║
║                                                          ║
║   Ready to process documents!                            ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
      `);
    });
  } catch (error) {
    console.error('❌ Failed to start server:', error);
    process.exit(1);
  }
}

// Handle graceful shutdown
process.on('SIGTERM', () => {
  console.log('👋 SIGTERM received. Shutting down gracefully...');
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('👋 SIGINT received. Shutting down gracefully...');
  process.exit(0);
});

export default app;
startServer();
