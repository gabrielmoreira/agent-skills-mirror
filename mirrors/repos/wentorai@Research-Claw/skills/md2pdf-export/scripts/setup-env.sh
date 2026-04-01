#!/usr/bin/env bash
# ============================================================================
# md2pdf-export: Environment Setup Script
# Installs Node.js, Puppeteer, and Chrome/Chromium dependencies
# Idempotent — safe to run multiple times
# ============================================================================
set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
MIN_NODE_VERSION=18
NVM_VERSION="v0.40.1"

# ── Utility functions ────────────────────────────────────────────────────────

log_info()  { echo -e "${BLUE}[INFO]${NC}  $*"; }
log_ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
log_err()   { echo -e "${RED}[ERROR]${NC} $*"; }

command_exists() { command -v "$1" &>/dev/null; }

version_gte() {
  # Returns 0 if $1 >= $2 (semver major only)
  local cur="$1" min="$2"
  [ "$cur" -ge "$min" ] 2>/dev/null
}

detect_os() {
  if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "macos"
  elif [ -f /etc/os-release ]; then
    . /etc/os-release
    case "$ID" in
      ubuntu|debian|pop|linuxmint|elementary) echo "debian" ;;
      alpine) echo "alpine" ;;
      centos|rhel|fedora|rocky|almalinux) echo "rhel" ;;
      arch|manjaro) echo "arch" ;;
      *) echo "linux-unknown" ;;
    esac
  else
    echo "unknown"
  fi
}

detect_container() {
  # Detect if running inside Docker/container
  if [ -f /.dockerenv ] || grep -qsE '(docker|containerd|kubepods)' /proc/1/cgroup 2>/dev/null; then
    echo "true"
  else
    echo "false"
  fi
}

# ── Step 1: Detect environment ───────────────────────────────────────────────

echo ""
echo "============================================================"
echo "  md2pdf-export: Environment Setup"
echo "============================================================"
echo ""

OS=$(detect_os)
IN_CONTAINER=$(detect_container)
log_info "Detected OS: $OS"
log_info "In container: $IN_CONTAINER"

# ── Step 2: Install Node.js ──────────────────────────────────────────────────

install_node_nvm() {
  log_info "Installing Node.js via nvm..."

  # Install nvm if not present
  if [ ! -d "$HOME/.nvm" ]; then
    log_info "Installing nvm ${NVM_VERSION}..."
    curl -fsSL "https://raw.githubusercontent.com/nvm-sh/nvm/${NVM_VERSION}/install.sh" | bash
  fi

  # Source nvm
  export NVM_DIR="$HOME/.nvm"
  [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"

  if ! command_exists nvm; then
    log_err "nvm installation failed. Try installing Node.js manually."
    return 1
  fi

  nvm install --lts
  nvm use --lts
  nvm alias default 'lts/*'

  log_ok "Node.js $(node -v) installed via nvm"
}

install_node_package_manager() {
  case "$OS" in
    macos)
      if command_exists brew; then
        log_info "Installing Node.js via Homebrew..."
        brew install node
      else
        install_node_nvm
      fi
      ;;
    debian)
      log_info "Installing Node.js via NodeSource..."
      if command_exists sudo; then
        sudo apt-get update -qq
        sudo apt-get install -y -qq curl
        curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
        sudo apt-get install -y -qq nodejs
      else
        apt-get update -qq
        apt-get install -y -qq curl
        curl -fsSL https://deb.nodesource.com/setup_lts.x | bash -
        apt-get install -y -qq nodejs
      fi
      ;;
    alpine)
      apk add --no-cache nodejs npm
      ;;
    rhel)
      if command_exists dnf; then
        sudo dnf install -y nodejs npm
      else
        sudo yum install -y nodejs npm
      fi
      ;;
    *)
      install_node_nvm
      ;;
  esac
}

check_node() {
  if command_exists node; then
    local node_major
    node_major=$(node -v | sed 's/v//' | cut -d. -f1)
    if version_gte "$node_major" "$MIN_NODE_VERSION"; then
      log_ok "Node.js $(node -v) found (>= v${MIN_NODE_VERSION} required)"
      return 0
    else
      log_warn "Node.js $(node -v) is too old (need >= v${MIN_NODE_VERSION})"
      return 1
    fi
  else
    log_warn "Node.js not found"
    return 1
  fi
}

if ! check_node; then
  install_node_package_manager
  # Re-source in case nvm was used
  [ -s "$HOME/.nvm/nvm.sh" ] && . "$HOME/.nvm/nvm.sh"
  if ! check_node; then
    log_err "Failed to install Node.js >= v${MIN_NODE_VERSION}"
    exit 1
  fi
fi

# Ensure npm is available
if ! command_exists npm; then
  log_err "npm not found even though Node.js is installed"
  exit 1
fi
log_ok "npm $(npm -v) found"

# ── Step 3: Install Chrome/Chromium system dependencies ─────────────────────

install_chrome_deps() {
  log_info "Installing Chromium system dependencies..."

  case "$OS" in
    debian)
      local DEPS=(
        ca-certificates fonts-liberation libasound2t64 libatk-bridge2.0-0t64
        libatk1.0-0t64 libcups2t64 libdbus-1-3 libdrm2 libgbm1 libgtk-3-0t64
        libnspr4 libnss3 libx11-xcb1 libxcomposite1 libxdamage1
        libxfixes3 libxrandr2 xdg-utils wget fonts-noto-cjk
      )
      # Try with t64 suffix first (Ubuntu 24+), fallback to plain names
      if command_exists sudo; then
        sudo apt-get update -qq
        sudo apt-get install -y -qq "${DEPS[@]}" 2>/dev/null || {
          # Fallback for older Ubuntu/Debian without t64 suffix
          local DEPS_FALLBACK=(
            ca-certificates fonts-liberation libasound2 libatk-bridge2.0-0
            libatk1.0-0 libcups2 libdbus-1-3 libdrm2 libgbm1 libgtk-3-0
            libnspr4 libnss3 libx11-xcb1 libxcomposite1 libxdamage1
            libxfixes3 libxrandr2 xdg-utils wget fonts-noto-cjk
          )
          sudo apt-get install -y -qq "${DEPS_FALLBACK[@]}"
        }
      else
        apt-get update -qq
        apt-get install -y -qq "${DEPS[@]}" 2>/dev/null || {
          local DEPS_FALLBACK=(
            ca-certificates fonts-liberation libasound2 libatk-bridge2.0-0
            libatk1.0-0 libcups2 libdbus-1-3 libdrm2 libgbm1 libgtk-3-0
            libnspr4 libnss3 libx11-xcb1 libxcomposite1 libxdamage1
            libxfixes3 libxrandr2 xdg-utils wget fonts-noto-cjk
          )
          apt-get install -y -qq "${DEPS_FALLBACK[@]}"
        }
      fi
      ;;
    alpine)
      apk add --no-cache \
        chromium nss freetype harfbuzz ca-certificates ttf-freefont \
        font-noto-cjk
      export PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
      export PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium-browser
      ;;
    rhel)
      if command_exists dnf; then
        sudo dnf install -y \
          alsa-lib atk cups-libs dbus-libs libdrm mesa-libgbm gtk3 \
          nss libXcomposite libXdamage libXfixes libXrandr xdg-utils \
          google-noto-sans-cjk-ttc-fonts
      fi
      ;;
    macos)
      # macOS: Puppeteer bundles Chromium, no system deps needed
      # But install CJK fonts if missing
      if command_exists brew; then
        brew install --cask font-noto-sans-cjk 2>/dev/null || true
      fi
      ;;
    *)
      log_warn "Unknown OS — skipping system dependency installation."
      log_warn "If Chrome fails to launch, install Chromium deps manually."
      ;;
  esac

  log_ok "Chrome system dependencies installed"
}

install_chrome_deps

# ── Step 4: Install Puppeteer ────────────────────────────────────────────────

install_puppeteer() {
  log_info "Installing puppeteer globally..."

  # Set npm global prefix to user space to avoid sudo
  local NPM_GLOBAL="$HOME/.npm-global"
  mkdir -p "$NPM_GLOBAL"
  npm config set prefix "$NPM_GLOBAL"

  # Ensure it's in PATH
  if [[ ":$PATH:" != *":$NPM_GLOBAL/bin:"* ]]; then
    export PATH="$NPM_GLOBAL/bin:$PATH"
    # Persist in shell rc
    for rc in "$HOME/.bashrc" "$HOME/.zshrc"; do
      if [ -f "$rc" ]; then
        grep -q 'npm-global/bin' "$rc" 2>/dev/null || \
          echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> "$rc"
      fi
    done
  fi

  # Install puppeteer
  npm install -g puppeteer 2>&1 | tail -5
  log_ok "puppeteer installed globally"
}

check_puppeteer() {
  if node -e "require('puppeteer')" 2>/dev/null; then
    local pup_ver
    pup_ver=$(node -e "console.log(require('puppeteer/package.json').version)" 2>/dev/null)
    log_ok "puppeteer v${pup_ver} found"
    return 0
  else
    return 1
  fi
}

if ! check_puppeteer; then
  install_puppeteer
  if ! check_puppeteer; then
    log_err "Failed to install puppeteer"
    exit 1
  fi
fi

# ── Step 5: Install md2pdf.js local dependencies ────────────────────────────

install_skill_deps() {
  log_info "Installing md2pdf.js npm dependencies..."

  cd "$SKILL_DIR/scripts"

  if [ ! -f package.json ]; then
    log_warn "No package.json found in scripts/, creating one..."
    cat > package.json <<'PJSON'
{
  "name": "md2pdf-export",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "markdown-it": "^14.0.0",
    "markdown-it-anchor": "^9.0.0",
    "markdown-it-footnote": "^4.0.0",
    "markdown-it-highlightjs": "^4.1.0",
    "markdown-it-texmath": "^1.0.0",
    "markdown-it-toc-done-right": "^4.2.0",
    "katex": "^0.16.0",
    "gray-matter": "^4.0.3",
    "puppeteer": ">=21.0.0"
  }
}
PJSON
  fi

  npm install --prefer-offline 2>&1 | tail -3
  log_ok "md2pdf.js dependencies installed"
  cd - > /dev/null
}

install_skill_deps

# ── Step 6: Verify everything works ─────────────────────────────────────────

log_info "Running smoke test..."

CHROME_LAUNCH_ARGS=""
if [ "$IN_CONTAINER" = "true" ]; then
  CHROME_LAUNCH_ARGS="--no-sandbox --disable-setuid-sandbox --disable-dev-shm-usage"
fi

SMOKE_RESULT=$(node -e "
const puppeteer = require('puppeteer');
(async () => {
  try {
    const args = '${CHROME_LAUNCH_ARGS}'.split(' ').filter(Boolean);
    const browser = await puppeteer.launch({
      headless: 'new',
      args: args
    });
    const page = await browser.newPage();
    await page.setContent('<h1>Smoke Test OK</h1>');
    const pdf = await page.pdf({ format: 'A4' });
    console.log('PDF_SIZE=' + pdf.length);
    await browser.close();
    console.log('SMOKE_OK');
  } catch (e) {
    console.error('SMOKE_FAIL: ' + e.message);
    process.exit(1);
  }
})();
" 2>&1) || true

if echo "$SMOKE_RESULT" | grep -q "SMOKE_OK"; then
  PDF_SIZE=$(echo "$SMOKE_RESULT" | grep "PDF_SIZE" | cut -d= -f2)
  log_ok "Smoke test passed (PDF generated: ${PDF_SIZE} bytes)"
else
  log_err "Smoke test failed:"
  echo "$SMOKE_RESULT"
  echo ""
  log_warn "Common fixes:"
  log_warn "  - Docker: ensure --no-sandbox is enabled"
  log_warn "  - Missing libs: run 'npx puppeteer browsers install chrome'"
  log_warn "  - Set PUPPETEER_EXECUTABLE_PATH to an existing Chrome binary"
  exit 1
fi

# ── Summary ──────────────────────────────────────────────────────────────────

echo ""
echo "============================================================"
echo "  ✅ md2pdf-export: Environment Ready"
echo "============================================================"
echo ""
echo "  Node.js:    $(node -v)"
echo "  npm:        $(npm -v)"
echo "  Puppeteer:  $(node -e "console.log(require('puppeteer/package.json').version)" 2>/dev/null || echo 'unknown')"
echo "  OS:         $OS"
echo "  Container:  $IN_CONTAINER"
echo ""
echo "  Usage:"
echo "    node ${SKILL_DIR}/scripts/md2pdf.js input.md"
echo "    node ${SKILL_DIR}/scripts/md2pdf.js input.md --type png"
echo "    node ${SKILL_DIR}/scripts/md2pdf.js input.md -o output.pdf"
echo ""
echo "============================================================"
