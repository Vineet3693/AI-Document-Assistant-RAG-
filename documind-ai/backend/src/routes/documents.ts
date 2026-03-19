import express, { Request, Response, NextFunction } from 'express';
import multer from 'multer';
import path from 'path';
import fs from 'fs/promises';
import { config } from '../config';
import { documentService } from '../services/documentService';
import { vectorStore } from '../services/vectorStore';

const router = express.Router();

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: async (req, file, cb) => {
    const uploadDir = config.upload.uploadDir;
    await fs.mkdir(uploadDir, { recursive: true });
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, `${uniqueSuffix}-${file.originalname}`);
  },
});

const fileFilter = (req: Request, file: Express.Multer.File, cb: multer.FileFilterCallback) => {
  if (config.upload.allowedMimeTypes.includes(file.mimetype)) {
    cb(null, true);
  } else {
    cb(new Error(`Unsupported file type: ${file.mimetype}`));
  }
};

const upload = multer({
  storage,
  fileFilter,
  limits: {
    fileSize: config.upload.maxSizeMB * 1024 * 1024,
  },
});

/**
 * Mock user middleware (replace with real auth in production)
 */
const mockAuthMiddleware = (req: Request, res: Response, next: NextFunction) => {
  // In production, verify JWT token here
  const userId = req.headers['x-user-id'] as string || 'user-123';
  const userName = req.headers['x-user-name'] as string || 'Demo User';
  
  (req as any).userId = userId;
  (req as any).userName = userName;
  next();
};

/**
 * GET /api/documents
 * Get all documents for current user
 */
router.get('/', mockAuthMiddleware, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).userId;
    const documents = await documentService.getUserDocuments(userId);
    
    res.json({
      success: true,
      data: documents,
      count: documents.length,
    });
  } catch (error) {
    console.error('Error fetching documents:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch documents',
      message: (error as Error).message,
    });
  }
});

/**
 * POST /api/documents/upload
 * Upload a new document
 */
router.post('/upload', mockAuthMiddleware, upload.single('file'), async (req: Request, res: Response) => {
  try {
    if (!req.file) {
      return res.status(400).json({
        success: false,
        error: 'No file uploaded',
      });
    }

    const userId = (req as any).userId;
    const tags = req.body.tags ? JSON.parse(req.body.tags) : [];
    const category = req.body.category;
    const accessLevel = req.body.accessLevel as 'public' | 'private' | 'team' || 'private';

    const document = await documentService.createDocument(
      req.file.path,
      req.file.originalname,
      req.file.mimetype,
      req.file.size,
      userId,
      {
        tags,
        category,
        accessLevel,
      }
    );

    res.status(201).json({
      success: true,
      data: document,
      message: 'Document uploaded successfully. Processing started.',
    });
  } catch (error) {
    console.error('Error uploading document:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to upload document',
      message: (error as Error).message,
    });
  }
});

/**
 * GET /api/documents/:id
 * Get document by ID
 */
router.get('/:id', mockAuthMiddleware, async (req: Request, res: Response) => {
  try {
    const document = await documentService.getDocument(req.params.id);
    
    if (!document) {
      return res.status(404).json({
        success: false,
        error: 'Document not found',
      });
    }

    res.json({
      success: true,
      data: document,
    });
  } catch (error) {
    console.error('Error fetching document:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch document',
      message: (error as Error).message,
    });
  }
});

/**
 * PUT /api/documents/:id
 * Update document metadata
 */
router.put('/:id', mockAuthMiddleware, async (req: Request, res: Response) => {
  try {
    const { tags, category, accessLevel } = req.body;
    
    const document = await documentService.updateDocument(req.params.id, {
      tags,
      category,
      accessLevel,
    });
    
    if (!document) {
      return res.status(404).json({
        success: false,
        error: 'Document not found',
      });
    }

    res.json({
      success: true,
      data: document,
      message: 'Document updated successfully',
    });
  } catch (error) {
    console.error('Error updating document:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to update document',
      message: (error as Error).message,
    });
  }
});

/**
 * DELETE /api/documents/:id
 * Delete document
 */
router.delete('/:id', mockAuthMiddleware, async (req: Request, res: Response) => {
  try {
    const deleted = await documentService.deleteDocument(req.params.id);
    
    if (!deleted) {
      return res.status(404).json({
        success: false,
        error: 'Document not found',
      });
    }

    res.json({
      success: true,
      message: 'Document deleted successfully',
    });
  } catch (error) {
    console.error('Error deleting document:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to delete document',
      message: (error as Error).message,
    });
  }
});

/**
 * POST /api/documents/:id/summarize
 * Generate summary of document
 */
router.post('/:id/summarize', mockAuthMiddleware, async (req: Request, res: Response) => {
  try {
    const { summaryType = 'executive', industry } = req.body;
    
    const summary = await documentService.summarizeDocument({
      documentId: req.params.id,
      summaryType,
      industry,
    });

    res.json({
      success: true,
      data: summary,
    });
  } catch (error) {
    console.error('Error summarizing document:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to summarize document',
      message: (error as Error).message,
    });
  }
});

/**
 * POST /api/documents/:id/extract
 * Extract information from document
 */
router.post('/:id/extract', mockAuthMiddleware, async (req: Request, res: Response) => {
  try {
    const { extractionType = 'all' } = req.body;
    
    const extracted = await documentService.extractInformation(
      req.params.id,
      extractionType
    );

    res.json({
      success: true,
      data: extracted,
    });
  } catch (error) {
    console.error('Error extracting information:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to extract information',
      message: (error as Error).message,
    });
  }
});

/**
 * POST /api/documents/query
 * Query documents using RAG
 */
router.post('/query', mockAuthMiddleware, async (req: Request, res: Response) => {
  try {
    const { question, documentIds, mode, industry, language } = req.body;
    const userId = (req as any).userId;

    if (!question) {
      return res.status(400).json({
        success: false,
        error: 'Question is required',
      });
    }

    const response = await documentService.queryDocuments(
      {
        question,
        documentIds,
        mode,
        industry,
        language,
      },
      userId
    );

    res.json({
      success: true,
      data: response,
    });
  } catch (error) {
    console.error('Error querying documents:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to query documents',
      message: (error as Error).message,
    });
  }
});

/**
 * POST /api/documents/compare
 * Compare two documents
 */
router.post('/compare', mockAuthMiddleware, async (req: Request, res: Response) => {
  try {
    const { documentId1, documentId2, comparisonType = 'general' } = req.body;

    if (!documentId1 || !documentId2) {
      return res.status(400).json({
        success: false,
        error: 'Both document IDs are required',
      });
    }

    const comparison = await documentService.compareDocuments({
      documentId1,
      documentId2,
      comparisonType,
    });

    res.json({
      success: true,
      data: comparison,
    });
  } catch (error) {
    console.error('Error comparing documents:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to compare documents',
      message: (error as Error).message,
    });
  }
});

/**
 * GET /api/documents/stats
 * Get document statistics
 */
router.get('/stats/overview', mockAuthMiddleware, async (req: Request, res: Response) => {
  try {
    const stats = await documentService.getStats();
    const vectorStats = await vectorStore.getStats();

    res.json({
      success: true,
      data: {
        ...stats,
        vectorStore: vectorStats,
      },
    });
  } catch (error) {
    console.error('Error fetching stats:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch statistics',
      message: (error as Error).message,
    });
  }
});

export default router;
