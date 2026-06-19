# ─────────────────────────────────────────────────────────────────────────────
# AutoMind AI — Frontend Dockerfile
# TanStack Start requires full source at runtime for SSR dev server
# ─────────────────────────────────────────────────────────────────────────────

FROM oven/bun:1-alpine
WORKDIR /app

# Install deps
COPY package.json bun.lock* bunfig.toml ./
RUN bun install

# Copy full source (TanStack Start needs src/ at runtime)
COPY . .

EXPOSE 3000

CMD ["bun", "run", "dev", "--host", "0.0.0.0", "--port", "3000"]
