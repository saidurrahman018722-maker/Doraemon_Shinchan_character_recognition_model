import { Router, Request, Response } from 'express';
import multer from 'multer';
import FormData from 'form-data';
import axios from 'axios';
import { PrismaClient } from '@prisma/client';

const router = Router();
const prisma = new PrismaClient();

const upload = multer({
  storage: multer.memoryStorage(),
  limits: {
    fileSize: 10 * 1024 * 1024, // 10 MB limit
  },
  fileFilter: (req, file, cb) => {
    if (file.mimetype.startsWith('image/')) {
      cb(null, true);
    } else {
      cb(new Error('Only image files are allowed!'));
    }
  },
});

router.post('/upload', upload.single('image'), async (req: Request, res: Response): Promise<void> => {
  try {
    if (!req.file) {
      res.status(400).json({ error: 'No image uploaded' });
      return;
    }

    const file = req.file;
    const formData = new FormData();
    formData.append('file', file.buffer, {
      filename: file.originalname,
      contentType: file.mimetype,
    });

    const mlServiceUrl = process.env.ML_SERVICE_URL || 'http://localhost:8000';
    
    let mlResponse;
    try {
      mlResponse = await axios.post(`${mlServiceUrl}/predict`, formData, {
        headers: {
          ...formData.getHeaders(),
        },
        timeout: 15000,
      });
    } catch (err: any) {
      console.error('Error connecting to ML service:', err.message);
      res.status(502).json({ error: 'Failed to communicate with ML inference service', details: err.message });
      return;
    }

    const { predicted_class, display_name, series, role, confidence, top_predictions } = mlResponse.data;

    // Log prediction to database async
    try {
      await prisma.predictionLog.create({
        data: {
          predictedCharacter: predicted_class,
          confidence: confidence || 0.0,
        },
      });
    } catch (dbErr) {
      console.warn('Failed to log prediction to DB:', dbErr);
    }

    res.json({
      message: 'Prediction successful',
      predictedClass: predicted_class,
      displayName: display_name,
      series: series,
      role: role,
      confidence: confidence,
      topPredictions: top_predictions || [],
    });
  } catch (error: any) {
    console.error('Error during image upload:', error);
    res.status(500).json({ error: 'Internal server error', details: error.message });
  }
});

export default router;
