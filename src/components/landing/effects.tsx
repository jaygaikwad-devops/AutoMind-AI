import { useEffect, useRef } from "react";

export function CursorGlow() {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    let raf = 0;
    let x = 0, y = 0, tx = 0, ty = 0;
    const onMove = (e: MouseEvent) => { tx = e.clientX; ty = e.clientY; };
    const loop = () => {
      x += (tx - x) * 0.12;
      y += (ty - y) * 0.12;
      el.style.transform = `translate3d(${x - 200}px, ${y - 200}px, 0)`;
      raf = requestAnimationFrame(loop);
    };
    window.addEventListener("mousemove", onMove);
    raf = requestAnimationFrame(loop);
    return () => { window.removeEventListener("mousemove", onMove); cancelAnimationFrame(raf); };
  }, []);
  return (
    <div
      ref={ref}
      aria-hidden
      className="pointer-events-none fixed left-0 top-0 z-[1] hidden h-[400px] w-[400px] rounded-full opacity-60 mix-blend-screen md:block"
      style={{
        background: "radial-gradient(circle, oklch(0.72 0.25 295 / 0.25), transparent 60%)",
        filter: "blur(40px)",
      }}
    />
  );
}

export function AuroraBackground() {
  return (
    <div aria-hidden className="pointer-events-none fixed inset-0 z-0 overflow-hidden">
      <div className="absolute -top-40 -left-40 h-[600px] w-[600px] rounded-full opacity-60"
           style={{ background: "radial-gradient(circle, oklch(0.72 0.25 295 / 0.5), transparent 60%)", animation: "aurora 22s ease infinite" }} />
      <div className="absolute top-1/3 -right-40 h-[700px] w-[700px] rounded-full opacity-50"
           style={{ background: "radial-gradient(circle, oklch(0.82 0.18 200 / 0.45), transparent 60%)", animation: "aurora 28s ease infinite reverse" }} />
      <div className="absolute -bottom-40 left-1/4 h-[500px] w-[500px] rounded-full opacity-40"
           style={{ background: "radial-gradient(circle, oklch(0.75 0.25 350 / 0.4), transparent 60%)", animation: "aurora 25s ease infinite" }} />
      <div className="absolute inset-0 grid-bg opacity-30" />
      <div className="absolute inset-0" style={{ background: "radial-gradient(ellipse at top, transparent 0%, var(--background) 80%)" }} />
    </div>
  );
}
