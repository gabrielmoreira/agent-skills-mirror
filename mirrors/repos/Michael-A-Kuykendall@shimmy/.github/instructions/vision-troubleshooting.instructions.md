---
applyTo: "**"
---
# Shimmy Vision Troubleshooting Guide

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

## Common Issues & Solutions

This guide covers the most frequent issues encountered with Shimmy Vision and their solutions.

## License & Authentication Issues

### **"License key required for vision features"**

**Symptoms:**
- Vision commands return 401 error
- HTTP API returns `"license_required"` error
- CLI shows license missing message

**Solutions:**
```bash
# 1. Set environment variable (recommended)
export SHIMMY_LICENSE_KEY="B864C5-1464D7-52A2F5-C2453A-E20587-V3"

# 2. Use CLI flag
shimmy --license "your-key-here" generate --image test.jpg --prompt "describe"

# 3. Verify license format (should be XXXXXX-XXXXXX-XXXXXX-XXXXXX-XXXXXX-V3)
echo $SHIMMY_LICENSE_KEY | grep -E '^[A-F0-9]{6}-[A-F0-9]{6}-[A-F0-9]{6}-[A-F0-9]{6}-[A-F0-9]{6}-V3$'
```

**Verification:**
```bash
# Test license validation
curl -X POST http://localhost:11435/api/license/validate \
  -H "Content-Type: application/json" \
  -d '{"license_key": "your-key-here"}'
```

### **"License key is invalid or expired"**

**Symptoms:**
- Valid-looking key returns 403 error
- Was working before, now failing
- Keygen dashboard shows license as valid

**Common Causes & Solutions:**

#### **Network Issues**
```bash
# Test Keygen API connectivity
curl -s "https://api.keygen.sh/v1/accounts/6270bf9c-23ad-4483-9296-3a6d9178514a/licenses/actions/validate-key" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"meta": {"key": "your-license-key"}}'

# If this fails, check network/firewall settings
```

#### **System Clock Issues**
```bash
# Check system time
date

# Sync system clock (Linux/Mac)
sudo ntpdate -s time.nist.gov

# Sync system clock (Windows)
w32tm /resync
```

#### **Ed25519 Signature Verification Issues**
```bash
# Enable debug logging to see signature verification
RUST_LOG=shimmy_vision=debug cargo run --features llama,vision -- generate --image test.jpg --prompt "test"

# Look for "Signature verification" messages in output
```

### **"Monthly usage limit exceeded"**

**Symptoms:**  
- 402 error with usage details
- Was working, now blocked
- API returns `payment_required` error

**Solutions:**
```bash
# 1. Check current usage
curl -H "Authorization: Bearer $SHIMMY_LICENSE_KEY" \
  http://localhost:11435/api/license/usage

# 2. Wait for next billing cycle (shown in response)
# 3. Or upgrade to higher tier at shimmy-vision website
```

**Usage Optimization:**
```bash
# Batch process images to reduce API calls
shimmy generate --image "img1.jpg,img2.jpg,img3.jpg" --prompt "process all"

# Use lower max_tokens for simple tasks  
shimmy generate --image doc.pdf --prompt "extract title only" --max-tokens 50
```

## Installation & Build Issues

### **"Feature 'vision' not available"**

**Symptoms:**
- CLI shows "vision feature not compiled"
- Commands fail with feature error
- Only text generation works

**Solutions:**
```bash
# 1. Build with vision features
cargo build --release --features llama,vision

# 2. Or download pre-built binary with vision support
# Check GitHub releases for vision-enabled builds

# 3. Verify features in build
cargo run --features llama,vision -- --help | grep -i vision
```

### **Vision Model Download Issues**

**Symptoms:**
- "Failed to download vision model"  
- Slow first-time startup
- Network timeout errors

**Solutions:**
```bash
# 1. Manual download with custom directory
export SHIMMY_VISION_MODEL_DIR=/path/to/models
mkdir -p $SHIMMY_VISION_MODEL_DIR

# 2. Increase download timeout
export SHIMMY_VISION_DOWNLOAD_TIMEOUT_SECS=600  # 10 minutes

# 3. Use offline model
export SHIMMY_VISION_MODEL_PATH=/path/to/existing/model.gguf

# 4. Verify model file
ls -lh $SHIMMY_VISION_MODEL_PATH
file $SHIMMY_VISION_MODEL_PATH  # Should show "data" or binary file
```

### **GPU/CUDA Issues**

**Symptoms:**
- "CUDA device not found"
- Slow processing on GPU systems
- Memory errors with large images

**Solutions:**
```bash
# 1. Verify CUDA installation
nvidia-smi

# 2. Build with CUDA support
cargo build --release --features llama,vision,llama-cuda

# 3. Set GPU device
export CUDA_VISIBLE_DEVICES=0

# 4. Reduce GPU memory usage
export SHIMMY_GPU_LAYERS=20  # Lower number = less GPU usage

# 5. For memory issues, reduce image size
export SHIMMY_VISION_MAX_LONG_EDGE=1024
export SHIMMY_VISION_MAX_PIXELS=1000000
```

## Image Processing Issues

### **"Unable to process image: invalid format"**

**Symptoms:**
- Supported format fails to process
- Base64 decoding errors
- Image corruption messages

**Solutions:**
```bash
# 1. Verify image file
file image.jpg  # Should show image type
head -c 20 image.jpg  # Should show binary data, not text

# 2. Convert to supported format
convert image.bmp image.jpg  # Using ImageMagick
# or
ffmpeg -i image.webp image.png

# 3. For API calls, verify base64 encoding
base64 image.jpg | head -c 100  # Should show clean base64 without newlines

# 4. Test with minimal image
echo "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==" > test_image.txt
```

### **"Image size exceeds limit"**

**Symptoms:**
- 413 error for large images
- Upload fails with size error
- Processing timeouts

**Solutions:**
```bash
# 1. Check image size
ls -lh large_image.jpg

# 2. Resize image before processing
convert large_image.jpg -resize 1920x1920\> resized_image.jpg

# 3. Increase limits (if self-hosting)
export SHIMMY_VISION_MAX_FETCH_BYTES=52428800  # 50MB
export SHIMMY_VISION_MAX_PIXELS=5000000

# 4. Split PDF pages
pdftk document.pdf burst output page_%02d.pdf
```

### **URL Processing Issues**

**Symptoms:**
- "Failed to fetch URL"
- Timeout errors for web pages
- Empty screenshots

**Solutions:**
```bash
# 1. Test URL accessibility
curl -I "https://example.com"

# 2. Increase timeout
export SHIMMY_VISION_DOWNLOAD_TIMEOUT_SECS=60

# 3. Set custom user agent
export SHIMMY_VISION_USER_AGENT="Mozilla/5.0 (compatible; ShimmyVision/1.0)"

# 4. For private networks, enable private IPs
export SHIMMY_VISION_ALLOW_PRIVATE_IPS=true

# 5. Debug with headless browser
# Check if URL loads in regular browser first
```

## Performance Issues

### **Slow Processing Times**

**Symptoms:**
- Each image takes >30 seconds
- High CPU usage during processing
- System becomes unresponsive

**Solutions:**
```bash
# 1. Use GPU acceleration (if available)
cargo run --features llama,vision,llama-cuda

# 2. Optimize image size
export SHIMMY_VISION_MAX_LONG_EDGE=1024  # Smaller = faster

# 3. Reduce max tokens for simple tasks
shimmy generate --image doc.jpg --prompt "title only" --max-tokens 20

# 4. Increase thread count (CPU only)
export SHIMMY_VISION_THREAD_COUNT=8

# 5. Monitor system resources
htop  # Check CPU/memory usage
nvidia-smi  # Check GPU usage
```

### **Memory Issues**

**Symptoms:**
- "Out of memory" errors
- System freezes during processing
- Killed by OOM killer

**Solutions:**
```bash
# 1. Check available memory
free -h  # Linux
# Ensure >8GB RAM available

# 2. Process images sequentially, not in batch
for img in *.jpg; do
  shimmy generate --image "$img" --prompt "analyze" > "${img%.jpg}.json"
done

# 3. Reduce model memory usage
export SHIMMY_GPU_LAYERS=0  # Force CPU-only mode

# 4. Close other applications
# Free up system memory before processing
```

## API & Integration Issues

### **HTTP Server Won't Start**

**Symptoms:**
- "Address already in use"
- Server fails to bind to port
- Connection refused errors

**Solutions:**
```bash
# 1. Check what's using the port
lsof -i :11435  # Linux/Mac
netstat -ano | findstr :11435  # Windows

# 2. Use different port
shimmy serve --bind 127.0.0.1:11436

# 3. Kill existing shimmy process
pkill shimmy
# or find PID and kill
ps aux | grep shimmy
kill [PID]

# 4. Verify server is running
curl http://localhost:11435/health
```

### **CORS Issues**

**Symptoms:**
- Browser blocks API requests
- "Access-Control-Allow-Origin" errors
- Frontend can't connect to API

**Solutions:**
```bash
# 1. Shimmy doesn't have CORS restrictions by default
# If issues, verify request format:

curl -X POST http://localhost:11435/api/vision \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $SHIMMY_LICENSE_KEY" \
  -d '{"prompt": "test", "image_url": "https://example.com/test.jpg"}'

# 2. For browser requests, ensure proper headers
fetch('http://localhost:11435/api/vision', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + licenseKey
  },
  body: JSON.stringify({...})
})
```

## Payment & Checkout Issues

### **Stripe Checkout Not Loading**

**Symptoms:**
- Blank checkout page
- JavaScript errors in browser console
- Checkout session creation fails

**Solutions:**
```bash
# 1. Verify Worker endpoints
curl https://shimmy-license-webhook.workers.dev/health
# Should return: {"status": "ok", ...}

# 2. Test buy endpoint
curl "https://shimmy-license-webhook.workers.dev/buy?tier=developer&email=test@example.com"
# Should redirect to Stripe

# 3. Check browser console for errors
# Open DevTools → Console and look for error messages

# 4. Verify Stripe publishable key in frontend
# Check .env.local has correct pk_live_... key
```

### **License Not Generated After Payment**

**Symptoms:**
- Payment successful in Stripe
- No license key received  
- Success page shows error

**Solutions:**
```bash
# 1. Check Stripe webhook delivery
# Go to Stripe Dashboard → Webhooks → View events
# Look for "checkout.session.completed" events

# 2. Check Worker logs
wrangler tail --env production

# 3. Verify webhook endpoint URL
# Should be: https://shimmy-license-webhook.workers.dev/stripe-webhook

# 4. Test webhook manually (with proper signature)
# This requires Stripe CLI for proper signing

# 5. Check Keygen for license creation
# Login to Keygen dashboard and check recent licenses
```

## Debug & Logging

### **Enable Debug Logging**

```bash
# Rust application logging
export RUST_LOG=debug
export SHIMMY_VISION_TRACE=1

# Specific module logging
export RUST_LOG=shimmy=debug,shimmy_vision=trace

# Worker logging
wrangler tail --env production --format pretty

# Stripe webhook events
stripe listen --forward-to localhost:8787/stripe-webhook
```

### **Test Environment Setup**

```bash
# Use test data for debugging
export SHIMMY_LICENSE_KEY="1CF681-F65AC1-34018A-CA470A-1B107D-V3"  # Test license

# Use test Stripe environment
# Point frontend to test worker for debugging
const WORKER_URL = 'https://shimmy-license-webhook-test.workers.dev';

# Minimal test image for debugging
echo "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==" | base64 -d > minimal.png
```

## Getting Help

### **Information to Collect**
When reporting issues, please include:

1. **System Information:**
   ```bash
   uname -a  # Operating system
   cargo --version  # Rust version
   shimmy --version  # Application version
   ```

2. **License Information:**
   ```bash
   echo $SHIMMY_LICENSE_KEY | cut -c1-10  # First 10 chars only
   curl -X POST http://localhost:11435/api/license/validate \
     -H "Content-Type: application/json" \
     -d '{"license_key": "'$SHIMMY_LICENSE_KEY'"}' | jq .
   ```

3. **Error Logs:**
   ```bash
   RUST_LOG=debug shimmy generate --image test.jpg --prompt "test" 2>&1 | head -50
   ```

4. **Configuration:**
   ```bash
   env | grep SHIMMY  # Show shimmy-related env vars (redact license key)
   ```

### **Support Channels**

- **Email**: michaelallenkuykendall@gmail.com
- **GitHub Issues**: [shimmy-workspace repository](https://github.com/Michael-A-Kuykendall/shimmy)
- **Documentation**: Check .github/instructions/ for latest guides

### **Emergency Contacts**

For critical production issues:
- **Payment Issues**: Contact immediately via email with "URGENT" in subject
- **License Validation Down**: Check Keygen status page first
- **Security Issues**: Report privately via email, do not open public issues

This troubleshooting guide covers 95% of common issues encountered with Shimmy Vision. For issues not covered here, follow the "Getting Help" section to provide detailed information for support.