#!/usr/bin/env bash
# =============================================================================
# catobigato.com — Production Deploy Script
# =============================================================================
# Pull latest code, rebuild Docker containers, run optional migrations.
#
# Usage:
#   bin/deploy.sh [MODE] [OPTIONS]
#
# MODES:
#   full        (default) Rebuild API + frontend
#   frontend    Only rebuild the frontend container
#   backend     Only rebuild the API container
#
# OPTIONS:
#   --branch <name>   Branch to deploy (default: main)
#   --migrate         Run Alembic migrations after rebuilding API
#   --no-pull         Skip git pull (deploy from current working tree)
#   --dry-run         Print commands without executing
#   -h, --help        Show this help message
#
# Container layout:
#   catobigato-api       FastAPI  → :8001
#   catobigato-frontend  Vite/Nginx → :8081
#
# Examples:
#   bin/deploy.sh                       # full deploy from main
#   bin/deploy.sh frontend              # rebuild only frontend
#   bin/deploy.sh backend --migrate     # rebuild API + run migrations
#   bin/deploy.sh --branch dev          # deploy dev branch
#   bin/deploy.sh --dry-run             # preview what would happen
# =============================================================================
set -euo pipefail

# -----------------------------------------------------------------------------
# Colours
# -----------------------------------------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m'

# -----------------------------------------------------------------------------
# Paths
# -----------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
COMPOSE_FILE="${PROJECT_ROOT}/docker-compose.yml"

# -----------------------------------------------------------------------------
# Defaults
# -----------------------------------------------------------------------------
MODE="full"
BRANCH="main"
DO_MIGRATE=false
DO_PULL=true
DRY_RUN=false
STEP=0
START_TIME=$(date +%s)

declare -a STEP_NAMES=()
declare -a STEP_RESULTS=()

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
usage() {
    sed -n '3,35p' "$0" | sed 's/^# \?//'
    exit 0
}

info()    { echo -e "${CYAN}▶${NC} $*"; }
success() { echo -e "${GREEN}✔${NC} $*"; }
warn()    { echo -e "${YELLOW}⚠${NC}  $*"; }
error()   { echo -e "${RED}✖${NC} $*" >&2; }
dim()     { echo -e "${DIM}  $*${NC}"; }

step() {
    STEP=$((STEP + 1))
    echo ""
    echo -e "${BOLD}${CYAN}━━━ Step ${STEP}: $*${NC}"
    STEP_NAMES+=("$*")
}

record_result() { STEP_RESULTS+=("$1"); }

run() {
    if [[ "$DRY_RUN" == true ]]; then
        echo -e "  ${DIM}[dry-run]${NC} ${BOLD}$*${NC}"
    else
        "$@"
    fi
}

elapsed_time() {
    local secs=$(( $(date +%s) - START_TIME ))
    printf '%dm%02ds' $(( secs / 60 )) $(( secs % 60 ))
}

# -----------------------------------------------------------------------------
# Parse arguments
# -----------------------------------------------------------------------------
parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            full|frontend|backend)
                MODE="$1"; shift ;;
            --branch)
                [[ -n "${2:-}" ]] || { error "--branch requires a value"; exit 1; }
                BRANCH="$2"; shift 2 ;;
            --migrate)
                DO_MIGRATE=true; shift ;;
            --no-pull)
                DO_PULL=false; shift ;;
            --dry-run)
                DRY_RUN=true; shift ;;
            -h|--help)
                usage ;;
            *)
                error "Unknown argument: $1"
                echo "Run 'bin/deploy.sh --help' for usage."
                exit 1 ;;
        esac
    done
}

# -----------------------------------------------------------------------------
# Pre-flight
# -----------------------------------------------------------------------------
preflight() {
    info "catobigato.com deploy — mode: ${BOLD}${MODE}${NC} | branch: ${BOLD}${BRANCH}${NC} | dry-run: ${BOLD}${DRY_RUN}${NC}"
    dim "Project: ${PROJECT_ROOT}"
    dim "Compose: ${COMPOSE_FILE}"
    echo ""

    if [[ ! -f "$COMPOSE_FILE" ]]; then
        error "Compose file not found: ${COMPOSE_FILE}"
        exit 1
    fi
}

# -----------------------------------------------------------------------------
# Step: Git pull
# -----------------------------------------------------------------------------
do_pull() {
    if [[ "$DO_PULL" == false ]]; then
        step "Git pull (skipped — --no-pull)"
        record_result "skip"
        return
    fi

    step "Git pull (branch: ${BRANCH})"

    run git -C "$PROJECT_ROOT" fetch origin
    run git -C "$PROJECT_ROOT" checkout "$BRANCH"
    run git -C "$PROJECT_ROOT" pull origin "$BRANCH"

    if [[ "$DRY_RUN" == false ]]; then
        local sha
        sha=$(git -C "$PROJECT_ROOT" log -1 --oneline)
        success "At: ${sha}"
    fi

    record_result "ok"
}

# -----------------------------------------------------------------------------
# Step: Build & restart containers
# -----------------------------------------------------------------------------
do_build() {
    local services=""

    case "$MODE" in
        full)     services="catobigato-api catobigato-frontend" ;;
        frontend) services="catobigato-frontend" ;;
        backend)  services="catobigato-api" ;;
    esac

    step "Build & restart: ${services}"
    dim "docker compose -f ${COMPOSE_FILE} up -d --build ${services}"

    run docker compose -f "$COMPOSE_FILE" up -d --build $services

    if [[ "$DRY_RUN" == false ]]; then
        success "Containers rebuilt and started"
    fi

    record_result "ok"
}

# -----------------------------------------------------------------------------
# Step: Run migrations
# -----------------------------------------------------------------------------
do_migrate() {
    if [[ "$DO_MIGRATE" == false ]]; then
        step "Alembic migrations (skipped)"
        record_result "skip"
        return
    fi

    step "Run Alembic migrations"
    dim "docker exec catobigato-api alembic upgrade head"

    run docker exec catobigato-api alembic upgrade head

    if [[ "$DRY_RUN" == false ]]; then
        success "Migrations applied"
    fi

    record_result "ok"
}

# -----------------------------------------------------------------------------
# Step: Health check
# -----------------------------------------------------------------------------
do_health_check() {
    step "Health check"

    if [[ "$DRY_RUN" == true ]]; then
        dim "[dry-run] would check http://localhost:8001/api/health"
        record_result "skip"
        return
    fi

    if [[ "$MODE" == "frontend" ]]; then
        # Just check frontend responds
        local attempt
        for attempt in 1 2 3 4 5; do
            if curl -sf -o /dev/null "http://localhost:8081"; then
                success "Frontend responding on :8081"
                record_result "ok"
                return
            fi
            sleep 2
        done
        warn "Frontend not responding after 10s"
        record_result "fail"
        return
    fi

    # Check API health
    local attempt
    for attempt in 1 2 3 4 5 6; do
        if curl -sf -o /dev/null "http://localhost:8001/api/health"; then
            success "API healthy on :8001"
            record_result "ok"
            return
        fi
        sleep 3
    done

    warn "API not responding after 18s — check logs: docker logs catobigato-api"
    record_result "fail"
}

# -----------------------------------------------------------------------------
# Step: Cleanup
# -----------------------------------------------------------------------------
do_cleanup() {
    step "Cleanup dangling images"

    run docker image prune -f --filter "until=72h"

    record_result "ok"
}

# -----------------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------------
print_summary() {
    echo ""
    echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD} Deploy Summary — catobigato.com${NC}"
    echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    printf "%-6s  %-42s  %s\n" "Step" "Action" "Result"
    echo  "──────  ──────────────────────────────────────────  ──────"

    local i
    for i in "${!STEP_NAMES[@]}"; do
        local num=$((i + 1))
        local result="${STEP_RESULTS[$i]:-?}"
        local icon
        case "$result" in
            ok)   icon="${GREEN}✔ ok${NC}" ;;
            skip) icon="${YELLOW}– skip${NC}" ;;
            fail) icon="${RED}✖ FAIL${NC}" ;;
            *)    icon="${DIM}?${NC}" ;;
        esac
        printf "%-6s  %-42s  " "$num" "${STEP_NAMES[$i]:0:42}"
        echo -e "$icon"
    done

    echo ""
    echo -e "  Mode: ${BOLD}${MODE}${NC}   Branch: ${BOLD}${BRANCH}${NC}   Elapsed: ${BOLD}$(elapsed_time)${NC}"
    echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    if [[ "$DRY_RUN" == false ]]; then
        echo ""
        echo -e "${BOLD}Running containers:${NC}"
        docker ps --filter "name=catobigato" --format "  {{.Names}}  {{.Status}}  {{.Ports}}" 2>/dev/null || true
    fi
}

trap 'echo ""; error "Deploy interrupted."; print_summary; exit 1' ERR

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
main() {
    parse_args "$@"
    preflight
    do_pull
    do_build
    do_migrate
    do_health_check
    do_cleanup
    print_summary
    echo ""
    echo -e "${GREEN}${BOLD}Deploy complete.${NC}"
}

main "$@"
