import { createFileRoute } from "@tanstack/react-router";
import { AuroraBackground, CursorGlow } from "@/components/landing/effects";
import {
  Nav, Hero, LogoMarquee, SocialAutomation, Features,
  AgentNetwork, WorkflowBuilder, Infrastructure, Pricing,
  Testimonials, FAQ, CTA, Footer,
} from "@/components/landing/sections";

export const Route = createFileRoute("/")({
  component: Index,
});

function Index() {
  return (
    <main className="relative min-h-screen overflow-hidden bg-background text-foreground">
      <AuroraBackground />
      <CursorGlow />
      <div className="relative z-10">
        <Nav />
        <Hero />
        <LogoMarquee />
        <SocialAutomation />
        <Features />
        <AgentNetwork />
        <WorkflowBuilder />
        <Infrastructure />
        <Pricing />
        <Testimonials />
        <FAQ />
        <CTA />
        <Footer />
      </div>
    </main>
  );
}
