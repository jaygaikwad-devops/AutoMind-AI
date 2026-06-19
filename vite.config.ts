import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tsConfigPaths from "vite-tsconfig-paths";

export default defineConfig({
  plugins: [react(), tsConfigPaths()],

  server: {
    host: "0.0.0.0",
    port: 3000,
    // Proxy API calls to backend in development
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        secure: false,
      },
      "/ws": {
        target: "ws://localhost:8000",
        ws: true,
      },
    },
  },

  build: {
    outDir: "dist",
    sourcemap: false,
  },
});
