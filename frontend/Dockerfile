# ─────────────────────────────────────────────────────────────────────────────
# AutoMind AI — Frontend Dockerfile (Production Grade)
# Multi-stage: install → build → serve
# ─────────────────────────────────────────────────────────────────────────────

# ── Stage 1: Install dependencies ────────────────────────────────────────────
FROM oven/bun:1-alpine AS deps
WORKDIR /app
COPY package.json bun.lock* bunfig.toml ./
RUN bun install --frozen-lockfile

# ── Stage 2: Build ───────────────────────────────────────────────────────────
FROM oven/bun:1-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NODE_ENV=production
RUN bun run build

# ── Stage 3: Production runtime ──────────────────────────────────────────────
FROM oven/bun:1-alpine AS runner
WORKDIR /app

# Security: run as non-root
RUN addgroup -S automind && adduser -S automind -G automind

# Copy only the built output + server deps
COPY --from=builder --chown=automind:automind /app/.output ./.output
COPY --from=builder --chown=automind:automind /app/node_modules ./node_modules
COPY --from=builder --chown=automind:automind /app/package.json ./package.json

USER automind

EXPOSE 3000

ENV NODE_ENV=production \
    HOST=0.0.0.0 \
    PORT=3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD wget -qO- http://localhost:3000/ || exit 1

CMD ["bun", "run", ".output/server/index.mjs"]
