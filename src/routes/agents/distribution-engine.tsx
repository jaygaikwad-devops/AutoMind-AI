import { createFileRoute } from '@tanstack/react-router';
import { useState } from 'react';
import { Share2, Calendar, Clock, Plus, Loader2, Image as ImageIcon } from 'lucide-react';

export const Route = createFileRoute('/agents/distribution-engine')({
  component: DistributionEngine,
});

function DistributionEngine() {
  const [loading, setLoading] = useState(false);

  const handleSchedule = () => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      alert('Content added to the distribution queue!');
    }, 1500);
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-500 max-w-5xl mx-auto">
      <div>
        <div className="flex items-center gap-3 mb-2">
          <div className="grid h-10 w-10 place-items-center rounded-xl glass-strong" style={{ boxShadow: `0 4px 20px -5px var(--neon-pink)` }}>
            <Share2 className="h-5 w-5 text-[var(--neon-pink)]" />
          </div>
          <h1 className="text-3xl font-display font-bold text-foreground">Distribution Engine</h1>
        </div>
        <p className="text-muted-foreground mt-2">
          Omnichannel scheduling and autonomous posting. Let the AI find the optimal time to post across all your connected social accounts.
        </p>
      </div>

      <div className="grid md:grid-cols-3 gap-8">
        
        {/* Scheduler Form */}
        <div className="md:col-span-1 space-y-6">
          <div className="glass-strong rounded-2xl p-6">
            <h3 className="font-semibold mb-4">New Post</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-muted-foreground mb-1.5 uppercase tracking-wider">Select Asset</label>
                <div className="border border-white/10 border-dashed rounded-xl p-4 text-center cursor-pointer hover:bg-white/5 transition flex flex-col items-center gap-2">
                  <ImageIcon className="w-6 h-6 text-muted-foreground" />
                  <span className="text-xs text-muted-foreground font-medium">Select from Creative Studio</span>
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-muted-foreground mb-1.5 uppercase tracking-wider">Caption</label>
                <textarea 
                  className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-sm focus:outline-none focus:border-[var(--neon-pink)] transition resize-none h-24"
                  placeholder="Generated caption will appear here..."
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-muted-foreground mb-1.5 uppercase tracking-wider">Platforms</label>
                <div className="flex gap-2">
                  {['Instagram', 'TikTok', 'LinkedIn', 'X/Twitter'].map(p => (
                    <div key={p} className="bg-[var(--neon-pink)]/20 text-[var(--neon-pink)] border border-[var(--neon-pink)]/30 text-xs px-2.5 py-1 rounded-md font-medium cursor-pointer">
                      {p}
                    </div>
                  ))}
                </div>
              </div>

              <div className="pt-2">
                <div className="flex items-center justify-between bg-white/5 rounded-lg p-3 border border-white/5 mb-4">
                  <span className="text-xs font-medium text-muted-foreground">Network Cost</span>
                  <span className="text-sm font-bold">1 <span className="text-xs font-normal text-muted-foreground">Credit / Post</span></span>
                </div>
                
                <button 
                  onClick={handleSchedule}
                  disabled={loading}
                  className="w-full bg-gradient-to-r from-[var(--neon-pink)] to-[var(--neon-violet)] text-background font-bold py-3 rounded-xl flex items-center justify-center gap-2 hover:opacity-90 disabled:opacity-50 transition text-sm"
                >
                  {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Calendar className="w-4 h-4" />}
                  Schedule Post (1 Credit)
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Calendar View (Mock) */}
        <div className="md:col-span-2 glass rounded-3xl p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="font-semibold text-lg">Upcoming Queue</h3>
            <div className="flex gap-2">
              <button className="bg-white/5 hover:bg-white/10 px-3 py-1.5 rounded-lg text-xs font-medium transition">Today</button>
              <button className="bg-white/5 hover:bg-white/10 px-3 py-1.5 rounded-lg text-xs font-medium transition">This Week</button>
            </div>
          </div>

          <div className="space-y-4">
            {/* Timeline Item 1 */}
            <div className="flex gap-4 group">
              <div className="flex flex-col items-center">
                <div className="w-2 h-2 rounded-full bg-[var(--neon-pink)] shadow-[0_0_8px_var(--neon-pink)] mt-2" />
                <div className="w-px h-full bg-white/10 mt-2" />
              </div>
              <div className="bg-white/5 border border-white/5 rounded-xl p-4 flex-1 group-hover:bg-white/10 transition">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2 text-xs font-medium">
                    <span className="bg-[var(--neon-violet)]/20 text-[var(--neon-violet)] px-2 py-0.5 rounded uppercase tracking-wider text-[9px]">Instagram</span>
                    <span className="bg-white/10 px-2 py-0.5 rounded uppercase tracking-wider text-[9px]">TikTok</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                    <Clock className="w-3.5 h-3.5" /> 14:30 Today
                  </div>
                </div>
                <p className="text-sm">🔥 Unleash the power of AI in your marketing stack. Stop trading time for money... #AutoMind</p>
              </div>
            </div>

            {/* Timeline Item 2 */}
            <div className="flex gap-4 group">
              <div className="flex flex-col items-center">
                <div className="w-2 h-2 rounded-full bg-[var(--neon-cyan)] shadow-[0_0_8px_var(--neon-cyan)] mt-2" />
                <div className="w-px h-full bg-white/10 mt-2" />
              </div>
              <div className="bg-white/5 border border-white/5 rounded-xl p-4 flex-1 group-hover:bg-white/10 transition">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2 text-xs font-medium">
                    <span className="bg-blue-500/20 text-blue-400 px-2 py-0.5 rounded uppercase tracking-wider text-[9px]">LinkedIn</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                    <Clock className="w-3.5 h-3.5" /> 09:00 Tomorrow
                  </div>
                </div>
                <p className="text-sm">Why the traditional agency model is dead. Here's how autonomous agents are changing the game...</p>
              </div>
            </div>
            
            <div className="flex gap-4 group opacity-50">
              <div className="flex flex-col items-center">
                <div className="w-2 h-2 rounded-full bg-white/20 mt-2" />
              </div>
              <div className="border border-white/10 border-dashed rounded-xl p-4 flex-1 text-center text-sm text-muted-foreground cursor-pointer hover:bg-white/5 transition flex items-center justify-center gap-2">
                <Plus className="w-4 h-4" /> Schedule more content
              </div>
            </div>

          </div>
        </div>

      </div>
    </div>
  );
}
