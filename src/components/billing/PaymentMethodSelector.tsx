import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { CreditCard, Shield } from 'lucide-react';
import { useState } from 'react';

interface PaymentSelectorProps {
  isOpen: boolean;
  onClose: () => void;
  itemType: 'plan' | 'pack';
  itemId: string;
}

export function PaymentSelectorModal({ isOpen, onClose, itemType, itemId }: PaymentSelectorProps) {
  const [loading, setLoading] = useState<string | null>(null);
  
  const isLocalhost = typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');
  const API_URL = isLocalhost ? 'http://localhost:8000/api' : (import.meta.env.VITE_API_URL || '/api');

  const loadRazorpayScript = () => {
    return new Promise((resolve) => {
      if ((window as any).Razorpay) {
        resolve(true);
        return;
      }
      const script = document.createElement('script');
      script.src = 'https://checkout.razorpay.com/v1/checkout.js';
      script.onload = () => resolve(true);
      script.onerror = () => resolve(false);
      document.body.appendChild(script);
    });
  };

  const handleSelect = async (provider: 'stripe' | 'razorpay') => {
    try {
      setLoading(provider);
      
      const currency = provider === 'razorpay' ? 'inr' : 'usd';

      const res = await fetch(`${API_URL}/billing/checkout`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          item_id: itemId,
          item_type: itemType,
          provider: provider,
          currency: currency
        })
      });

      if (!res.ok) {
        throw new Error('Failed to create checkout session');
      }

      const data = await res.json();

      if (provider === 'stripe') {
        window.location.href = data.url_or_id;
      } else if (provider === 'razorpay') {
        const isLoaded = await loadRazorpayScript();
        if (!isLoaded) {
          alert('Failed to load Razorpay SDK');
          setLoading(null);
          return;
        }

        // Fetch config to get key ID
        const configRes = await fetch(`${API_URL}/billing/config`);
        const config = await configRes.json();

        const options = {
          key: config.razorpay_key_id,
          order_id: data.url_or_id,
          name: "AutoMind AI",
          description: `Purchase ${itemType}: ${itemId}`,
          handler: function (response: any) {
            // Wait a moment for webhook to process, then refresh page
            setTimeout(() => {
              window.location.reload();
            }, 2000);
          },
          theme: {
            color: "#bdff00" // var(--neon-lime)
          }
        };

        const rzp = new (window as any).Razorpay(options);
        rzp.on('payment.failed', function (response: any) {
          console.error(response.error);
        });
        rzp.open();
        onClose(); // Close the modal
      }
    } catch (err) {
      console.error(err);
      alert('Error initiating payment');
    } finally {
      setLoading(null);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md bg-black border border-white/10 text-white">
        <DialogHeader>
          <DialogTitle className="text-xl font-display">Select Payment Method</DialogTitle>
          <DialogDescription className="text-muted-foreground">
            Choose your preferred payment gateway to continue.
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-4 py-4">
          <button 
            onClick={() => handleSelect('razorpay')}
            disabled={loading !== null}
            className="flex items-center gap-4 p-4 rounded-xl border border-white/10 bg-white/5 hover:bg-white/10 transition-colors text-left"
          >
            <div className="bg-[#3395FF]/10 p-3 rounded-lg text-[#3395FF]">
              <Shield className="w-6 h-6" />
            </div>
            <div className="flex-1">
              <h4 className="font-semibold text-white">Razorpay</h4>
              <p className="text-xs text-muted-foreground mt-1">UPI, Cards, Net Banking (Recommended for India)</p>
            </div>
            {loading === 'razorpay' && <span className="text-sm text-muted-foreground animate-pulse">Loading...</span>}
          </button>

          <button 
            onClick={() => handleSelect('stripe')}
            disabled={loading !== null}
            className="flex items-center gap-4 p-4 rounded-xl border border-white/10 bg-white/5 hover:bg-white/10 transition-colors text-left"
          >
            <div className="bg-[#635BFF]/10 p-3 rounded-lg text-[#635BFF]">
              <CreditCard className="w-6 h-6" />
            </div>
            <div className="flex-1">
              <h4 className="font-semibold text-white">Stripe</h4>
              <p className="text-xs text-muted-foreground mt-1">International Cards (USD)</p>
            </div>
            {loading === 'stripe' && <span className="text-sm text-muted-foreground animate-pulse">Loading...</span>}
          </button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
