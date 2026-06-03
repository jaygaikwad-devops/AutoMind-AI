import { createFileRoute, Link } from '@tanstack/react-router';
import { useQuery } from '@tanstack/react-query';
import { Loader2, Plus, Calendar, Target, Globe } from 'lucide-react';

export const Route = createFileRoute('/campaigns')({
  component: CampaignsComponent,
});

function CampaignsComponent() {
  const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
const API_URL = isLocalhost ? 'http://localhost:8000/api' : (import.meta.env.VITE_API_URL || '/api');

  const { data: campaigns, isLoading } = useQuery({
    queryKey: ['campaigns'],
    queryFn: async () => {
      const res = await fetch(`${API_URL}/campaigns/history`, {
        credentials: 'include'
      });
      if (!res.ok) throw new Error('Failed to fetch campaigns');
      return res.json();
    }
  });

  return (
    <div className="min-h-screen bg-background p-8 max-w-7xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-display font-bold">Campaigns</h1>
          <p className="text-muted-foreground mt-1">Your AI-generated marketing strategies.</p>
        </div>
        <Link 
          to="/campaign-builder"
          className="bg-primary text-primary-foreground px-4 py-2 rounded-lg font-medium flex items-center hover:bg-primary/90 transition shadow-lg shadow-primary/20"
        >
          <Plus className="w-4 h-4 mr-2" />
          New Campaign
        </Link>
      </div>

      {isLoading ? (
        <div className="flex justify-center items-center py-20">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {campaigns?.map((campaign: any) => (
            <Link 
              key={campaign.id} 
              to={`/campaign/${campaign.id}`}
              className="glass p-6 rounded-xl border border-white/10 hover:border-primary/50 transition group"
            >
              <div className="flex justify-between items-start mb-4">
                <div className={`px-2 py-1 rounded text-xs font-medium uppercase tracking-wider ${
                  campaign.status === 'completed' ? 'bg-green-500/20 text-green-400' : 
                  campaign.status === 'failed' ? 'bg-red-500/20 text-red-400' :
                  'bg-blue-500/20 text-blue-400 animate-pulse'
                }`}>
                  {campaign.status.replace('_', ' ')}
                </div>
              </div>
              
              <div className="space-y-3">
                {campaign.website_url && (
                  <div className="flex items-center text-sm text-white/80">
                    <Globe className="w-4 h-4 mr-2 opacity-50" />
                    <span className="truncate">{campaign.website_url}</span>
                  </div>
                )}
                {campaign.campaign_goal && (
                  <div className="flex items-center text-sm text-white/80">
                    <Target className="w-4 h-4 mr-2 opacity-50" />
                    <span className="capitalize">{campaign.campaign_goal.replace('_', ' ')}</span>
                  </div>
                )}
                <div className="flex items-center text-xs text-muted-foreground pt-4 border-t border-white/10">
                  <Calendar className="w-3 h-3 mr-1" />
                  {new Date(campaign.created_at).toLocaleDateString()}
                </div>
              </div>
            </Link>
          ))}

          {(!campaigns || campaigns.length === 0) && (
            <div className="col-span-full text-center py-20 glass rounded-xl border border-white/5">
              <p className="text-muted-foreground">No campaigns found. Start by generating one!</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
