import { createFileRoute } from '@tanstack/react-router';
import { CreditCard, TrendingUp, Video, PenTool, Megaphone, Zap, History } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { useState } from 'react';
import { PaymentSelectorModal } from '@/components/billing/PaymentMethodSelector';

export const Route = createFileRoute('/agents/credits')({
  component: CreditsDashboard,
});

function CreditsDashboard() {
  const isLocalhost = typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');
  const API_URL = isLocalhost ? 'http://localhost:8000/api' : (import.meta.env.VITE_API_URL || '/api');

  const [isPaymentModalOpen, setIsPaymentModalOpen] = useState(false);
  const [paymentContext, setPaymentContext] = useState<{type: 'plan' | 'pack', id: string}>({type: 'plan', id: 'growth'});

  const { data: status } = useQuery({
    queryKey: ['billing-status'],
    queryFn: async () => {
      const res = await fetch(`${API_URL}/billing/status`, { credentials: 'include' });
      if (!res.ok) throw new Error('Failed to fetch status');
      return res.json();
    },
    retry: false,
  });

  const { data: history } = useQuery({
    queryKey: ['billing-history'],
    queryFn: async () => {
      const res = await fetch(`${API_URL}/billing/history`, { credentials: 'include' });
      if (!res.ok) throw new Error('Failed to fetch history');
      return res.json();
    },
    retry: false,
  });

  const creditsRemaining = status?.credits_remaining || 0;
  const creditsTotal = status?.credits_total || 500;
  const percentage = Math.min(100, (creditsRemaining / Math.max(1, creditsTotal)) * 100);

  const handleOpenPayment = (type: 'plan' | 'pack', id: string) => {
    setPaymentContext({ type, id });
    setIsPaymentModalOpen(true);
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-500 max-w-6xl mx-auto pb-20">
      <div>
        <div className="flex items-center gap-3 mb-2">
          <div className="grid h-10 w-10 place-items-center rounded-xl glass-strong" style={{ boxShadow: `0 4px 20px -5px var(--neon-lime)` }}>
            <CreditCard className="h-5 w-5 text-[var(--neon-lime)]" />
          </div>
          <h1 className="text-3xl font-display font-bold text-foreground">Billing & Usage</h1>
        </div>
        <p className="text-muted-foreground mt-2">
          Manage your subscription, view your payment history, and buy credit packs.
        </p>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        
        {/* Main Credit Gauge */}
        <div className="glass-strong rounded-[2rem] p-8 md:col-span-2 relative overflow-hidden border border-[var(--neon-lime)]/30">
          <div className="absolute top-0 right-0 w-64 h-64 bg-[var(--neon-lime)]/10 rounded-full blur-[80px] -z-10 pointer-events-none" />
          
          <h3 className="text-sm font-semibold tracking-widest uppercase text-muted-foreground mb-8">Remaining Credits</h3>
          
          <div className="flex items-end gap-4 mb-4">
            <span className="text-6xl md:text-8xl font-display font-bold text-white tracking-tighter">
              {creditsRemaining.toLocaleString()}
            </span>
            <span className="text-2xl text-muted-foreground mb-2">/ {creditsTotal.toLocaleString()}</span>
          </div>

          <div className="h-3 w-full bg-white/10 rounded-full overflow-hidden mt-6">
            <div 
              className="h-full bg-gradient-to-r from-[var(--neon-cyan)] to-[var(--neon-lime)] shadow-[0_0_10px_var(--neon-lime)] transition-all duration-1000"
              style={{ width: `${percentage}%` }}
            />
          </div>
          <div className="flex justify-between items-center mt-3 text-sm text-muted-foreground">
            <span>0</span>
            <span>{percentage.toFixed(0)}% Available</span>
            <span>{creditsTotal.toLocaleString()}</span>
          </div>
        </div>

        {/* Current Plan Card */}
        <div className="glass rounded-[2rem] p-8 border border-[var(--neon-cyan)]/20 relative overflow-hidden flex flex-col justify-center">
          <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-br from-[var(--neon-cyan)]/10 to-[var(--neon-violet)]/10 -z-10 pointer-events-none" />
          <h3 className="text-sm font-semibold tracking-widest uppercase text-muted-foreground mb-4 flex items-center gap-2"><CreditCard className="w-4 h-4"/> Current Plan</h3>
          
          <div className="text-3xl font-display font-bold text-white mb-6 capitalize">{status?.plan || "Starter"}</div>
          
          <div className="space-y-4">
            <div className="flex justify-between items-center text-sm border-b border-white/5 pb-2">
              <span className="text-muted-foreground">Provider:</span>
              <span className="capitalize">{status?.provider || "N/A"}</span>
            </div>
            <div className="flex justify-between items-center text-sm border-b border-white/5 pb-2">
              <span className="text-muted-foreground">Next Renewal:</span>
              <span>{status?.renewal_date ? new Date(status.renewal_date).toLocaleDateString() : "N/A"}</span>
            </div>
            <div className="flex justify-between items-center text-sm">
              <span className="text-muted-foreground">Status:</span>
              <span className="text-[var(--neon-lime)] capitalize font-semibold">{status?.subscription_status || "Active"}</span>
            </div>
          </div>
          
          {status?.plan !== "agency" && (
            <button onClick={() => handleOpenPayment('plan', status?.plan === 'starter' ? 'growth' : 'agency')} className="mt-6 w-full py-2.5 rounded-xl bg-[var(--neon-cyan)]/10 hover:bg-[var(--neon-cyan)]/20 text-[var(--neon-cyan)] border border-[var(--neon-cyan)]/30 font-medium transition">
              Upgrade Plan
            </button>
          )}
        </div>
      </div>

      {/* Usage Summary Card */}
      <div className="grid md:grid-cols-4 gap-6">
        <h2 className="md:col-span-4 text-xl font-display font-bold mt-4">Usage This Month</h2>
        
        <div className="glass rounded-2xl p-6 flex flex-col justify-center">
          <div className="flex items-center gap-3 mb-2">
            <Video className="w-5 h-5 text-[var(--neon-violet)]" />
            <span className="text-sm text-muted-foreground font-semibold">Videos Generated</span>
          </div>
          <div className="text-3xl font-bold">12</div>
        </div>

        <div className="glass rounded-2xl p-6 flex flex-col justify-center">
          <div className="flex items-center gap-3 mb-2">
            <Megaphone className="w-5 h-5 text-[var(--neon-cyan)]" />
            <span className="text-sm text-muted-foreground font-semibold">Campaigns Built</span>
          </div>
          <div className="text-3xl font-bold">8</div>
        </div>

        <div className="glass rounded-2xl p-6 flex flex-col justify-center border border-[var(--neon-pink)]/20">
          <div className="flex items-center gap-3 mb-2">
            <Zap className="w-5 h-5 text-[var(--neon-pink)]" />
            <span className="text-sm text-muted-foreground font-semibold">Credits Used</span>
          </div>
          <div className="text-3xl font-bold text-[var(--neon-pink)]">420</div>
        </div>
        
        <div className="glass rounded-2xl p-6 flex flex-col justify-center border border-[var(--neon-lime)]/20">
          <div className="flex items-center gap-3 mb-2">
            <TrendingUp className="w-5 h-5 text-[var(--neon-lime)]" />
            <span className="text-sm text-muted-foreground font-semibold">Credits Remaining</span>
          </div>
          <div className="text-3xl font-bold text-[var(--neon-lime)]">{creditsRemaining.toLocaleString()}</div>
        </div>
      </div>

      {/* Top Up Section */}
      <div className="glass-strong rounded-3xl p-8 border border-white/5 mt-8 flex flex-col md:flex-row items-center justify-between gap-6">
        <div>
          <h3 className="text-lg font-bold flex items-center gap-2">
            <Zap className="w-5 h-5 text-[var(--neon-violet)]" /> Need more power?
          </h3>
          <p className="text-muted-foreground text-sm mt-1">
            Buy one-time credit packs to instantly boost your capacity. Credits never expire.
          </p>
        </div>
        <div className="flex gap-3 w-full md:w-auto">
          <button onClick={() => handleOpenPayment('pack', 'pack_500')} className="flex-1 md:flex-none bg-white/5 hover:bg-white/10 border border-white/10 px-6 py-3 rounded-xl text-sm font-medium transition">
            Buy 500
          </button>
          <button onClick={() => handleOpenPayment('pack', 'pack_1000')} className="flex-1 md:flex-none bg-white/5 hover:bg-white/10 border border-white/10 px-6 py-3 rounded-xl text-sm font-medium transition">
            Buy 1,000
          </button>
        </div>
      </div>
      
      {/* Payment History */}
      <div className="mt-12">
        <h2 className="text-xl font-display font-bold mb-6 flex items-center gap-2">
          <History className="w-5 h-5" /> Payment History
        </h2>
        <div className="glass rounded-2xl border border-white/5 overflow-hidden">
          <Table>
            <TableHeader className="bg-white/5">
              <TableRow className="border-b border-white/10 hover:bg-transparent">
                <TableHead>Date</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Credits</TableHead>
                <TableHead>Amount</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {!history || history.length === 0 ? (
                <TableRow className="hover:bg-transparent">
                  <TableCell colSpan={5} className="text-center py-8 text-muted-foreground">
                    No payment history found.
                  </TableCell>
                </TableRow>
              ) : (
                history.map((tx: any) => (
                  <TableRow key={tx.id} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                    <TableCell>{new Date(tx.date).toLocaleDateString()}</TableCell>
                    <TableCell className="font-medium">{tx.type}</TableCell>
                    <TableCell className="text-[var(--neon-lime)] font-medium">+{tx.credits}</TableCell>
                    <TableCell className="uppercase">{tx.amount} {tx.currency}</TableCell>
                    <TableCell>
                      <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${tx.status === 'succeeded' || tx.status === 'paid' ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'}`}>
                        {tx.status}
                      </span>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      </div>

      {isPaymentModalOpen && (
        <PaymentSelectorModal 
          isOpen={isPaymentModalOpen} 
          onClose={() => setIsPaymentModalOpen(false)} 
          itemType={paymentContext.type}
          itemId={paymentContext.id}
        />
      )}
    </div>
  );
}
