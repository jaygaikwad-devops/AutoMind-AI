import { createFileRoute } from '@tanstack/react-router';
import { useState } from 'react';
import { BrainCircuit, Globe, ArrowRight, Loader2, Play } from 'lucide-react';
import { API_URL } from '../../lib/api';

export const Route = createFileRoute('/agents/campaign-manager')({
  component: CampaignManager,
});

function CampaignManager() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');

  const handleLaunch = async () => {
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const res = await fetch(`${API_URL}/v1/marketing/full-content-bundle`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ website_url: url, product_name: url, industry: 'general' }),
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
    <div className="space-y-8 animate-in fade-in duration-500 max-w-5xl mx-auto mt-10">
      
      <div className="text-center space-y-4 mb-12">
        <div className="inline-flex items-center justify-center p-3 rounded-2xl glass-strong mb-2 shadow-[0_0_30px_-5px_var(--neon-violet)]">
          <BrainCircuit className="h-8 w-8 text-[var(--neon-violet)]" />
        </div>
        <h1 className="text-4xl md:text-5xl font-display font-bold text-foreground tracking-tight">
          Campaign Orchestrator
        </h1>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
          Input your website URL. AutoMind will scrape your brand context, generate your ad creatives, write your copy, and deploy the campaign automatically.
        </p>
      </div>

      <div className="glass-strong rounded-[2rem] p-8 md:p-12 relative overflow-hidden border border-white/10 shadow-2xl">
        {/* Glow effect */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-1/2 bg-gradient-to-b from-[var(--neon-violet)]/10 to-transparent blur-3xl -z-10 pointer-events-none" />
        
        <div className="max-w-3xl mx-auto space-y-8">
          
          <div className="space-y-3">
            <label className="text-sm font-semibold tracking-wide uppercase text-muted-foreground ml-2">Target URL</label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <Globe className="h-5 w-5 text-muted-foreground" />
              </div>
              <input
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://your-product-page.com"
                className="w-full bg-white/5 border border-white/10 rounded-2xl py-4 pl-12 pr-4 text-lg focus:outline-none focus:ring-2 focus:ring-[var(--neon-violet)] transition-all"
              />
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            <div className="bg-white/5 rounded-xl p-5 border border-white/5">
              <div className="text-xs font-mono uppercase text-[var(--neon-lime)] mb-1">Estimated Value</div>
              <div className="text-2xl font-bold">100+ USDT</div>
              <div className="text-xs text-muted-foreground mt-2 space-y-1">
                <div className="flex items-center gap-2"><div className="w-1 h-1 rounded-full bg-white/50" /> 20 Variations of Hooks & CTAs</div>
                <div className="flex items-center gap-2"><div className="w-1 h-1 rounded-full bg-white/50" /> 5 Video Ad Scripts</div>
                <div className="flex items-center gap-2"><div className="w-1 h-1 rounded-full bg-white/50" /> Competitor Positioning matrix</div>
              </div>
            </div>

            <div className="bg-white/5 rounded-xl p-5 border border-white/5 flex flex-col justify-center items-center text-center">
              <div className="text-xs font-mono uppercase text-[var(--neon-violet)] mb-2">Network Cost</div>
              <div className="text-3xl font-display font-bold text-white">
                20 <span className="text-sm text-muted-foreground">Credits</span>
              </div>
            </div>
          </div>

          <button
            onClick={handleLaunch}
            disabled={!url || loading}
            className="w-full relative group overflow-hidden rounded-2xl bg-foreground text-background font-bold text-lg py-5 transition-all hover:scale-[1.01] disabled:opacity-50 disabled:hover:scale-100"
          >
            <div className="absolute inset-0 bg-gradient-to-r from-[var(--neon-violet)] via-[var(--neon-pink)] to-[var(--neon-cyan)] opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            <span className="relative z-10 flex items-center justify-center gap-2 group-hover:text-white">
              {loading ? (
                <Loader2 className="h-6 w-6 animate-spin" />
              ) : (
                <>
                  <Play className="h-5 w-5 fill-current" /> Orchestrate Campaign <ArrowRight className="h-5 w-5 ml-1" />
                </>
              )}
            </span>
          </button>

          {error && (
            <div className="mt-4 p-4 bg-red-500/20 border border-red-500/30 rounded-xl text-sm text-red-200">{error}</div>
          )}

          {result && (
            <div className="mt-6 glass p-6 rounded-2xl space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-bold text-white">Campaign Generated ✓</h3>
                <span className="text-sm text-muted-foreground">{result.total_credits_committed} credits used</span>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {result.agents_completed?.map((agent: string) => (
                  <div key={agent} className="bg-white/5 rounded-lg p-3 text-center">
                    <div className="text-xs text-muted-foreground uppercase">{agent}</div>
                    <div className="text-sm font-bold text-[var(--neon-lime)]">{result.quality_scores?.[agent] || '—'}/100</div>
                  </div>
                ))}
              </div>
            </div>
          )}
          
        </div>
      </div>
      
    </div>
  );
}
