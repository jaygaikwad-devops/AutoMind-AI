import { createFileRoute } from '@tanstack/react-router';
import { useState } from 'react';
import { Video, Sparkles, Image as ImageIcon, Play, Loader2 } from 'lucide-react';
import { API_URL } from '../../lib/api';

export const Route = createFileRoute('/agents/creative-studio')({
  component: CreativeStudio,
});

function CreativeStudio() {
  const [prompt, setPrompt] = useState('');
  const [videoType, setVideoType] = useState('standard');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');

  const handleGenerate = async () => {
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const res = await fetch(`${API_URL}/v1/marketing/video-scripts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ product_name: prompt, research: { company_summary: prompt } }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || `Failed (${res.status})`);
      }
      setResult(await res.json());
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-500 max-w-4xl">
      <div>
        <div className="flex items-center gap-3 mb-2">
          <div className="grid h-10 w-10 place-items-center rounded-xl glass-strong" style={{ boxShadow: `0 4px 20px -5px var(--neon-violet)` }}>
            <Video className="h-5 w-5 text-[var(--neon-violet)]" />
          </div>
          <h1 className="text-3xl font-display font-bold text-foreground">Creative Studio</h1>
        </div>
        <p className="text-muted-foreground mt-2">
          Generate 4K cinematic videos, TikTok reels, and AI ad creatives. Powered by Kling and ElevenLabs.
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div 
          onClick={() => setVideoType('standard')}
          className={`glass rounded-2xl p-6 cursor-pointer border-2 transition-all ${
            videoType === 'standard' ? 'border-[var(--neon-violet)] bg-white/[0.05]' : 'border-transparent hover:border-white/10'
          }`}
        >
          <div className="flex justify-between items-start mb-4">
            <h3 className="font-bold text-lg">Standard Reel</h3>
            <span className="bg-white/10 px-2 py-1 rounded text-xs text-muted-foreground font-mono">50 Credits</span>
          </div>
          <p className="text-sm text-muted-foreground">Template-based short form video with stock footage and AI voiceover. Perfect for daily TikToks.</p>
        </div>

        <div 
          onClick={() => setVideoType('premium')}
          className={`glass rounded-2xl p-6 cursor-pointer border-2 transition-all relative overflow-hidden ${
            videoType === 'premium' ? 'border-[var(--neon-cyan)] bg-white/[0.05]' : 'border-transparent hover:border-white/10'
          }`}
        >
          {videoType === 'premium' && (
            <div className="absolute inset-0 bg-gradient-to-br from-[var(--neon-cyan)]/10 to-transparent opacity-50" />
          )}
          <div className="flex justify-between items-start mb-4 relative z-10">
            <h3 className="font-bold text-lg flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-[var(--neon-cyan)]" /> Cinematic Video
            </h3>
            <span className="bg-[var(--neon-cyan)]/20 text-[var(--neon-cyan)] px-2 py-1 rounded text-xs font-mono font-bold">200 Credits</span>
          </div>
          <p className="text-sm text-muted-foreground relative z-10">Fully autonomous generative video scenes with cinematic lighting and custom characters.</p>
        </div>
      </div>

      <div className="glass-strong rounded-3xl p-6 md:p-8">
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-muted-foreground mb-2">Video Prompt</label>
            <textarea 
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              className="w-full h-32 bg-white/5 border border-white/10 rounded-xl p-4 text-sm focus:outline-none focus:border-[var(--neon-violet)] transition resize-none"
              placeholder="A cinematic shot of a futuristic sports car driving through a cyberpunk city in the rain..."
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-muted-foreground mb-2">Aspect Ratio</label>
              <select className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-sm focus:outline-none">
                <option value="9:16">9:16 (TikTok/Reels)</option>
                <option value="16:9">16:9 (YouTube)</option>
                <option value="1:1">1:1 (Instagram Feed)</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-muted-foreground mb-2">AI Voice</label>
              <select className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-sm focus:outline-none">
                <option value="rachel">Rachel (Calm & Professional)</option>
                <option value="drew">Drew (Energetic News)</option>
                <option value="bella">Bella (Soft & ASMR)</option>
              </select>
            </div>
          </div>

          <div className="bg-white/5 rounded-xl p-4 border border-white/5 flex items-center justify-between mt-6">
            <div>
              <div className="text-xs font-mono uppercase text-[var(--neon-lime)] mb-1">Estimated Value</div>
              <div className="font-bold text-lg">18+ USDT <span className="text-sm font-normal text-muted-foreground">/ video</span></div>
            </div>
            <div className="text-right">
              <div className="text-xs font-mono uppercase text-[var(--neon-violet)] mb-1">Cost</div>
              <div className="font-bold text-lg">{videoType === 'standard' ? '50' : '200'} <span className="text-sm font-normal text-muted-foreground">Credits</span></div>
            </div>
          </div>

          <button 
            onClick={handleGenerate}
            disabled={loading || !prompt}
            className="w-full bg-gradient-to-r from-[var(--neon-violet)] to-[var(--neon-cyan)] text-background font-bold py-4 rounded-xl flex items-center justify-center gap-2 hover:opacity-90 disabled:opacity-50 transition"
          >
            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Play className="w-5 h-5" />}
            Generate {videoType === 'standard' ? 'Standard Reel (50 Credits)' : 'Cinematic Video (200 Credits)'}
          </button>
        </div>
      </div>
    </div>
  );
}
