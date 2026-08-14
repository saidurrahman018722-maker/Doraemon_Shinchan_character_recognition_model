import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import uploadRoute from './routes/upload';
import characterRoute from './routes/characters';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ limit: '10mb', extended: true }));

app.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: 'doraemon-shinchan-backend' });
});

app.use('/api', uploadRoute);
app.use('/api', characterRoute);

app.listen(PORT, () => {
  console.log(`Doraemon & Shin-chan Backend API running on port ${PORT}`);
});
