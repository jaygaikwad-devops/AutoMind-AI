import { createFileRoute } from '@tanstack/react-router';
import { CreditCard, TrendingUp, Video, PenTool, Megaphone, Zap } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';

export const Route = createFileRoute('/agents/credits')({
  component: CreditsDashboard,
});

function CreditsDashboard() {
  const isLocalhost = typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');
  const API_URL = isLocalhost ? 'http://localhost:8000/api' : (import.meta.env.VITE_API_URL || '/api');

  const { data: user } = useQuery({
    queryKey: ['me'],
    queryFn: async () => {
      const res = await fetch(`${API_URL}/auth/me`, { credentials: 'include' });
      if (!res.ok) throw new Error('Not authenticated');
      return res.json();
    },
    retry: false,
  });

  const credits = user?.credits || 0;
  const maxCredits = user?.plan === 'starter' ? 500 : user?.plan === 'growth' ? 2000 : 5000;
  const percentage = Math.min(100, (credits / maxCredits) * 100);

  return (
    <div className="space-y-8 animate-in fade-in duration-500 max-w-5xl mx-auto">
      <div>
        <div className="flex items-center gap-3 mb-2">
          <div className="grid h-10 w-10 place-items-center rounded-xl glass-strong" style={{ boxShadow: `0 4px 20px -5px var(--neon-lime)` }}>
            <CreditCard className="h-5 w-5 text-[var(--neon-lime)]" />
          </div>
          <h1 className="text-3xl font-display font-bold text-foreground">Credits & Usage</h1>
        </div>
        <p className="text-muted-foreground mt-2">
          Monitor your AutoMind marketing credits, view usage history, and see how much you're saving compared to a traditional agency.
        </p>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        
        {/* Main Credit Gauge */}
        <div className="glass-strong rounded-[2rem] p-8 md:col-span-2 relative overflow-hidden border border-[var(--neon-lime)]/30">
          <div className="absolute top-0 right-0 w-64 h-64 bg-[var(--neon-lime)]/10 rounded-full blur-[80px] -z-10 pointer-events-none" />
          
          <h3 className="text-sm font-semibold tracking-widest uppercase text-muted-foreground mb-8">Remaining Credits</h3>
          
          <div className="flex items-end gap-4 mb-4">
            <span className="text-6xl md:text-8xl font-display font-bold text-white tracking-tighter">
              {credits.toLocaleString()}
            </span>
            <span className="text-2xl text-muted-foreground mb-2">/ {maxCredits.toLocaleString()}</span>
          </div>

          <div className="h-3 w-full bg-white/10 rounded-full overflow-hidden mt-6">
            <div 
              className="h-full bg-gradient-to-r from-[var(--neon-cyan)] to-[var(--neon-lime)] shadow-[0_0_10px_var(--neon-lime)]"
              style={{ width: `${percentage}%` }}
            />
          </div>
          <div className="flex justify-between items-center mt-3 text-sm text-muted-foreground">
            <span>0</span>
            <span>{percentage.toFixed(0)}% Available</span>
            <span>{maxCredits.toLocaleString()}</span>
          </div>
        </div>

        {/* Agency Cost Saved */}
        <div className="glass rounded-[2rem] p-8 border border-[var(--neon-pink)]/20 relative overflow-hidden flex flex-col justify-center text-center">
          <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-br from-[var(--neon-pink)]/10 to-[var(--neon-violet)]/10 -z-10 pointer-events-none" />
          <h3 className="text-sm font-semibold tracking-widest uppercase text-muted-foreground mb-4">Estimated Agency Cost Saved</h3>
          <div className="text-4xl md:text-5xl font-display font-bold text-white mb-2">560 USDT</div>
          <div className="flex items-center justify-center gap-1.5 text-[var(--neon-lime)] text-sm font-medium">
            <TrendingUp className="w-4 h-4" /> This Month
          </div>
        </div>

      </div>

      <div className="grid md:grid-cols-3 gap-6">
        <h2 className="md:col-span-3 text-xl font-display font-bold mt-4">Usage This Month</h2>
        
        <div className="glass rounded-2xl p-6 flex items-center gap-4">
          <div className="grid h-12 w-12 place-items-center rounded-full bg-white/5 text-[var(--neon-violet)]">
            <Video className="w-6 h-6" />
          </div>
          <div>
            <div className="text-2xl font-bold">20</div>
            <div className="text-sm text-muted-foreground uppercase tracking-wider font-semibold text-[10px]">Videos Generated</div>
          </div>
        </div>

        <div className="glass rounded-2xl p-6 flex items-center gap-4">
          <div className="grid h-12 w-12 place-items-center rounded-full bg-white/5 text-[var(--neon-cyan)]">
            <Megaphone className="w-6 h-6" />
          </div>
          <div>
            <div className="text-2xl font-bold">12</div>
            <div className="text-sm text-muted-foreground uppercase tracking-wider font-semibold text-[10px]">Active Campaigns</div>
          </div>
        </div>

        <div className="glass rounded-2xl p-6 flex items-center gap-4">
          <div className="grid h-12 w-12 place-items-center rounded-full bg-white/5 text-[var(--neon-pink)]">
            <PenTool className="w-6 h-6" />
          </div>
          <div>
            <div className="text-2xl font-bold">145</div>
            <div className="text-sm text-muted-foreground uppercase tracking-wider font-semibold text-[10px]">Content Requests</div>
          </div>
        </div>
      </div>

      {/* Top Up Section */}
      <div className="glass-strong rounded-3xl p-8 border border-white/5 mt-8 flex flex-col md:flex-row items-center justify-between gap-6">
        <div>
          <h3 className="text-lg font-bold flex items-center gap-2">
            <Zap className="w-5 h-5 text-[var(--neon-violet)]" /> Need more power?
          </h3>
          <p className="text-muted-foreground text-sm mt-1">
            Buy one-time credit packs to instantly boost your agent network's capacity. Credits never expire.
          </p>
        </div>
        <div className="flex gap-3 w-full md:w-auto">
          <button className="flex-1 md:flex-none bg-white/5 hover:bg-white/10 border border-white/10 px-6 py-3 rounded-xl text-sm font-medium transition">
            Buy 500 (12 USDT)
          </button>
          <button className="flex-1 md:flex-none bg-white/5 hover:bg-white/10 border border-white/10 px-6 py-3 rounded-xl text-sm font-medium transition">
            Buy 1,000 (22 USDT)
          </button>
        </div>
      </div>
    </div>
  );
}
