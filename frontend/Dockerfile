# ─────────────────────────────────────────────────────────────────────────────
# AutoMind AI — Frontend Dockerfile (Production)
# TanStack Start + Bun + @lovable.dev/vite-tanstack-config
# ─────────────────────────────────────────────────────────────────────────────

FROM oven/bun:1-alpine AS builder
WORKDIR /app

# Install deps (no --frozen-lockfile — lockfile may need refresh after config changes)
COPY package.json bun.lock* bunfig.toml ./
RUN bun install

# Copy source and build
COPY . .
ENV NODE_ENV=production
RUN bun run build

# Ensure output dirs exist (even if empty) so COPY never fails
RUN mkdir -p .output .vinxi dist

# ── Production runtime ────────────────────────────────────────────────────────
FROM oven/bun:1-alpine AS runner
WORKDIR /app

RUN addgroup -S automind && adduser -S automind -G automind

# Copy all build artifacts + runtime deps
COPY --from=builder --chown=automind:automind /app/package.json ./
COPY --from=builder --chown=automind:automind /app/node_modules ./node_modules
COPY --from=builder --chown=automind:automind /app/.output ./.output
COPY --from=builder --chown=automind:automind /app/.vinxi ./.vinxi
COPY --from=builder --chown=automind:automind /app/dist ./dist

USER automind
EXPOSE 3000

ENV NODE_ENV=production \
    HOST=0.0.0.0 \
    PORT=3000

CMD ["bun", "run", "preview", "--host", "0.0.0.0", "--port", "3000"]
