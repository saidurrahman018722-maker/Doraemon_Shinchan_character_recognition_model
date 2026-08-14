import { Router, Request, Response } from 'express';
import { PrismaClient } from '@prisma/client';

const router = Router();
const prisma = new PrismaClient();

router.get('/characters', async (req: Request, res: Response) => {
  try {
    const characters = await prisma.character.findMany();
    res.json({ characters });
  } catch (error) {
    console.error("Error fetching characters:", error);
    res.status(500).json({ error: "Failed to fetch characters" });
  }
});

export default router;
