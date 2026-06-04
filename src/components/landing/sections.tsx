import { motion } from "motion/react";
import {
  Sparkles, Play, ArrowRight, Bot, Video, Send, TrendingUp,
  Instagram, Facebook, Linkedin, Youtube, Music2, Megaphone,
  Wand2, Mic, Flame, Users, Target, Layers, BarChart3, LineChart,
  Workflow, Brain, Zap, Network, Activity, ShieldCheck, Globe,
  Server, Database, Container, Boxes, Check, Star, Github, MessageCircle,
  Twitter, Plus, Minus, ChevronRight, CircleDot, Image as ImageIcon,
} from "lucide-react";
import { useState } from "react";

// ---------------- NAV ----------------
export function Nav() {
  return (
    <header className="fixed top-4 left-1/2 z-50 w-[min(1100px,calc(100%-2rem))] -translate-x-1/2">
      <div className="glass-strong flex items-center justify-between rounded-full px-5 py-2.5">
        <a href="#" className="flex items-center gap-2 font-display text-base font-bold">
          <span className="grid h-7 w-7 place-items-center rounded-lg bg-gradient-to-br from-[var(--neon-violet)] to-[var(--neon-cyan)] text-background">
            <Brain className="h-4 w-4" strokeWidth={2.5} />
          </span>
          <span>AutoMindai<span className="text-neon">.info</span></span>
        </a>
        <nav className="hidden items-center gap-7 text-sm text-muted-foreground md:flex">
          <a href="#features" className="hover:text-foreground transition">Features</a>
          <a href="#automation" className="hover:text-foreground transition">Automation</a>
          <a href="#agents" className="hover:text-foreground transition">Agents</a>
          <a href="#pricing" className="hover:text-foreground transition">Pricing</a>
          <a href="#docs" className="hover:text-foreground transition">Docs</a>
        </nav>
        <div className="flex items-center gap-2">
          <a href="/login" className="hidden text-sm text-muted-foreground hover:text-foreground sm:block">Sign in</a>
          <a href="/agents" className="group relative inline-flex items-center gap-1.5 overflow-hidden rounded-full bg-foreground px-4 py-2 text-sm font-medium text-background transition hover:opacity-90">
            Start free <ArrowRight className="h-3.5 w-3.5 transition group-hover:translate-x-0.5" />
          </a>
        </div>
      </div>
    </header>
  );
}

// ---------------- HERO ----------------
export function Hero() {
  return (
    <section className="relative px-4 pt-36 pb-24 md:pt-44 md:pb-32">
      <div className="mx-auto max-w-6xl text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mx-auto mb-6 inline-flex items-center gap-2 rounded-full glass px-4 py-1.5 text-xs">
          <span className="relative flex h-1.5 w-1.5">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-[var(--neon-lime)] opacity-75" />
            <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-[var(--neon-lime)]" />
          </span>
          <span className="text-muted-foreground">v3.0 launching</span>
          <span className="mx-1 h-3 w-px bg-border" />
          <span>Autonomous Agents are live</span>
          <ArrowRight className="h-3 w-3" />
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.1 }}
          className="font-display text-5xl font-bold leading-[1.05] tracking-tight sm:text-6xl md:text-7xl lg:text-[88px]">
          Your Autonomous<br />
          <span className="text-gradient">AI Marketing Team.</span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.25 }}
          className="mx-auto mt-6 max-w-2xl text-base text-muted-foreground md:text-lg">
          Generate AI videos, automate social media, launch campaigns, orchestrate AI agents,
          and scale your marketing — <span className="text-foreground">automatically</span>.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.4 }}
          className="mt-10 flex flex-wrap items-center justify-center gap-3">
          <a href="/agents" className="group relative inline-flex items-center gap-2 overflow-hidden rounded-full bg-gradient-to-r from-[var(--neon-violet)] via-[var(--neon-pink)] to-[var(--neon-cyan)] px-6 py-3 text-sm font-semibold text-background shadow-[0_0_40px_-5px_oklch(0.72_0.25_295_/_0.6)] transition hover:scale-[1.02]">
            <Sparkles className="h-4 w-4" /> Start Building
            <ArrowRight className="h-4 w-4 transition group-hover:translate-x-0.5" />
          </a>
          <a href="#" className="group inline-flex items-center gap-2 rounded-full glass px-6 py-3 text-sm font-medium transition hover:bg-white/5">
            <Play className="h-4 w-4" /> Watch Demo
          </a>
        </motion.div>

        <p className="mt-6 text-xs text-muted-foreground">No credit card · Free 14-day trial · Cancel anytime</p>
      </div>

      <HeroMockup />
    </section>
  );
}

function HeroMockup() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 60 }} animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 1, delay: 0.5 }}
      className="relative mx-auto mt-20 max-w-6xl">
      <div className="absolute -inset-20 -z-10 opacity-70" style={{ background: "radial-gradient(ellipse at center, oklch(0.72 0.25 295 / 0.35), transparent 60%)", filter: "blur(60px)" }} />

      <div className="glass-strong overflow-hidden rounded-3xl p-2 shadow-[0_50px_120px_-30px_oklch(0_0_0_/_0.8)]">
        <div className="rounded-[1.3rem] bg-background/60 p-4 md:p-6">
          {/* Top bar */}
          <div className="flex items-center justify-between border-b border-border pb-3">
            <div className="flex items-center gap-1.5">
              <span className="h-2.5 w-2.5 rounded-full bg-red-500/60" />
              <span className="h-2.5 w-2.5 rounded-full bg-yellow-500/60" />
              <span className="h-2.5 w-2.5 rounded-full bg-green-500/60" />
              <span className="ml-3 text-xs text-muted-foreground">automindai.info / studio</span>
            </div>
            <div className="hidden gap-2 sm:flex">
              <span className="rounded-md bg-white/5 px-2 py-1 text-[10px] text-muted-foreground">⌘K</span>
            </div>
          </div>

          {/* Dashboard grid */}
          <div className="mt-4 grid grid-cols-12 gap-3">
            {/* Sidebar */}
            <aside className="col-span-2 hidden flex-col gap-1 rounded-xl bg-white/[0.02] p-2 md:flex">
              {[
                { i: Sparkles, l: "Studio", a: true },
                { i: Video, l: "Videos" },
                { i: Send, l: "Publish" },
                { i: Bot, l: "Agents" },
                { i: BarChart3, l: "Analytics" },
                { i: Workflow, l: "Flows" },
              ].map((it) => (
                <div key={it.l} className={`flex items-center gap-2 rounded-lg px-2 py-1.5 text-xs transition ${it.a ? "bg-white/10 text-foreground" : "text-muted-foreground hover:bg-white/5"}`}>
                  <it.i className="h-3.5 w-3.5" />{it.l}
                </div>
              ))}
            </aside>

            {/* Main area */}
            <div className="col-span-12 grid grid-cols-6 gap-3 md:col-span-10">
              {/* Video gen card */}
              <div className="col-span-6 rounded-xl glass p-4 md:col-span-3">
                <div className="mb-2 flex items-center justify-between">
                  <span className="text-xs font-medium">AI Video Generation</span>
                  <span className="rounded-full bg-[var(--neon-violet)]/20 px-2 py-0.5 text-[10px] text-[var(--neon-violet)]">Rendering 68%</span>
                </div>
                <div className="relative aspect-video overflow-hidden rounded-lg bg-gradient-to-br from-[var(--neon-violet)]/40 via-[var(--neon-pink)]/30 to-[var(--neon-cyan)]/40">
                  <motion.div animate={{ opacity: [0.4, 1, 0.4] }} transition={{ duration: 2.5, repeat: Infinity }} className="absolute inset-0 bg-[radial-gradient(circle_at_30%_30%,white_0%,transparent_40%)]" />
                  <div className="absolute bottom-2 left-2 rounded-md bg-black/40 px-2 py-1 text-[10px] backdrop-blur-md">"Launch reel · 9:16 · 4K"</div>
                </div>
                <div className="mt-3 h-1 overflow-hidden rounded-full bg-white/5">
                  <motion.div className="h-full bg-gradient-to-r from-[var(--neon-violet)] to-[var(--neon-cyan)]"
                    initial={{ width: "10%" }} animate={{ width: "68%" }} transition={{ duration: 3, repeat: Infinity, repeatType: "reverse" }} />
                </div>
              </div>

              {/* Agents */}
              <div className="col-span-6 rounded-xl glass p-4 md:col-span-3">
                <div className="mb-2 flex items-center justify-between">
                  <span className="text-xs font-medium">AI Agents</span>
                  <span className="text-[10px] text-muted-foreground">6 active</span>
                </div>
                <div className="grid grid-cols-3 gap-2">
                  {[
                    { i: Video, c: "var(--neon-violet)" },
                    { i: Wand2, c: "var(--neon-cyan)" },
                    { i: BarChart3, c: "var(--neon-pink)" },
                    { i: Send, c: "var(--neon-lime)" },
                    { i: Target, c: "var(--neon-violet)" },
                    { i: Megaphone, c: "var(--neon-cyan)" },
                  ].map((a, i) => (
                    <motion.div key={i}
                      animate={{ y: [0, -3, 0] }} transition={{ duration: 2 + i * 0.3, repeat: Infinity }}
                      className="grid aspect-square place-items-center rounded-lg bg-white/[0.03]"
                      style={{ boxShadow: `inset 0 0 20px -5px ${a.c}` }}>
                      <a.i className="h-4 w-4" style={{ color: a.c }} />
                    </motion.div>
                  ))}
                </div>
              </div>

              {/* Stats */}
              {[
                { l: "Posts today", v: "1,284", c: "var(--neon-violet)" },
                { l: "Leads", v: "+932", c: "var(--neon-cyan)" },
                { l: "Viral score", v: "92.4", c: "var(--neon-pink)" },
              ].map((s) => (
                <div key={s.l} className="col-span-2 rounded-xl glass p-3">
                  <div className="text-[10px] text-muted-foreground">{s.l}</div>
                  <div className="mt-1 font-display text-xl font-bold" style={{ color: s.c }}>{s.v}</div>
                </div>
              ))}

              {/* Chart */}
              <div className="col-span-6 rounded-xl glass p-4">
                <div className="mb-2 flex items-center justify-between">
                  <span className="text-xs font-medium">Realtime engagement</span>
                  <span className="flex items-center gap-1 text-[10px] text-[var(--neon-lime)]"><Activity className="h-3 w-3" /> live</span>
                </div>
                <MiniChart />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Floating notif cards */}
      <motion.div
        animate={{ y: [0, -10, 0] }} transition={{ duration: 4, repeat: Infinity }}
        className="absolute -left-4 top-1/3 hidden glass-strong rounded-2xl p-3 shadow-xl md:flex md:items-center md:gap-2">
        <span className="grid h-8 w-8 place-items-center rounded-lg bg-[var(--neon-lime)]/20 text-[var(--neon-lime)]"><Check className="h-4 w-4" /></span>
        <div className="text-xs">
          <div className="font-medium">Post published</div>
          <div className="text-muted-foreground">Instagram · 2.3k views</div>
        </div>
      </motion.div>
      <motion.div
        animate={{ y: [0, 10, 0] }} transition={{ duration: 5, repeat: Infinity }}
        className="absolute -right-4 top-1/2 hidden glass-strong rounded-2xl p-3 shadow-xl md:flex md:items-center md:gap-2">
        <span className="grid h-8 w-8 place-items-center rounded-lg bg-[var(--neon-pink)]/20 text-[var(--neon-pink)]"><TrendingUp className="h-4 w-4" /></span>
        <div className="text-xs">
          <div className="font-medium">Campaign optimized</div>
          <div className="text-muted-foreground">+38% CTR uplift</div>
        </div>
      </motion.div>
    </motion.div>
  );
}

function MiniChart() {
  const pts = [10, 22, 18, 32, 28, 44, 38, 56, 50, 68, 62, 80, 72, 88];
  const max = 90;
  const w = 600, h = 80;
  const step = w / (pts.length - 1);
  const path = pts.map((p, i) => `${i === 0 ? "M" : "L"} ${i * step} ${h - (p / max) * h}`).join(" ");
  const area = `${path} L ${w} ${h} L 0 ${h} Z`;
  return (
    <svg viewBox={`0 0 ${w} ${h}`} className="h-20 w-full">
      <defs>
        <linearGradient id="g1" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stopColor="oklch(0.72 0.25 295)" stopOpacity="0.5" />
          <stop offset="100%" stopColor="oklch(0.72 0.25 295)" stopOpacity="0" />
        </linearGradient>
      </defs>
      <path d={area} fill="url(#g1)" />
      <path d={path} fill="none" stroke="oklch(0.82 0.18 200)" strokeWidth="2" />
    </svg>
  );
}

// ---------------- LOGO MARQUEE ----------------
export function LogoMarquee() {
  const logos = ["LINEAR", "VERCEL", "RAYCAST", "NOTION", "ARC", "FRAMER", "STRIPE", "FIGMA"];
  return (
    <section className="border-y border-border/50 py-10">
      <p className="mb-6 text-center text-xs uppercase tracking-[0.3em] text-muted-foreground">Trusted by teams at the future of work</p>
      <div className="no-scrollbar overflow-hidden">
        <div className="flex w-max gap-16 px-8" style={{ animation: "marquee 30s linear infinite" }}>
          {[...logos, ...logos].map((l, i) => (
            <span key={i} className="font-display text-2xl font-bold text-muted-foreground/60 tracking-tight">{l}</span>
          ))}
        </div>
      </div>
    </section>
  );
}

// ---------------- SOCIAL AUTOMATION ----------------
export function SocialAutomation() {
  const platforms = [
    { i: Instagram, name: "Instagram", c: "#E1306C" },
    { i: Facebook, name: "Facebook", c: "#1877F2" },
    { i: Linkedin, name: "LinkedIn", c: "#0A66C2" },
    { i: Music2, name: "TikTok", c: "#FF0050" },
    { i: Youtube, name: "YouTube", c: "#FF0000" },
    { i: Megaphone, name: "Meta Ads", c: "#0866FF" },
  ];
  const steps = [
    { i: Video, t: "Generate AI Video", d: "Cinematic 4K reels in seconds" },
    { i: Wand2, t: "Smart Captions", d: "On-brand copy for every platform" },
    { i: Flame, t: "Viral Hashtags", d: "AI-optimized for max reach" },
    { i: Send, t: "Auto Publish", d: "Across every channel, on schedule" },
  ];
  return (
    <SectionWrap id="automation" eyebrow="Social Automation" title={<>One workflow. <span className="text-gradient">Every platform.</span></>} sub="Generate a video, and AutoMind handles captions, hashtags, scheduling, ads, and lead capture across every channel — autonomously.">
      <div className="mt-14 grid gap-4 lg:grid-cols-5">
        {/* Pipeline */}
        <div className="lg:col-span-3 glass-strong rounded-3xl p-6 md:p-8 noise">
          <div className="mb-6 flex items-center justify-between">
            <span className="text-sm font-medium">Publishing pipeline</span>
            <span className="inline-flex items-center gap-1.5 text-xs text-[var(--neon-lime)]">
              <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-[var(--neon-lime)]" /> Running
            </span>
          </div>
          <div className="space-y-3">
            {steps.map((s, i) => (
              <motion.div key={s.t}
                initial={{ opacity: 0, x: -20 }} whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }} transition={{ delay: i * 0.1 }}
                className="group flex items-center gap-4 rounded-2xl bg-white/[0.03] p-4 transition hover:bg-white/[0.06]">
                <span className="grid h-10 w-10 place-items-center rounded-xl bg-gradient-to-br from-[var(--neon-violet)]/30 to-[var(--neon-cyan)]/30 text-foreground">
                  <s.i className="h-4 w-4" />
                </span>
                <div className="flex-1">
                  <div className="text-sm font-medium">{s.t}</div>
                  <div className="text-xs text-muted-foreground">{s.d}</div>
                </div>
                <span className="text-xs text-[var(--neon-lime)]"><Check className="h-4 w-4" /></span>
              </motion.div>
            ))}
          </div>

          <div className="mt-6 flex flex-wrap gap-2">
            {platforms.map((p) => (
              <div key={p.name} className="flex items-center gap-2 rounded-full bg-white/[0.04] px-3 py-1.5 text-xs">
                <p.i className="h-3.5 w-3.5" style={{ color: p.c }} />
                {p.name}
              </div>
            ))}
          </div>
        </div>

        {/* Live cards */}
        <div className="space-y-3 lg:col-span-2">
          {[
            { i: Check, t: "Post Published Successfully", d: "Reel · Instagram + TikTok · 12.4k impressions", c: "var(--neon-lime)" },
            { i: Users, t: "327 Leads Generated", d: "Captured via AI lead funnel · last 24h", c: "var(--neon-cyan)" },
            { i: TrendingUp, t: "AI Optimized Campaign Running", d: "Meta Ads · ROAS 4.8x · auto-bidding", c: "var(--neon-pink)" },
            { i: Flame, t: "Viral score 94 · trending", d: "Video #4781 surging on TikTok", c: "var(--neon-violet)" },
          ].map((c) => (
            <div key={c.t} className="glass rounded-2xl p-4 transition hover:translate-x-1">
              <div className="flex items-start gap-3">
                <span className="grid h-9 w-9 place-items-center rounded-xl" style={{ background: `${c.c}20`, color: c.c }}>
                  <c.i className="h-4 w-4" />
                </span>
                <div>
                  <div className="text-sm font-medium">{c.t}</div>
                  <div className="text-xs text-muted-foreground">{c.d}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </SectionWrap>
  );
}

// ---------------- FEATURES ----------------
export function Features() {
  const items = [
    { i: Video, t: "AI Video Generation", d: "Text-to-video reels in 4K.", href: "/studio" },
    { i: Flame, t: "AI Reel Generator", d: "Trend-aware short-form." },
    { i: ImageIcon, t: "AI Ad Creative", d: "On-brand creatives, A/B tested." },
    { i: Send, t: "Autonomous Posting", d: "Cross-platform schedules." },
    { i: Workflow, t: "Agent Workflows", d: "Chain agents like LEGO." },
    { i: Layers, t: "AI Content Studio", d: "Posts, blogs, scripts, threads." },
    { i: Wand2, t: "Caption Generator", d: "Native to every platform." },
    { i: Mic, t: "AI Voice Automation", d: "Cloned, multilingual voices." },
    { i: TrendingUp, t: "Viral Content Engine", d: "Predicts hits before posting." },
    { i: Users, t: "AI Lead Generation", d: "Smart funnels, zero spam." },
    { i: Megaphone, t: "Campaign Automation", d: "Self-tuning ad spend." },
    { i: Globe, t: "Multi-platform Publishing", d: "10+ networks, one click." },
    { i: LineChart, t: "Realtime Analytics", d: "Sub-second telemetry." },
    { i: Activity, t: "AI Trend Analyzer", d: "Spot waves before they break." },
    { i: Zap, t: "Marketing Pipelines", d: "Drag, drop, deploy." },
  ];
  return (
    <SectionWrap id="features" eyebrow="Features" title={<>The full <span className="text-gradient">marketing stack</span>, on autopilot.</>}
      sub="Every workflow your team runs manually — automated by AI agents that learn your brand.">
      <div className="mt-14 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {items.map((it, i) => (
          <motion.div key={it.t}
            onClick={() => { if (it.href) window.location.href = it.href; }}
            initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-50px" }} transition={{ delay: (i % 6) * 0.05 }}
            className={`group relative overflow-hidden rounded-2xl glass p-5 transition hover:-translate-y-1 hover:bg-white/[0.06] ${it.href ? 'cursor-pointer' : ''}`}>
            <div className="pointer-events-none absolute -right-10 -top-10 h-32 w-32 rounded-full opacity-0 transition group-hover:opacity-100"
                 style={{ background: "radial-gradient(circle, oklch(0.72 0.25 295 / 0.4), transparent 60%)", filter: "blur(20px)" }} />
            <span className="mb-4 grid h-10 w-10 place-items-center rounded-xl bg-gradient-to-br from-[var(--neon-violet)]/30 to-[var(--neon-cyan)]/30">
              <it.i className="h-[18px] w-[18px]" />
            </span>
            <h3 className="font-display text-base font-semibold">{it.t}</h3>
            <p className="mt-1 text-sm text-muted-foreground">{it.d}</p>
          </motion.div>
        ))}
      </div>
    </SectionWrap>
  );
}

// ---------------- AGENT NETWORK ----------------
export function AgentNetwork() {
  const agents = [
    { i: Video, name: "Video Agent", angle: 0, c: "var(--neon-violet)" },
    { i: Wand2, name: "Content Agent", angle: 60, c: "var(--neon-cyan)" },
    { i: BarChart3, name: "Analytics Agent", angle: 120, c: "var(--neon-pink)" },
    { i: Send, name: "Publishing Agent", angle: 180, c: "var(--neon-lime)" },
    { i: Target, name: "Lead Gen Agent", angle: 240, c: "var(--neon-violet)" },
    { i: Megaphone, name: "Ad Ops Agent", angle: 300, c: "var(--neon-cyan)" },
  ];
  return (
    <SectionWrap id="agents" eyebrow="AI Agent Network" title={<>Six agents. <span className="text-gradient">One mission.</span></>}
      sub="Specialized AI agents collaborate in real time — each owning a part of your funnel, all talking to each other.">
      <div className="mt-14 grid items-center gap-10 lg:grid-cols-5">
        <div className="relative mx-auto aspect-square w-full max-w-[480px] lg:col-span-3">
          <div className="absolute inset-0 rounded-full" style={{ background: "radial-gradient(circle, oklch(0.72 0.25 295 / 0.25), transparent 70%)", filter: "blur(40px)" }} />
          {[1, 2, 3].map((r) => (
            <div key={r} className="absolute inset-0 m-auto rounded-full border border-white/5" style={{ width: `${r * 33}%`, height: `${r * 33}%` }} />
          ))}
          {/* Center */}
          <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">
            <div className="relative grid h-20 w-20 place-items-center rounded-2xl glass-strong">
              <Brain className="h-8 w-8 text-foreground" />
              <span className="absolute inset-0 rounded-2xl" style={{ boxShadow: "0 0 60px oklch(0.72 0.25 295 / 0.6)" }} />
            </div>
          </div>
          {/* Orbiting */}
          {agents.map((a, i) => {
            const rad = (a.angle * Math.PI) / 180;
            const r = 180;
            const x = Math.cos(rad) * r;
            const y = Math.sin(rad) * r;
            return (
              <motion.div key={a.name}
                animate={{ y: [y, y - 8, y] }} transition={{ duration: 3 + i * 0.4, repeat: Infinity }}
                className="absolute left-1/2 top-1/2"
                style={{ transform: `translate(calc(-50% + ${x}px), calc(-50% + ${y}px))` }}>
                <div className="flex flex-col items-center gap-1.5">
                  <div className="grid h-12 w-12 place-items-center rounded-xl glass-strong" style={{ boxShadow: `0 0 30px -5px ${a.c}` }}>
                    <a.i className="h-5 w-5" style={{ color: a.c }} />
                  </div>
                  <span className="rounded-full bg-black/40 px-2 py-0.5 text-[10px] backdrop-blur">{a.name}</span>
                </div>
              </motion.div>
            );
          })}
          {/* Connections */}
          <svg className="absolute inset-0 h-full w-full" viewBox="-250 -250 500 500">
            {agents.map((a, i) => {
              const rad = (a.angle * Math.PI) / 180;
              const x = Math.cos(rad) * 180;
              const y = Math.sin(rad) * 180;
              return <line key={i} x1="0" y1="0" x2={x} y2={y} stroke="oklch(0.72 0.25 295 / 0.25)" strokeWidth="1" strokeDasharray="3 4" />;
            })}
          </svg>
        </div>

        <div className="space-y-3 lg:col-span-2">
          {agents.map((a) => (
            <div key={a.name} className="flex items-center gap-3 rounded-2xl glass p-4">
              <span className="grid h-10 w-10 place-items-center rounded-xl" style={{ background: `${a.c}20`, color: a.c }}>
                <a.i className="h-4 w-4" />
              </span>
              <div className="flex-1">
                <div className="text-sm font-medium">{a.name}</div>
                <div className="text-xs text-muted-foreground">Autonomous · self-healing · 24/7</div>
              </div>
              <CircleDot className="h-4 w-4 text-[var(--neon-lime)]" />
            </div>
          ))}
          <div className="pt-4">
            <a href="/agents" className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-white/10 px-4 py-3 text-sm font-medium transition hover:bg-white/20">
              Access the Agent Hub <ArrowRight className="h-4 w-4" />
            </a>
          </div>
        </div>
      </div>
    </SectionWrap>
  );
}

// ---------------- WORKFLOW BUILDER ----------------
export function WorkflowBuilder() {
  return (
    <SectionWrap id="workflows" eyebrow="Workflow Builder" title={<>Drag, drop, <span className="text-gradient">deploy.</span></>}
      sub="A visual canvas inspired by n8n, Zapier, and Make — purpose-built for AI marketing pipelines.">
      <div className="relative mt-14 overflow-hidden rounded-3xl glass-strong p-6 md:p-10">
        <div className="absolute inset-0 grid-bg opacity-30" />
        <div className="relative grid gap-6 md:grid-cols-4">
          {[
            { i: Zap, t: "Trigger", d: "New lead", c: "var(--neon-lime)" },
            { i: Video, t: "AI Video", d: "Generate reel", c: "var(--neon-violet)" },
            { i: Wand2, t: "Caption", d: "Multi-language", c: "var(--neon-cyan)" },
            { i: Send, t: "Publish", d: "5 platforms", c: "var(--neon-pink)" },
          ].map((n, i) => (
            <div key={n.t} className="relative">
              <div className="glass-strong rounded-2xl p-4">
                <div className="flex items-center gap-2">
                  <span className="grid h-8 w-8 place-items-center rounded-lg" style={{ background: `${n.c}20`, color: n.c }}>
                    <n.i className="h-4 w-4" />
                  </span>
                  <div>
                    <div className="text-xs uppercase tracking-wider text-muted-foreground">{n.t}</div>
                    <div className="text-sm font-medium">{n.d}</div>
                  </div>
                </div>
                <div className="mt-3 h-1.5 rounded-full bg-white/5">
                  <motion.div className="h-full rounded-full"
                    style={{ background: n.c }}
                    initial={{ width: 0 }} whileInView={{ width: "100%" }}
                    viewport={{ once: true }}
                    transition={{ duration: 1.2, delay: i * 0.2 }} />
                </div>
              </div>
              {i < 3 && (
                <ChevronRight className="absolute top-1/2 -right-3 hidden -translate-y-1/2 text-muted-foreground md:block" />
              )}
            </div>
          ))}
        </div>
      </div>
    </SectionWrap>
  );
}

// ---------------- INFRASTRUCTURE ----------------
export function Infrastructure() {
  const nodes = [
    { i: Globe, t: "Frontend", d: "Next.js · Vercel edge" },
    { i: Server, t: "API Gateway", d: "FastAPI · WebSocket" },
    { i: Database, t: "PostgreSQL", d: "Primary + replicas" },
    { i: Boxes, t: "Redis Queue", d: "Realtime + jobs" },
    { i: Bot, t: "AI Workers", d: "GPU autoscaling" },
    { i: Video, t: "Render Farm", d: "Distributed FFmpeg" },
    { i: Container, t: "Docker", d: "Containerized" },
    { i: ShieldCheck, t: "K8s / ECS", d: "Production-ready" },
  ];
  return (
    <SectionWrap eyebrow="Infrastructure" title={<>Built for <span className="text-gradient">enterprise scale.</span></>}
      sub="A modular, container-first architecture that scales from zero to billions of events.">
      <div className="mt-14 grid grid-cols-2 gap-3 md:grid-cols-4">
        {nodes.map((n, i) => (
          <motion.div key={n.t}
            initial={{ opacity: 0, scale: 0.95 }} whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }} transition={{ delay: i * 0.05 }}
            className="glass rounded-2xl p-5 text-center">
            <span className="mx-auto mb-3 grid h-10 w-10 place-items-center rounded-xl bg-gradient-to-br from-[var(--neon-violet)]/20 to-[var(--neon-cyan)]/20">
              <n.i className="h-[18px] w-[18px]" />
            </span>
            <div className="text-sm font-semibold">{n.t}</div>
            <div className="mt-0.5 text-xs text-muted-foreground">{n.d}</div>
          </motion.div>
        ))}
      </div>
    </SectionWrap>
  );
}

// ---------------- PRICING ----------------
export function Pricing() {
  const tiers = [
    { name: "Starter", price: "60", tag: "For solo founders", feats: ["500 Marketing Credits", "10 Standard Videos", "100 AI Generations", "10 Ad Campaigns"], featured: false },
    { name: "Growth", price: "120", tag: "Most popular", feats: ["2,000 Marketing Credits", "40 Standard Videos", "500 AI Generations", "50 Ad Campaigns"], featured: true },
    { name: "Agency", price: "180", tag: "For teams & studios", feats: ["5,000 Marketing Credits", "100 Standard Videos", "Multi-client Workspaces", "White-label Options"], featured: false },
  ];
  return (
    <SectionWrap id="pricing" eyebrow="Pricing" title={<>Simple plans. <span className="text-gradient">Insane value.</span></>}
      sub="Start free. Scale as your AI team works around the clock.">
      <div className="mt-14 grid gap-6 lg:grid-cols-3">
        {tiers.map((t) => (
          <div key={t.name} className={`relative rounded-3xl p-px ${t.featured ? "shimmer-border" : ""}`}>
            <div className={`relative h-full rounded-3xl p-7 ${t.featured ? "glass-strong" : "glass"}`}>
              {t.featured && (
                <span className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-gradient-to-r from-[var(--neon-violet)] to-[var(--neon-cyan)] px-3 py-1 text-[10px] font-bold uppercase tracking-wider text-background">
                  Recommended
                </span>
              )}
              <div className="text-xs uppercase tracking-[0.2em] text-muted-foreground">{t.name}</div>
              <div className="mt-1 text-xs text-muted-foreground">{t.tag}</div>
              <div className="mt-4 flex items-baseline gap-1">
                <span className="font-display text-5xl font-bold">{t.price} USDT</span>
                <span className="text-sm text-muted-foreground">/mo</span>
              </div>
              <ul className="mt-6 space-y-2.5 text-sm">
                {t.feats.map((f) => (
                  <li key={f} className="flex items-start gap-2">
                    <Check className="mt-0.5 h-4 w-4 text-[var(--neon-lime)]" />
                    <span className="text-muted-foreground">{f}</span>
                  </li>
                ))}
              </ul>
              <a href="#" className={`mt-7 inline-flex w-full items-center justify-center rounded-full px-5 py-3 text-sm font-semibold transition ${t.featured ? "bg-gradient-to-r from-[var(--neon-violet)] to-[var(--neon-cyan)] text-background hover:opacity-90" : "glass hover:bg-white/10"}`}>
                Start with {t.name}
              </a>
            </div>
          </div>
        ))}
      </div>
    </SectionWrap>
  );
}

// ---------------- TESTIMONIALS ----------------
export function Testimonials() {
  const items = [
    { q: "AutoMind replaced an entire 12-person content team. Our reach 4x'd in 60 days.", a: "Maya Chen", r: "Founder · Halo Labs" },
    { q: "The agent network is uncanny. It posts better than I do, at 3am.", a: "Dev Patel", r: "CMO · Sunday Studio" },
    { q: "We went from 4 reels a week to 80. Same team. Same budget.", a: "Lina Ortega", r: "Head of Growth · Pulse" },
    { q: "The viral score is scary accurate. We've stopped guessing.", a: "Noah Kim", r: "Creator · 2.1M followers" },
    { q: "Best AI product I've used since GPT-4. Period.", a: "Sasha Wolf", r: "VP Marketing · NorthFront" },
    { q: "The workflow builder is dangerously fun. Shipped 14 funnels in a weekend.", a: "Ravi Mehta", r: "Indie hacker" },
  ];
  return (
    <SectionWrap eyebrow="Loved by builders" title={<>Founders are <span className="text-gradient">shipping faster</span> with AutoMind.</>}>
      <div className="mt-12 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {items.map((t, i) => (
          <motion.figure key={i}
            initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }} transition={{ delay: (i % 3) * 0.08 }}
            className="glass rounded-2xl p-6">
            <div className="mb-3 flex gap-0.5">
              {[...Array(5)].map((_, k) => <Star key={k} className="h-3.5 w-3.5 fill-[var(--neon-lime)] text-[var(--neon-lime)]" />)}
            </div>
            <blockquote className="text-sm leading-relaxed">"{t.q}"</blockquote>
            <figcaption className="mt-4 flex items-center gap-3">
              <div className="grid h-9 w-9 place-items-center rounded-full bg-gradient-to-br from-[var(--neon-violet)] to-[var(--neon-cyan)] text-xs font-bold text-background">
                {t.a.split(" ").map(n => n[0]).join("")}
              </div>
              <div>
                <div className="text-sm font-medium">{t.a}</div>
                <div className="text-xs text-muted-foreground">{t.r}</div>
              </div>
            </figcaption>
          </motion.figure>
        ))}
      </div>
    </SectionWrap>
  );
}

// ---------------- FAQ ----------------
export function FAQ() {
  const qs = [
    { q: "What makes AutoMind different from ChatGPT or Midjourney?", a: "AutoMind isn't a tool — it's an autonomous team. Six specialized agents handle generation, publishing, analytics, ads, and lead gen in coordination, 24/7." },
    { q: "Which social platforms do you support?", a: "Instagram, Facebook, LinkedIn, TikTok, YouTube Shorts, X, Pinterest, Threads, and Meta Ads — with more coming monthly." },
    { q: "Can I bring my own AI models?", a: "Yes. On Agency you can plug in your own OpenAI, Anthropic, Replicate, or self-hosted models per agent." },
    { q: "Is my data private?", a: "Always. We never train on your content, SOC 2 in progress, and all data is encrypted at rest with regional residency options." },
    { q: "Do you support white-label?", a: "Agency plan includes full white-label, custom domain, and API access for embedding into your own product." },
    { q: "What about deliverability and platform compliance?", a: "Our publishing layer respects every platform's official API limits, with smart queueing and shadow-ban detection built in." },
  ];
  const [open, setOpen] = useState<number | null>(0);
  return (
    <SectionWrap eyebrow="FAQ" title={<>Questions, <span className="text-gradient">answered.</span></>}>
      <div className="mx-auto mt-12 max-w-3xl space-y-2">
        {qs.map((it, i) => {
          const o = open === i;
          return (
            <div key={i} className="glass rounded-2xl">
              <button onClick={() => setOpen(o ? null : i)} className="flex w-full items-center justify-between gap-4 p-5 text-left">
                <span className="text-sm font-medium">{it.q}</span>
                <span className="grid h-7 w-7 shrink-0 place-items-center rounded-full bg-white/5">
                  {o ? <Minus className="h-3.5 w-3.5" /> : <Plus className="h-3.5 w-3.5" />}
                </span>
              </button>
              <motion.div
                initial={false} animate={{ height: o ? "auto" : 0, opacity: o ? 1 : 0 }}
                transition={{ duration: 0.3 }} className="overflow-hidden">
                <p className="px-5 pb-5 text-sm text-muted-foreground">{it.a}</p>
              </motion.div>
            </div>
          );
        })}
      </div>
    </SectionWrap>
  );
}

// ---------------- CTA ----------------
export function CTA() {
  return (
    <section className="relative px-4 py-32">
      <div className="relative mx-auto max-w-5xl overflow-hidden rounded-[2rem] glass-strong p-12 text-center md:p-20">
        <div className="absolute inset-0 -z-10 opacity-70" style={{ background: "var(--gradient-aurora)" }} />
        <h2 className="font-display text-4xl font-bold tracking-tight md:text-6xl">
          Ship at the <span className="text-gradient">speed of AI.</span>
        </h2>
        <p className="mx-auto mt-4 max-w-xl text-muted-foreground">Join 12,000+ teams using AutoMind to run their marketing on autopilot.</p>
        <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
          <a href="#" className="rounded-full bg-gradient-to-r from-[var(--neon-violet)] to-[var(--neon-cyan)] px-7 py-3 text-sm font-semibold text-background">Start free trial</a>
          <a href="#" className="rounded-full glass px-7 py-3 text-sm font-medium">Book a demo</a>
        </div>
      </div>
    </section>
  );
}

// ---------------- FOOTER ----------------
export function Footer() {
  return (
    <footer className="border-t border-border/50 px-4 py-14">
      <div className="mx-auto max-w-6xl">
        <div className="grid gap-10 md:grid-cols-5">
          <div className="md:col-span-2">
            <a href="#" className="flex items-center gap-2 font-display text-lg font-bold">
              <span className="grid h-8 w-8 place-items-center rounded-lg bg-gradient-to-br from-[var(--neon-violet)] to-[var(--neon-cyan)] text-background">
                <Brain className="h-4 w-4" strokeWidth={2.5} />
              </span>
              AutoMindai<span className="text-neon">.info</span>
            </a>
            <p className="mt-4 max-w-sm text-sm text-muted-foreground">
              The autonomous AI marketing OS. Generate, publish, and optimize — automatically.
            </p>
            <div className="mt-5 flex gap-2">
              {[Github, Twitter, MessageCircle, Linkedin].map((I, i) => (
                <a key={i} href="#" className="grid h-9 w-9 place-items-center rounded-full glass transition hover:bg-white/10">
                  <I className="h-4 w-4" />
                </a>
              ))}
            </div>
          </div>
          {[
            { t: "Product", l: ["Features", "Pricing", "Agents", "Workflows", "Changelog"] },
            { t: "Resources", l: ["Docs", "API", "Guides", "Community", "Status"] },
            { t: "Company", l: ["About", "Careers", "Privacy", "Terms", "Contact"] },
          ].map((c) => (
            <div key={c.t}>
              <div className="mb-3 text-xs font-semibold uppercase tracking-[0.2em] text-muted-foreground">{c.t}</div>
              <ul className="space-y-2 text-sm">
                {c.l.map(x => <li key={x}><a href="#" className="text-muted-foreground transition hover:text-foreground">{x}</a></li>)}
              </ul>
            </div>
          ))}
        </div>
        <div className="mt-12 flex flex-col items-center justify-between gap-3 border-t border-border/50 pt-6 text-xs text-muted-foreground md:flex-row">
          <span>© {new Date().getFullYear()} AutoMind AI · All rights reserved.</span>
          <span>Made with autonomous agents · v3.0</span>
        </div>
      </div>
    </footer>
  );
}

// ---------------- helpers ----------------
function SectionWrap({ id, eyebrow, title, sub, children }: {
  id?: string; eyebrow: string; title: React.ReactNode; sub?: string; children: React.ReactNode;
}) {
  return (
    <section id={id} className="relative px-4 py-24 md:py-32">
      <div className="mx-auto max-w-6xl">
        <div className="mx-auto max-w-2xl text-center">
          <div className="inline-flex items-center gap-2 rounded-full glass px-3 py-1 text-[11px] uppercase tracking-[0.2em] text-muted-foreground">
            <Sparkles className="h-3 w-3" /> {eyebrow}
          </div>
          <h2 className="mt-5 font-display text-4xl font-bold leading-tight tracking-tight md:text-5xl lg:text-6xl">{title}</h2>
          {sub && <p className="mx-auto mt-4 max-w-xl text-sm text-muted-foreground md:text-base">{sub}</p>}
        </div>
        {children}
      </div>
    </section>
  );
}
