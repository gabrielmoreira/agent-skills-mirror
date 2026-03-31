---
applyTo: "**"
---
# Shimmy Vision API Reference

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

## Overview

Shimmy Vision provides both CLI and HTTP API interfaces for vision processing. All vision features require a valid license key for access.

## Authentication

### **License Key Configuration**
```bash
# Environment variable (recommended)
export SHIMMY_LICENSE_KEY="your-license-key-here"

# CLI flag (alternative)
shimmy --license "your-license-key-here" [command]
```

### **License Validation**
- **Method**: Keygen API with Ed25519 signature verification
- **Frequency**: Cached for 24 hours, revalidated on expiry  
- **Offline Grace**: 24-hour grace period for cached licenses
- **Usage Metering**: Monthly usage tracked and enforced

## CLI Interface

### **Vision Processing**
```bash
# Basic image analysis
shimmy generate --prompt "Describe this image" --image path/to/image.jpg

# OCR extraction  
shimmy generate --prompt "Extract all text" --image document.pdf --max-tokens 500

# Structured data extraction
shimmy generate --prompt "Extract invoice data as JSON" --image invoice.png

# Web page processing  
shimmy generate --prompt "Analyze this webpage" --image-url "https://example.com"

# Batch processing
for img in *.jpg; do
  shimmy generate --prompt "Extract text" --image "$img" > "${img%.jpg}.json"
done
```

### **Common CLI Options**
```bash
--image <path>          # Local image file path
--image-url <url>       # Remote image URL  
--prompt <text>         # Analysis prompt
--max-tokens <num>      # Maximum response tokens (default: 500)
--temperature <float>   # Sampling temperature (0.0-1.0)
--format json          # Output format (json, text)
--license <key>        # License key (alternative to env var)
```

### **Supported Image Formats**
- **Static**: JPEG, PNG, GIF, WEBP, BMP, TIFF
- **Documents**: PDF (first page), SVG
- **Web**: Screenshots via URL processing

## HTTP API

### **Base Configuration**
```bash
# Start server with vision features
cargo run --features llama,vision -- serve --bind 127.0.0.1:11435

# Or with GPU acceleration
cargo run --features llama,vision,llama-cuda -- serve --bind 127.0.0.1:11435
```

### **Vision Analysis Endpoint**

#### **POST /api/vision**

**Request Headers:**
```http
Content-Type: application/json
Authorization: Bearer your-license-key-here  # Optional if SHIMMY_LICENSE_KEY set
```

**Request Body:**
```json
{
  "prompt": "Describe this image in detail",
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABA...",  
  "max_tokens": 500,
  "temperature": 0.7,
  "stream": false
}
```

**Alternative with URL:**
```json
{
  "prompt": "Extract text from this webpage",
  "image_url": "https://example.com/page.html",
  "max_tokens": 1000,
  "stream": false
}
```

**Response (Success):**
```json
{
  "choices": [{
    "message": {
      "role": "assistant",
      "content": "This image shows a modern office building..."
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 15,
    "completion_tokens": 87,
    "total_tokens": 102
  },
  "model": "minicpm-v"
}
```

**Response (Error):**
```json
{
  "error": {
    "type": "license_required",
    "message": "Vision features require a valid license",
    "code": 402
  }
}
```

### **Streaming Response**

**Request with streaming:**
```json
{
  "prompt": "Analyze this chart",
  "image": "data:image/png;base64,iVBOR...",
  "stream": true
}
```

**Server-Sent Events Response:**
```
data: {"choices":[{"delta":{"content":"This"}}]}

data: {"choices":[{"delta":{"content":" chart"}}]}

data: {"choices":[{"delta":{"content":" shows"}}]}

data: [DONE]
```

### **WebSocket Interface**

#### **WS /ws/vision**

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:11435/ws/vision');

// First message: Send request
ws.send(JSON.stringify({
  "prompt": "What's in this image?",
  "image": "data:image/jpeg;base64,/9j/...",
  "max_tokens": 300
}));

// Subsequent messages: Receive tokens
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.done) {
    console.log('Complete');
  } else {
    console.log('Token:', data.token);
  }
};
```

## Status & Health Endpoints

### **GET /health**
```json
{
  "status": "ok",
  "version": "1.7.2",
  "features": ["llama", "vision"],
  "vision_model_loaded": true,
  "license_valid": true,
  "uptime_seconds": 3600
}
```

### **GET /v1/models**
```json
{
  "data": [{
    "id": "minicpm-v",
    "object": "model",
    "created": 1641918000,
    "owned_by": "shimmy",
    "permission": [],
    "root": "minicpm-v",
    "parent": null
  }]
}
```

## License Management API

### **POST /api/license/validate**

**Request:**
```json
{
  "license_key": "your-license-key"
}
```

**Response:**
```json
{
  "valid": true,
  "expires_at": "2025-02-08T00:00:00Z",
  "usage": {
    "current_period": {
      "pages_processed": 1250,
      "pages_limit": 2500,
      "period_start": "2025-01-01T00:00:00Z",
      "period_end": "2025-02-01T00:00:00Z"
    }
  },
  "entitlements": [
    "VISION_ANALYSIS",
    "API_ACCESS", 
    "CLI_ACCESS"
  ],
  "policy": {
    "name": "Developer",
    "tier": "developer"
  }
}
```

### **GET /api/license/usage**

**Response:**
```json
{
  "current_period": {
    "pages_processed": 1250,
    "pages_limit": 2500,
    "percentage_used": 50.0,
    "days_remaining": 15
  },
  "all_time": {
    "total_pages_processed": 15750,
    "account_created": "2024-12-01T00:00:00Z"
  }
}
```

## Error Codes & Responses

### **Authentication Errors**
```json
// 401 - Missing License
{
  "error": {
    "type": "unauthorized",
    "message": "License key required for vision features",
    "code": 401
  }
}

// 403 - Invalid License  
{
  "error": {
    "type": "forbidden", 
    "message": "License key is invalid or expired",
    "code": 403
  }
}

// 402 - Usage Limit Exceeded
{
  "error": {
    "type": "payment_required",
    "message": "Monthly usage limit exceeded. Upgrade plan or wait for next cycle.",
    "code": 402,
    "details": {
      "pages_used": 2500,
      "pages_limit": 2500,
      "reset_date": "2025-02-01T00:00:00Z"
    }
  }
}
```

### **Processing Errors**
```json
// 400 - Invalid Image
{
  "error": {
    "type": "bad_request",
    "message": "Unable to process image: invalid format",
    "code": 400
  }
}

// 413 - Image Too Large
{
  "error": {
    "type": "payload_too_large", 
    "message": "Image size exceeds 25MB limit",
    "code": 413
  }
}

// 422 - Processing Failed
{
  "error": {
    "type": "unprocessable_entity",
    "message": "Vision model failed to process image",
    "code": 422
  }
}

// 500 - Server Error
{
  "error": {
    "type": "internal_server_error",
    "message": "Vision processing temporarily unavailable", 
    "code": 500
  }
}
```

## Configuration Reference

### **Environment Variables**

#### **Required**
```bash
SHIMMY_LICENSE_KEY=your-license-key-here
```

#### **Optional Vision Settings**
```bash
# Vision model configuration
SHIMMY_VISION_MODEL_PATH=/path/to/vision/model.gguf
SHIMMY_VISION_MODEL_DIR=/custom/models/directory

# Image processing limits
SHIMMY_VISION_MAX_LONG_EDGE=1920          # Max image dimension
SHIMMY_VISION_MAX_PIXELS=2500000          # Max total pixels
SHIMMY_VISION_MAX_FETCH_BYTES=26214400    # 25MB download limit

# Network settings  
SHIMMY_VISION_DOWNLOAD_TIMEOUT_SECS=30    # URL fetch timeout
SHIMMY_VISION_USER_AGENT="Custom-Agent"   # Custom user agent

# Performance tuning
SHIMMY_VISION_THREAD_COUNT=4              # Processing threads
SHIMMY_VISION_BATCH_SIZE=1                # Batch processing size

# Security settings
SHIMMY_VISION_ALLOW_PRIVATE_IPS=false     # Block private IP ranges
SHIMMY_VISION_ALLOWED_DOMAINS="example.com,trusted.com"  # Domain whitelist

# Debugging  
SHIMMY_VISION_TRACE=1                     # Enable detailed logging
RUST_LOG=shimmy_vision=debug              # Rust logging level
```

### **Server Configuration**
```bash
# Basic server settings
SHIMMY_BIND_ADDRESS=127.0.0.1:11435       # Server bind address
SHIMMY_MODEL_PATHS=/path/to/models         # Model search paths
RUST_LOG=info                             # General logging level

# CUDA settings (if using GPU)
CUDA_VISIBLE_DEVICES=0                    # GPU device selection
SHIMMY_GPU_LAYERS=35                      # Layers to offload to GPU
```

## Integration Examples

### **Python Integration**
```python
import requests
import base64

def analyze_image(image_path, prompt):
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode()
    
    response = requests.post('http://localhost:11435/api/vision', 
        headers={'Authorization': f'Bearer {license_key}'},
        json={
            'prompt': prompt,
            'image': f'data:image/jpeg;base64,{image_data}',
            'max_tokens': 500
        }
    )
    
    return response.json()

result = analyze_image('document.jpg', 'Extract all text as JSON')
print(result['choices'][0]['message']['content'])
```

### **Node.js Integration**
```javascript
const fs = require('fs');
const fetch = require('node-fetch');

async function processImage(imagePath, prompt) {
    const imageData = fs.readFileSync(imagePath, 'base64');
    
    const response = await fetch('http://localhost:11435/api/vision', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${process.env.SHIMMY_LICENSE_KEY}`
        },
        body: JSON.stringify({
            prompt: prompt,
            image: `data:image/jpeg;base64,${imageData}`,
            max_tokens: 500
        })
    });
    
    return await response.json();
}
```

### **cURL Examples**
```bash
# Basic image analysis
curl -X POST http://localhost:11435/api/vision \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $SHIMMY_LICENSE_KEY" \
  -d '{
    "prompt": "What is in this image?",
    "image_url": "https://example.com/image.jpg",
    "max_tokens": 300
  }'

# Streaming response
curl -X POST http://localhost:11435/api/vision \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $SHIMMY_LICENSE_KEY" \
  -d '{
    "prompt": "Describe this chart",
    "image": "data:image/png;base64,iVBOR...",
    "stream": true
  }'
```

## Rate Limits & Usage

### **Rate Limiting**
- **Requests**: 60 requests per minute per license
- **Concurrent**: 3 simultaneous requests per license  
- **Image Size**: 25MB maximum per image
- **Processing Time**: 30 seconds maximum per request

### **Usage Tracking**
- **Granularity**: Per-page processed (1 image = 1 page)
- **Reset**: Monthly, based on license creation date
- **Overages**: Blocked at limit, no additional charges
- **Monitoring**: Real-time usage via `/api/license/usage`

This API reference provides complete documentation for integrating Shimmy Vision into any application or workflow.---
applyTo: "**"
---
