import React, { useState, useEffect, useRef } from 'react';
import { Upload, Sparkles, AlertCircle, RefreshCw, CheckCircle2, Image as ImageIcon, Info, Heart } from 'lucide-react';
import axios from 'axios';

// Use hardcoded Render API URL to bypass Vercel configuration requirements
axios.defaults.baseURL = 'https://doraemon-shinchan-character-recognition-gvn5.onrender.com';

interface TopPrediction {
  class_name: string;
  display_name: string;
  confidence: number;
}

interface PredictionResult {
  predictedClass: string;
  displayName: string;
  series: string;
  role: string;
  confidence: number;
  topPredictions: TopPrediction[];
}

interface CharacterInfo {
  key: string;
  displayName: string;
  series: string;
  role: string;
  color: string;
  bio: string;
}

export default function App() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [characters, setCharacters] = useState<CharacterInfo[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    // Fetch characters list from backend API
    axios.get('/api/characters')
      .then(res => {
        if (res.data && res.data.characters) {
          setCharacters(res.data.characters);
        }
      })
      .catch(() => {
        // Fallback default list
        setCharacters([
          { key: "doraemon", displayName: "Doraemon", series: "Doraemon", role: "Cat Robot", color: "#00a0e9", bio: "A robotic cat from the 22nd century with a 4D pocket full of gadgets." },
          { key: "nobi_nobita", displayName: "Nobita Nobi", series: "Doraemon", role: "Main Protagonist", color: "#f7b500", bio: "Lazy but kind-hearted 4th grader who relies on Doraemon's gadgets." },
          { key: "shizuka_minamoto", displayName: "Shizuka Minamoto", series: "Doraemon", role: "Friend & Future Wife", color: "#ff80ab", bio: "Sweet, intelligent girl who loves playing violin and sweet potatoes." },
          { key: "takeshi_goda_gian", displayName: "Takeshi 'Gian' Goda", series: "Doraemon", role: "Neighborhood Bully", color: "#ff6f00", bio: "Strong, quick-tempered boy who loves singing and baseball." },
          { key: "suneo_honekawa", displayName: "Suneo Honekawa", series: "Doraemon", role: "Wealthy Friend", color: "#4caf50", bio: "Rich kid who loves bragging about expensive toys." },
          { key: "dorami", displayName: "Dorami", series: "Doraemon", role: "Younger Sister", color: "#fff176", bio: "Doraemon's younger yellow sister who is smart and responsible." },
          { key: "misae_nohara", displayName: "Misae Nohara", series: "Shin-chan", role: "Mother", color: "#ab47bc", bio: "Shin-chan's hardworking mother known for her fist-twisting punishment." },
          { key: "hiroshi_nohara", displayName: "Hiroshi Nohara", series: "Shin-chan", role: "Father", color: "#0288d1", bio: "Shin-chan's salaryman father who loves beer." },
          { key: "himawari_nohara", displayName: "Himawari Nohara", series: "Shin-chan", role: "Baby Sister", color: "#ffd54f", bio: "Shin-chan's baby sister who loves shiny jewels." },
          { key: "shiro_dog", displayName: "Shiro", series: "Shin-chan", role: "Pet Dog", color: "#eceff1", bio: "Intelligent white fluffy dog who takes care of himself." },
          { key: "toru_kazama", displayName: "Toru Kazama", series: "Shin-chan", role: "Smart Friend", color: "#1e88e5", bio: "Elite, polite kindergarten classmate who secretly loves Moe-P." },
          { key: "nene_sakurada", displayName: "Nene Sakurada", series: "Shin-chan", role: "Fiery Friend", color: "#ec407a", bio: "Cute kindergarten girl who vents her rage on a stuffed bunny." },
          { key: "masao_sato", displayName: "Masao Sato", series: "Shin-chan", role: "Timid Friend", color: "#26a69a", bio: "Timid kindergarten boy with an onion-shaped head." },
          { key: "bo_chan", displayName: "Bo-chan", series: "Shin-chan", role: "Calm Friend", color: "#8d6e63", bio: "Quiet boy with a runny nose who collects unique stones." }
        ]);
      });
  }, []);

  const handleFileSelect = (file: File) => {
    if (!file.type.startsWith('image/')) {
      setError("Please upload a valid image file (JPG, PNG, WEBP).");
      return;
    }
    setError(null);
    setSelectedFile(file);
    setPreviewUrl(URL.createObjectURL(file));
    setResult(null);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleClassify = async () => {
    if (!selectedFile) return;

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('image', selectedFile);

    try {
      const response = await axios.post('/api/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setResult(response.data);
    } catch (err: any) {
      console.error("Classification error:", err);
      const msg = err.response?.data?.error || err.message || "Failed to classify image. Ensure backend & ML service are running.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setResult(null);
    setError(null);
  };

  return (
    <div className="container">
      {/* Header */}
      <header className="header">
        <div className="header-badge">
          <Sparkles size={16} /> ConvNeXt-Tiny Deep Learning Vision Model
        </div>
        <h1 className="header-title">Doraemon & Shin-chan Character AI</h1>
        <p className="header-subtitle">
          Upload any anime or cartoon image to automatically recognize characters from Doraemon and Crayon Shin-chan in real-time.
        </p>
      </header>

      {/* Main Grid */}
      <div className="grid-layout">
        {/* Left Column: Upload & Control */}
        <div className="glass-panel">
          <h2 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '1.25rem', color: '#fff', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <ImageIcon size={20} color="#00a0e9" /> Image Input
          </h2>

          {!previewUrl ? (
            <div
              className="upload-area"
              onDragOver={(e) => e.preventDefault()}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <input
                type="file"
                ref={fileInputRef}
                style={{ display: 'none' }}
                accept="image/*"
                onChange={(e) => e.target.files?.[0] && handleFileSelect(e.target.files[0])}
              />
              <Upload size={48} color="#00a0e9" style={{ marginBottom: '1rem', opacity: 0.8 }} />
              <p style={{ fontWeight: 600, color: '#fff', marginBottom: '0.25rem' }}>
                Drag and drop your image here
              </p>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                Supports PNG, JPG, JPEG, WEBP up to 10MB
              </p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div className="preview-container">
                <img src={previewUrl} alt="Selected Character" className="preview-image" />
              </div>
              <div style={{ display: 'flex', gap: '0.75rem' }}>
                <button
                  className="btn-action btn-primary"
                  onClick={handleClassify}
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <RefreshCw size={18} className="animate-spin" /> Analyzing Image...
                    </>
                  ) : (
                    <>
                      <Sparkles size={18} /> Identify Character
                    </>
                  )}
                </button>
                <button
                  onClick={handleReset}
                  style={{
                    padding: '0.9rem',
                    borderRadius: '0.75rem',
                    background: 'rgba(255,255,255,0.08)',
                    border: 'none',
                    color: '#fff',
                    cursor: 'pointer'
                  }}
                  title="Reset image"
                >
                  <RefreshCw size={18} />
                </button>
              </div>
            </div>
          )}

          {error && (
            <div style={{ marginTop: '1.25rem', padding: '1rem', background: 'rgba(229,57,53,0.15)', border: '1px solid rgba(229,57,53,0.3)', borderRadius: '0.75rem', color: '#ff8a80', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <AlertCircle size={18} />
              {error}
            </div>
          )}
        </div>

        {/* Right Column: Prediction Results */}
        <div className="glass-panel">
          <h2 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '1.25rem', color: '#fff', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <CheckCircle2 size={20} color="#ffd54f" /> Recognition Result
          </h2>

          {result ? (
            <div className="result-card">
              <div className="result-header">
                <span className={`result-badge ${result.series === 'Doraemon' ? 'badge-doraemon' : 'badge-shinchan'}`}>
                  {result.series} Series
                </span>
                <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                  {result.role}
                </span>
              </div>

              <div>
                <h3 className="character-title">{result.displayName}</h3>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '0.75rem' }}>
                  <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)', fontWeight: 600 }}>
                    Confidence Score
                  </span>
                  <span style={{ fontSize: '1.1rem', fontWeight: 800, color: '#ffd54f' }}>
                    {result.confidence}%
                  </span>
                </div>
                <div className="confidence-bar-bg">
                  <div className="confidence-bar-fill" style={{ width: `${result.confidence}%` }}></div>
                </div>
              </div>

              {result.topPredictions && result.topPredictions.length > 0 && (
                <div>
                  <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '0.5rem' }}>
                    Alternative Top Matches
                  </p>
                  <div className="prob-list">
                    {result.topPredictions.map((pred, idx) => (
                      <div key={idx} className="prob-item">
                        <span style={{ fontWeight: 600, color: '#fff' }}>{pred.display_name}</span>
                        <span style={{ color: 'var(--text-muted)', fontWeight: 700 }}>{pred.confidence}%</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div style={{ height: '260px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center', color: 'var(--text-muted)' }}>
              <Info size={40} style={{ opacity: 0.4, marginBottom: '1rem' }} />
              <p style={{ fontWeight: 500 }}>No image classified yet.</p>
              <p style={{ fontSize: '0.85rem', opacity: 0.7 }}>Upload an image on the left and click "Identify Character".</p>
            </div>
          )}
        </div>
      </div>

      {/* Character Cards Showcase */}
      <section className="character-gallery">
        <h2 className="gallery-title">
          <Heart size={22} color="#e53935" /> Supported Character Roster
        </h2>
        <div className="gallery-grid">
          {characters.map((char) => (
            <div key={char.key} className="gallery-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                <span style={{ fontWeight: 800, fontSize: '1.05rem', color: '#fff' }}>{char.displayName}</span>
                <span className={`result-badge ${char.series === 'Doraemon' ? 'badge-doraemon' : 'badge-shinchan'}`} style={{ fontSize: '0.7rem' }}>
                  {char.series}
                </span>
              </div>
              <p style={{ fontSize: '0.8rem', color: char.color, fontWeight: 700, marginBottom: '0.5rem' }}>{char.role}</p>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: 1.4 }}>{char.bio}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
