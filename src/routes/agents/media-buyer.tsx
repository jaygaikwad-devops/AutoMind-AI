import { createFileRoute } from '@tanstack/react-router';
import { useState } from 'react';
import { Megaphone, Target, DollarSign, TrendingUp, Play, Loader2 } from 'lucide-react';

export const Route = createFileRoute('/agents/media-buyer')({
  component: MediaBuyerAI,
});

function MediaBuyerAI() {
  const [budget, setBudget] = useState('500');
  const [loading, setLoading] = useState(false);

  const handleLaunch = () => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      alert('Ad campaigns dispatched to Meta & TikTok!');
    }, 2000);
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-500 max-w-5xl mx-auto">
      <div>
        <div className="flex items-center gap-3 mb-2">
          <div className="grid h-10 w-10 place-items-center rounded-xl glass-strong" style={{ boxShadow: `0 4px 20px -5px var(--neon-cyan)` }}>
            <Megaphone className="h-5 w-5 text-[var(--neon-cyan)]" />
          </div>
          <h1 className="text-3xl font-display font-bold text-foreground">Media Buyer AI</h1>
        </div>
        <p className="text-muted-foreground mt-2">
          Self-tuning ad campaigns across Meta and TikTok. The AI tests creatives, shifts budget to winning audiences, and scales ROAS automatically.
        </p>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        <div className="glass-strong rounded-2xl p-6 md:col-span-2">
          <h3 className="font-semibold text-lg mb-6 flex items-center gap-2">
            <Target className="w-5 h-5 text-[var(--neon-violet)]" /> Campaign Setup
          </h3>
          
          <div className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-muted-foreground mb-2">Target Audience Persona</label>
              <select className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-sm focus:outline-none">
                <option>SaaS Founders (B2B)</option>
                <option>E-commerce Owners (DTC)</option>
                <option>Marketing Agencies (B2B)</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-muted-foreground mb-2">Daily Budget (USD)</label>
              <div className="relative">
                <DollarSign className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <input 
                  type="number" 
                  value={budget}
                  onChange={(e) => setBudget(e.target.value)}
                  className="w-full bg-white/5 border border-white/10 rounded-xl py-3 pl-9 pr-4 text-sm focus:outline-none" 
                />
              </div>
            </div>

            <div className="pt-4 mt-4 border-t border-white/10">
              <div className="flex items-center justify-between mb-4">
                <div className="text-sm font-medium">Auto-Optimization</div>
                <div className="w-10 h-5 bg-[var(--neon-lime)]/20 rounded-full flex items-center p-1 cursor-pointer">
                  <div className="w-3 h-3 rounded-full bg-[var(--neon-lime)] transform translate-x-5" />
                </div>
              </div>
              <p className="text-xs text-muted-foreground">
                If enabled, the AI will pause underperforming ads and increase budget for ads hitting your target CPA.
              </p>
            </div>

            <button
              onClick={handleLaunch}
              disabled={loading}
              className="w-full bg-gradient-to-r from-[var(--neon-violet)] to-[var(--neon-cyan)] text-background font-bold py-4 rounded-xl flex items-center justify-center gap-2 hover:opacity-90 transition mt-4"
            >
              {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Play className="w-5 h-5" />}
              Launch Campaigns
            </button>
          </div>
        </div>

        <div className="space-y-6">
          <div className="glass rounded-2xl p-6 border border-white/5">
            <div className="text-xs font-mono uppercase text-[var(--neon-cyan)] mb-2">Network Cost</div>
            <div className="text-4xl font-display font-bold text-white mb-1">
              30 <span className="text-sm text-muted-foreground font-sans">Credits</span>
            </div>
            <div className="text-xs text-muted-foreground">Per Campaign Deployment</div>
          </div>

          <div className="glass rounded-2xl p-6 border border-white/5">
            <div className="text-xs font-mono uppercase text-[var(--neon-lime)] mb-2">Estimated Value</div>
            <div className="text-3xl font-bold text-white mb-3">180+ USDT</div>
            <div className="space-y-2 text-xs text-muted-foreground">
              <div className="flex items-center gap-2"><TrendingUp className="w-3 h-3" /> Replaces Junior Media Buyer</div>
              <div className="flex items-center gap-2"><TrendingUp className="w-3 h-3" /> 24/7 ROAS Monitoring</div>
              <div className="flex items-center gap-2"><TrendingUp className="w-3 h-3" /> A/B Testing Matrix</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
