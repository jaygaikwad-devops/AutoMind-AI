import { createFileRoute } from '@tanstack/react-router';
import { useState } from 'react';
import { Target, FileText, CheckSquare, Video, Download, Play, Loader2 } from 'lucide-react';

export const Route = createFileRoute('/agents/lead-engine')({
  component: LeadEngine,
});

function LeadEngine() {
  const [magnetType, setMagnetType] = useState('pdf');
  const [topic, setTopic] = useState('');
  const [loading, setLoading] = useState(false);

  const handleGenerate = () => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      alert('Lead Magnet generated successfully!');
    }, 2000);
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-500 max-w-5xl mx-auto">
      <div>
        <div className="flex items-center gap-3 mb-2">
          <div className="grid h-10 w-10 place-items-center rounded-xl glass-strong" style={{ boxShadow: `0 4px 20px -5px var(--neon-cyan)` }}>
            <Target className="h-5 w-5 text-[var(--neon-cyan)]" />
          </div>
          <h1 className="text-3xl font-display font-bold text-foreground">Lead Engine</h1>
        </div>
        <p className="text-muted-foreground mt-2">
          Instantly generate high-converting Lead Magnets (PDFs, Checklists) and deploy the capture pages to start building your list automatically.
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-8">
        <div className="glass-strong rounded-3xl p-6 md:p-8 space-y-8">
          
          <div className="space-y-4">
            <label className="block text-sm font-medium text-muted-foreground uppercase tracking-wider">1. Select Format</label>
            <div className="grid grid-cols-2 gap-3">
              {[
                { id: 'pdf', name: 'PDF Guide', icon: FileText },
                { id: 'checklist', name: 'Checklist', icon: CheckSquare },
                { id: 'webinar', name: 'Webinar Script', icon: Video },
                { id: 'template', name: 'Notion Template', icon: Download },
              ].map((type) => (
                <div
                  key={type.id}
                  onClick={() => setMagnetType(type.id)}
                  className={`border rounded-xl p-4 cursor-pointer transition-all flex flex-col items-center gap-2 text-center ${
                    magnetType === type.id ? 'border-[var(--neon-cyan)] bg-[var(--neon-cyan)]/10 text-white' : 'border-white/10 glass hover:bg-white/5 text-muted-foreground'
                  }`}
                >
                  <type.icon className="w-5 h-5" />
                  <span className="text-sm font-medium">{type.name}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="space-y-4">
            <label className="block text-sm font-medium text-muted-foreground uppercase tracking-wider">2. Describe the value proposition</label>
            <textarea 
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              className="w-full h-32 bg-white/5 border border-white/10 rounded-xl p-4 text-sm focus:outline-none focus:border-[var(--neon-cyan)] transition resize-none"
              placeholder="E.g., A comprehensive guide on how to scale a B2B SaaS from $0 to $10k MRR using autonomous AI agents..."
            />
          </div>

          <div className="pt-2">
            <div className="bg-white/5 rounded-xl p-4 border border-white/5 flex items-center justify-between mb-4">
              <div>
                <div className="text-xs font-mono uppercase text-[var(--neon-lime)] mb-1">Estimated Value</div>
                <div className="font-bold text-lg">150+ USDT</div>
              </div>
              <div className="text-right">
                <div className="text-xs font-mono uppercase text-[var(--neon-cyan)] mb-1">Cost</div>
                <div className="font-bold text-lg">30 <span className="text-sm font-normal text-muted-foreground">Credits</span></div>
              </div>
            </div>

            <button 
              onClick={handleGenerate}
              disabled={loading || !topic}
              className="w-full bg-gradient-to-r from-[var(--neon-cyan)] to-[var(--neon-violet)] text-background font-bold py-4 rounded-xl flex items-center justify-center gap-2 hover:opacity-90 disabled:opacity-50 transition"
            >
              {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Play className="w-5 h-5" />}
              Generate Lead Magnet & Capture Page
            </button>
          </div>

        </div>

        <div className="space-y-6">
          <div className="glass rounded-2xl p-6 border border-white/5">
            <h3 className="font-semibold text-lg mb-4 flex items-center gap-2">
              <Target className="w-5 h-5 text-[var(--neon-violet)]" /> Active Lead Capture
            </h3>
            
            <div className="space-y-4">
              {/* Mock active capture page */}
              <div className="bg-white/5 border border-white/10 rounded-xl p-4">
                <div className="flex justify-between items-start mb-2">
                  <div className="font-medium text-sm">"The 2026 AI Marketing Blueprint"</div>
                  <span className="bg-[var(--neon-lime)]/20 text-[var(--neon-lime)] px-2 py-0.5 rounded text-[10px] uppercase font-bold tracking-wider flex items-center gap-1.5">
                    <span className="w-1 h-1 rounded-full bg-[var(--neon-lime)] animate-pulse" /> Live
                  </span>
                </div>
                <div className="text-xs text-muted-foreground mb-4">PDF Guide · Deployed 3 days ago</div>
                
                <div className="grid grid-cols-2 gap-2 text-center">
                  <div className="bg-black/20 rounded-lg p-2">
                    <div className="text-xl font-bold text-white">1,492</div>
                    <div className="text-[10px] uppercase text-muted-foreground">Visitors</div>
                  </div>
                  <div className="bg-[var(--neon-cyan)]/10 rounded-lg p-2 border border-[var(--neon-cyan)]/20">
                    <div className="text-xl font-bold text-[var(--neon-cyan)]">43%</div>
                    <div className="text-[10px] uppercase text-muted-foreground">Conv. Rate</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
