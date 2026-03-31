---
applyTo: "**"
---
# 👁️ Vision Module Instructions

## 🔐 CRITICAL: Access & Credentials (READ FIRST)

### Required Environment Variables
All credentials are stored in `.env` file (gitignored). Source with: `source .env`

**Keygen API:**
- `KEYGEN_ACCOUNT_ID=6270bf9c-23ad-4483-9296-3a6d9178514a`
- `KEYGEN_ADMIN_TOKEN=admin-8087987cc615a82c0e67583b2163860df66cbcb5770b73026857c45d2f47d6b9v3`
- `KEYGEN_PRODUCT_TOKEN=prod-e1c02ef59daf4772577df65970f7c07a3058c7037648eba932c48f97a5488ab7v3`

**Stripe API:**
- `STRIPE_KEY=sk_test_51RwqRv1g5xy1QMw5LPiGeHt0qcVIkpsqi9fBbxgB4vgIzKBwyTgSfv1WmuaesbTSig0hMTaWft2o7Y4NZ5gxLINw00d5HNnuze`
- `STRIPE_PUBLISHABLE_KEY_TEST=pk_test_51RwqRv1g5xy1QMw5drOBCVy7G8isU0C07QL4wNYHzy9MTLTBiGDhrFVHmO03dbuPiq3PXDrK9aVMGKIMTne48AQV00n9v9cCIw`
- `STRIPE_PUBLISHABLE_KEY_LIVE=pk_live_51RwqRv1g5xy1QMw5P01z0dVCQWSnSqc2VQEfmscQyrfy2LAe1Un2gqE3b3kmxxxFlP8XyosxJVu2K1p81ShmgyDw009RQ8xU6Q`

**Cloudflare Workers:**
- `CLOUDFLARE_WORKERS_TOKEN` (set in Windows environment)
- Use: `export CLOUDFLARE_API_TOKEN=$CLOUDFLARE_WORKERS_TOKEN`

**GitHub API:**
- `GITHUB_TOKEN` (set in Windows environment)

### API Testing Commands
**Keygen:**
```bash
source .env
curl -H "Authorization: Bearer $KEYGEN_ADMIN_TOKEN" \
  "https://api.keygen.sh/v1/accounts/$KEYGEN_ACCOUNT_ID/licenses"
```

**Stripe:**
```bash
source .env
curl -u "$STRIPE_KEY:" https://api.stripe.com/v1/customers
```

**Wrangler:**
```bash
export CLOUDFLARE_API_TOKEN=$CLOUDFLARE_WORKERS_TOKEN
wrangler whoami
```

**GitHub:**
```bash
curl -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/user
```

### License Keys for Testing
- Valid: `1CF681-F65AC1-34018A-CA470A-1B107D-V3`
- Expired: `F252DC-EC5112-FB08C7-16AC0D-52409D-V3`
- Suspended: `42F598-624F3C-A4A0A1-E06A96-398E3F-V3`

## Architecture

- `src/vision.rs` - Main vision processing logic
- `src/vision_adapter.rs` - Trait-based abstraction for public/private split
- `src/vision_license.rs` - Keygen license validation

## Licensing

- Vision features require valid Keygen license
- License validation happens via `shimmy-vision-private` crate
- Keygen Account ID: `6270bf9c-23ad-4483-9296-3a6d9178514a`

## Testing Vision

- Vision tests in `tests/vision_*.rs`
- Requires `SHIMMY_VISION_MODEL_PATH` environment variable
- Use task `serve-vision-gpu` for GPU-accelerated testing

## Build Flags

- `--features vision` - Enable vision module
- `--features llama,vision` - Vision with llama backend
- `--features llama,vision,llama-cuda` - GPU acceleration

## Local Vision Testing Process (Manual Commands)

### Setup Test Environment
1. Switch Stripe to test mode in Cloudflare Worker
2. Set test environment variables:
   ```bash
   export SHIMMY_VISION_MODEL_PATH="/path/to/vision/model"
   export SHIMMY_VISION_MAX_LONG_EDGE=1024
   export SHIMMY_VISION_MAX_PIXELS=2500000
   ```

### Manual Lifecycle Testing Commands
Execute these commands in sequence for full customer journey testing:

1. **Start Vision Server:**
   ```bash
   cargo run --features llama,vision -- serve --bind 127.0.0.1:11435
   ```

2. **Test Vision API (separate terminal):**
   ```bash
   curl -X POST http://127.0.0.1:11435/api/generate \
     -H "Content-Type: application/json" \
     -d '{
       "model": "vision-model-name",
       "prompt": "Describe this image",
       "image": "data:image/jpeg;base64,'$(base64 -w 0 test-image.jpg)'",
       "stream": false,
       "max_tokens": 200
     }'
   ```

3. **Test Checkout Flow:**
   ```bash
   # Create test checkout session
   curl -X POST https://shimmy-license-webhook-test.michaelallenkuykendall.workers.dev/buy \
     -d "tier=developer&email=test@example.com"
   ```

4. **Verify License Creation:**
   ```bash
   # Check Keygen for new license
   curl -H "Authorization: Bearer $KEYGEN_ADMIN_TOKEN" \
        -H "Accept: application/vnd.api+json" \
        "https://api.keygen.sh/v1/accounts/$KEYGEN_ACCOUNT_ID/licenses?limit=5&sort=-created"
   ```

5. **Test Vision with License:**
   ```bash
   # Use licensed vision features
   curl -X POST http://127.0.0.1:11435/api/generate \
     -H "Authorization: Bearer <license-key>" \
     -H "Content-Type: application/json" \
     -d '{"model": "vision-model", "prompt": "Analyze", "image": "...", "licensed": true}'
   ```

### Cross-Platform Testing
- Build binaries: `cargo build --target x86_64-unknown-linux-gnu --features llama,vision --release`
- Deploy to cloud environments
- Test vision processing on Linux x86_64, macOS ARM64, Windows x64
- Verify model loading and inference performance
