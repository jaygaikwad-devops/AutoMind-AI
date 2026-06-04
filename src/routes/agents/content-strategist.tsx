import { createFileRoute } from '@tanstack/react-router';
import { useState } from 'react';
import { PenTool, MessageSquare, Hash, FileText, Loader2, Wand2 } from 'lucide-react';

export const Route = createFileRoute('/agents/content-strategist')({
  component: ContentStrategist,
});

function ContentStrategist() {
  const [topic, setTopic] = useState('');
  const [contentType, setContentType] = useState('caption');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState('');

  const handleGenerate = async () => {
    setLoading(true);
    // Simulate generation for now
    setTimeout(() => {
      setLoading(false);
      setResult('🔥 Unleash the power of AI in your marketing stack. Stop trading time for money and let autonomous agents scale your reach 24/7. #AutoMind #Marketing #AI');
    }, 1500);
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-500 max-w-5xl">
      <div>
        <div className="flex items-center gap-3 mb-2">
          <div className="grid h-10 w-10 place-items-center rounded-xl glass-strong" style={{ boxShadow: `0 4px 20px -5px var(--neon-cyan)` }}>
            <PenTool className="h-5 w-5 text-[var(--neon-cyan)]" />
          </div>
          <h1 className="text-3xl font-display font-bold text-foreground">Content Strategist</h1>
        </div>
        <p className="text-muted-foreground mt-2">
          Generate viral hooks, engaging captions, and SEO-optimized blogs instantly.
        </p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { id: 'caption', name: 'Social Caption', icon: MessageSquare, cost: '1 Credit' },
          { id: 'hook', name: 'Viral Hook', icon: Wand2, cost: '2 Credits' },
          { id: 'hashtag', name: 'Hashtag Set', icon: Hash, cost: '1 Credit' },
          { id: 'blog', name: 'SEO Article', icon: FileText, cost: '10 Credits' },
        ].map((type) => (
          <div
            key={type.id}
            onClick={() => setContentType(type.id)}
            className={`glass rounded-2xl p-4 cursor-pointer border transition-all ${
              contentType === type.id ? 'border-[var(--neon-cyan)] bg-white/[0.05]' : 'border-transparent hover:border-white/10'
            }`}
          >
            <type.icon className={`h-5 w-5 mb-3 ${contentType === type.id ? 'text-[var(--neon-cyan)]' : 'text-muted-foreground'}`} />
            <h3 className="font-semibold text-sm">{type.name}</h3>
            <div className="text-[10px] text-muted-foreground mt-1 font-mono uppercase tracking-wider">{type.cost}</div>
          </div>
        ))}
      </div>

      <div className="grid md:grid-cols-2 gap-8">
        <div className="glass-strong rounded-3xl p-6 md:p-8">
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-muted-foreground mb-2">What is the topic?</label>
              <textarea 
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                className="w-full h-32 bg-white/5 border border-white/10 rounded-xl p-4 text-sm focus:outline-none focus:border-[var(--neon-cyan)] transition resize-none"
                placeholder="Briefly describe what you want to write about..."
              />
            </div>

            <div className="bg-white/5 rounded-xl p-4 border border-white/5 flex items-center justify-between">
              <div>
                <div className="text-xs font-mono uppercase text-[var(--neon-lime)] mb-1">Estimated Value</div>
                <div className="font-bold text-lg">
                  {contentType === 'blog' ? '30+ USDT' : '3+ USDT'} 
                  <span className="text-sm font-normal text-muted-foreground"> / piece</span>
                </div>
              </div>
              <div className="text-right">
                <div className="text-xs font-mono uppercase text-[var(--neon-cyan)] mb-1">Cost</div>
                <div className="font-bold text-lg">
                  {contentType === 'blog' ? '10' : contentType === 'hook' ? '2' : '1'} 
                  <span className="text-sm font-normal text-muted-foreground"> Credits</span>
                </div>
              </div>
            </div>

            <button 
              onClick={handleGenerate}
              disabled={loading || !topic}
              className="w-full bg-gradient-to-r from-[var(--neon-cyan)] to-[var(--neon-lime)] text-background font-bold py-4 rounded-xl flex items-center justify-center gap-2 hover:opacity-90 disabled:opacity-50 transition"
            >
              {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <PenTool className="w-5 h-5" />}
              Generate {contentType} ({contentType === 'blog' ? '10' : contentType === 'hook' ? '2' : '1'} Credits)
            </button>
          </div>
        </div>

        <div className="glass rounded-3xl p-6 md:p-8 relative min-h-[300px]">
          <h3 className="text-sm font-medium text-muted-foreground mb-4 uppercase tracking-wider">Generated Result</h3>
          
          {loading ? (
            <div className="absolute inset-0 flex flex-col items-center justify-center text-muted-foreground gap-3">
              <Loader2 className="w-6 h-6 animate-spin text-[var(--neon-cyan)]" />
              <p className="text-xs animate-pulse">Consulting the Strategist...</p>
            </div>
          ) : result ? (
            <div className="bg-white/5 border border-white/10 rounded-xl p-6 text-sm leading-relaxed text-foreground whitespace-pre-wrap">
              {result}
            </div>
          ) : (
            <div className="absolute inset-0 flex items-center justify-center text-sm text-muted-foreground/50 text-center p-6">
              Your AI-generated content will appear here perfectly formatted.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
