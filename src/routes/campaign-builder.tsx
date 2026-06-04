import { createFileRoute, useNavigate } from '@tanstack/react-router';
import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Loader2, Wand2 } from 'lucide-react';
import { motion } from 'motion/react';

export const Route = createFileRoute('/campaign-builder')({
  component: CampaignBuilderComponent,
});

function CampaignBuilderComponent() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    website_url: '',
    product_description: '',
    target_audience: '',
    campaign_goal: ''
  });

  const isLocalhost = typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');
const API_URL = isLocalhost ? 'http://localhost:8000/api' : (import.meta.env.VITE_API_URL || '/api');

  const analyzeMutation = useMutation({
    mutationFn: async (data: typeof formData) => {
      const res = await fetch(`${API_URL}/campaigns/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify(data),
      });
      if (!res.ok) throw new Error('Failed to analyze campaign');
      return res.json();
    },
    onSuccess: (data) => {
      navigate({ to: `/campaign/${data.id}` });
    },
    onError: (error: any) => {
      alert(error.message);
    }
  });

  return (
    <div className="min-h-screen bg-background text-foreground p-8 flex justify-center items-center">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-2xl"
      >
        <div className="text-center mb-10">
          <div className="inline-flex items-center justify-center p-3 bg-primary/10 rounded-2xl mb-6">
            <Wand2 className="w-8 h-8 text-primary" />
          </div>
          <h1 className="text-4xl font-display font-bold mb-4 tracking-tight">AI Campaign Strategist</h1>
          <p className="text-muted-foreground text-lg">Enter your product details to generate a full marketing campaign.</p>
        </div>

        <div className="glass p-8 rounded-2xl border border-white/5 space-y-6 shadow-2xl relative overflow-hidden">
          {/* Subtle gradient background */}
          <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent pointer-events-none" />

          <div className="space-y-2 relative z-10">
            <label className="text-sm font-medium text-white/90">Website URL</label>
            <input 
              type="url" 
              placeholder="https://example.com"
              className="w-full bg-black/40 border border-white/10 rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-primary/50 transition"
              value={formData.website_url}
              onChange={(e) => setFormData({...formData, website_url: e.target.value})}
            />
          </div>

          <div className="space-y-2 relative z-10">
            <label className="text-sm font-medium text-white/90">Product Description</label>
            <textarea 
              rows={3}
              placeholder="What are you selling?"
              className="w-full bg-black/40 border border-white/10 rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-primary/50 transition resize-none"
              value={formData.product_description}
              onChange={(e) => setFormData({...formData, product_description: e.target.value})}
            />
          </div>

          <div className="grid grid-cols-2 gap-6 relative z-10">
            <div className="space-y-2">
              <label className="text-sm font-medium text-white/90">Target Audience</label>
              <input 
                type="text" 
                placeholder="e.g. Small Business Owners"
                className="w-full bg-black/40 border border-white/10 rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-primary/50 transition"
                value={formData.target_audience}
                onChange={(e) => setFormData({...formData, target_audience: e.target.value})}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-white/90">Campaign Goal</label>
              <select
                className="w-full bg-black/40 border border-white/10 rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-primary/50 transition text-white"
                value={formData.campaign_goal}
                onChange={(e) => setFormData({...formData, campaign_goal: e.target.value})}
              >
                <option value="">Select a goal...</option>
                <option value="lead_gen">Lead Generation</option>
                <option value="sales">Direct Sales</option>
                <option value="awareness">Brand Awareness</option>
              </select>
            </div>
          </div>

          <button 
            onClick={() => analyzeMutation.mutate(formData)}
            disabled={analyzeMutation.isPending || (!formData.website_url && !formData.product_description)}
            className="w-full mt-6 bg-primary hover:bg-primary/90 text-primary-foreground p-4 rounded-xl font-bold flex justify-center items-center transition disabled:opacity-50 relative z-10 shadow-[0_0_20px_rgba(var(--primary),0.3)]"
          >
            {analyzeMutation.isPending ? (
              <><Loader2 className="w-5 h-5 animate-spin mr-2" /> Generating Campaign...</>
            ) : (
              <><Wand2 className="w-5 h-5 mr-2" /> Start AI Strategist</>
            )}
          </button>
        </div>
      </motion.div>
    </div>
  );
}
