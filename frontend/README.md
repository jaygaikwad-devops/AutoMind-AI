# Frontend
This directory is reserved for a standalone Next.js / TanStack Start build of the AutoMind AI marketing site.

In this Lovable workspace the live frontend already runs from the repository root (`/src`) on TanStack Start v1 + React 19 + Tailwind v4. The Dockerfile here mirrors that build so the same UI can be containerized when deploying outside Lovable.

To run the live app:
```bash
bun install
bun run dev
```

To build for production:
```bash
bun run build
```
