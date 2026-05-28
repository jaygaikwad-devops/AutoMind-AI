#!/usr/bin/env bash
# AutoMind AI — One-Command Docker Setup
# Usage: ./setup.sh [up|down|logs|clean]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() { echo -e "${BLUE}[AutoMind]${NC} $1"; }
ok()  { echo -e "${GREEN}[AutoMind]${NC} $1"; }
warn() { echo -e "${YELLOW}[AutoMind]${NC} $1"; }
err() { echo -e "${RED}[AutoMind]${NC} $1"; }

check_prereqs() {
    if ! command -v docker &> /dev/null; then
        err "Docker is not installed. Install it first: https://docs.docker.com/get-docker/"
        exit 1
    fi

    if ! docker compose version &> /dev/null && ! docker-compose version &> /dev/null; then
        err "Docker Compose is not installed. Install it first: https://docs.docker.com/compose/install/"
        exit 1
    fi

    ok "Docker and Docker Compose are installed."
}

init_env() {
    if [ ! -f ".env" ]; then
        log "Creating .env from .env.example ..."
        cp .env.example .env

        # Generate a secure JWT_SECRET
        if command -v openssl &> /dev/null; then
            SECRET=$(openssl rand -hex 32)
        else
            SECRET=$(head -c 64 /dev/urandom | base64 | tr -dc 'a-zA-Z0-9' | head -c 64)
        fi

        # Replace the placeholder JWT_SECRET
        if sed --version &>/dev/null; then
            sed -i "s/JWT_SECRET=replace-me-with-a-long-random-string/JWT_SECRET=${SECRET}/" .env
        else
            sed -i '' "s/JWT_SECRET=replace-me-with-a-long-random-string/JWT_SECRET=${SECRET}/" .env
        fi

        ok ".env created with a secure JWT_SECRET."
    else
        warn ".env already exists — skipping creation."
    fi
}

print_urls() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║               AutoMind AI is running locally!                    ║"
    echo "╠══════════════════════════════════════════════════════════════════╣"
    echo "║  Frontend        → http://localhost:3000                        ║"
    echo "║  Backend API     → http://localhost:8000                        ║"
    echo "║  API Docs (Swagger) → http://localhost:8000/docs                ║"
    echo "║  PostgreSQL      → localhost:5432                               ║"
    echo "║  Redis           → localhost:6379                                 ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Commands:"
    echo "  docker compose logs -f     # follow all logs"
    echo "  docker compose down          # stop everything"
    echo "  ./setup.sh down              # stop everything"
    echo "  ./setup.sh clean             # stop + remove volumes + reset"
}

cmd_up() {
    check_prereqs
    init_env

    log "Building and starting all services ..."
    docker compose up --build -d

    log "Waiting for services to be healthy ..."
    sleep 3

    # Wait for backend to respond
    for i in {1..30}; do
        if curl -sf http://localhost:8000/health &> /dev/null; then
            break
        fi
        echo -n "."
        sleep 1
    done

    print_urls
}

cmd_down() {
    log "Stopping all services ..."
    docker compose down
    ok "All services stopped."
}

cmd_logs() {
    docker compose logs -f
}

cmd_clean() {
    warn "This will stop all services and remove all data volumes (PostgreSQL, Redis)."
    read -p "Are you sure? [y/N] " confirm
    if [[ "$confirm" =~ ^[Yy]$ ]]; then
        docker compose down -v
        rm -f .env
        ok "Cleanup complete. Run './setup.sh up' to start fresh."
    else
        log "Cleanup cancelled."
    fi
}

cmd_help() {
    echo "AutoMind AI — Docker Setup"
    echo ""
    echo "Usage: ./setup.sh [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  up      Build and start all services (default)"
    echo "  down    Stop all services"
    echo "  logs    Follow service logs"
    echo "  clean   Stop all services and remove data volumes"
    echo "  help    Show this help message"
    echo ""
    echo "Quick start:"
    echo "  ./setup.sh        # same as 'up'"
}

# Main
case "${1:-up}" in
    up)
        cmd_up
        ;;
    down)
        cmd_down
        ;;
    logs)
        cmd_logs
        ;;
    clean)
        cmd_clean
        ;;
    help|--help|-h)
        cmd_help
        ;;
    *)
        err "Unknown command: $1"
        cmd_help
        exit 1
        ;;
esac
