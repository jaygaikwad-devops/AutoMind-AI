import { createFileRoute, Link } from '@tanstack/react-router';
import { useState } from 'react';
import { Loader2 } from 'lucide-react';
import { API_URL } from '../lib/api';

export const Route = createFileRoute('/register')({
  component: RegisterPage,
});

function RegisterPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const res = await fetch(`${API_URL}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ email, password }),
      });

      if (!res.ok) {
        let errorMsg = 'Failed to register';
        const contentType = res.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
          const data = await res.json();
          errorMsg = data.detail || errorMsg;
        } else {
          errorMsg = `Server error: ${res.status} ${res.statusText}`;
        }
        throw new Error(errorMsg);
      }

      // Redirect to studio on success (auto-logged in)
      window.location.href = '/studio';
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-md glass-strong p-8 rounded-2xl relative overflow-hidden">
        <div className="absolute -top-24 -right-24 w-48 h-48 bg-[var(--neon-cyan)] rounded-full blur-[80px] opacity-30 pointer-events-none" />
        <div className="absolute -bottom-24 -left-24 w-48 h-48 bg-[var(--neon-violet)] rounded-full blur-[80px] opacity-30 pointer-events-none" />
        
        <div className="relative z-10">
          <h1 className="text-3xl font-display font-bold text-center mb-2">Create Account</h1>
          <p className="text-center text-muted-foreground mb-8">Join AutoMind AI</p>

          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="p-3 rounded-lg bg-red-500/20 text-red-200 text-sm border border-red-500/30">
                {error}
              </div>
            )}
            
            <div className="space-y-2">
              <label className="text-sm font-medium text-muted-foreground">Email Address</label>
              <input
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                required
                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-[var(--neon-cyan)] transition"
                placeholder="you@example.com"
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-muted-foreground">Password</label>
              <input
                type="password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                required
                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-[var(--neon-cyan)] transition"
                placeholder="••••••••"
                minLength={6}
              />
            </div>

            <button
              type="submit"
              disabled={loading || !email || !password}
              className="w-full bg-gradient-to-r from-[var(--neon-cyan)] to-[var(--neon-violet)] text-background font-semibold px-6 py-2.5 rounded-xl flex items-center justify-center gap-2 hover:opacity-90 disabled:opacity-50 transition mt-6"
            >
              {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Create Account'}
            </button>
          </form>

          <div className="mt-6 text-center text-sm text-muted-foreground">
            Already have an account?{' '}
            <Link to="/login" className="text-white hover:text-[var(--neon-violet)] transition font-medium">
              Sign In
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
