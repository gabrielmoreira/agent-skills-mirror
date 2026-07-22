# Request/Response Examples

## Universal URL Scraping

**Request:**
```bash
curl -X POST 'https://realtime.oxylabs.io/v1/queries' \
  -u "$OXY_WSA_USERNAME:$OXY_WSA_PASSWORD" \
  -H 'Content-Type: application/json' \
  -d '{
    "source": "universal",
    "url": "https://example.com"
  }'
```

**Response:**
```json
{
  "results": [{
    "content": "<!DOCTYPE html><html>...</html>",
    "created_at": "2024-01-15T10:30:00.000Z",
    "updated_at": "2024-01-15T10:30:01.000Z",
    "page": 1,
    "url": "https://example.com",
    "job_id": "7654321",
    "status_code": 200
  }]
}
```

## Google Search with Parsing

**Request:**
```bash
curl -X POST 'https://realtime.oxylabs.io/v1/queries' \
  -u "$OXY_WSA_USERNAME:$OXY_WSA_PASSWORD" \
  -H 'Content-Type: application/json' \
  -d '{
    "source": "google_search",
    "query": "best wireless headphones",
    "geo_location": "United States",
    "parse": true
  }'
```

**Response (parsed):**
```json
{
  "results": [{
    "content": {
      "results": {
        "organic": [
          {
            "pos": 1,
            "url": "https://example.com/headphones",
            "title": "Best Wireless Headphones 2024",
            "desc": "Our top picks for wireless headphones..."
          }
        ],
        "paid": [...],
        "knowledge": {...}
      }
    },
    "status_code": 200
  }]
}
```

## Amazon Product

**Request:**
```bash
curl -X POST 'https://realtime.oxylabs.io/v1/queries' \
  -u "$OXY_WSA_USERNAME:$OXY_WSA_PASSWORD" \
  -H 'Content-Type: application/json' \
  -d '{
    "source": "amazon_product",
    "query": "B07FZ8S74R",
    "geo_location": "90210",
    "parse": true
  }'
```

**Response (parsed):**
```json
{
  "results": [{
    "content": {
      "title": "Echo Dot (3rd Gen)",
      "price": 29.99,
      "currency": "USD",
      "rating": 4.7,
      "reviews_count": 845234,
      "availability": "In Stock",
      "seller": "Amazon.com",
      "categories": ["Electronics", "Smart Home"],
      "images": ["https://..."],
      "description": "..."
    },
    "status_code": 200
  }]
}
```

## Amazon Search

**Request:**
```bash
curl -X POST 'https://realtime.oxylabs.io/v1/queries' \
  -u "$OXY_WSA_USERNAME:$OXY_WSA_PASSWORD" \
  -H 'Content-Type: application/json' \
  -d '{
    "source": "amazon_search",
    "query": "wireless mouse",
    "geo_location": "10001",
    "parse": true
  }'
```

**Response (parsed):**
```json
{
  "results": [{
    "content": {
      "results": {
        "organic": [
          {
            "pos": 1,
            "asin": "B07CGKQLWG",
            "title": "Logitech M510 Wireless Mouse",
            "price": 24.99,
            "rating": 4.6,
            "reviews_count": 52341
          }
        ]
      }
    },
    "status_code": 200
  }]
}
```

## JavaScript Rendering

For pages that require JavaScript execution:

**Request:**
```bash
curl -X POST 'https://realtime.oxylabs.io/v1/queries' \
  -u "$OXY_WSA_USERNAME:$OXY_WSA_PASSWORD" \
  -H 'Content-Type: application/json' \
  -d '{
    "source": "universal",
    "url": "https://example.com/spa-page",
    "render": "html"
  }'
```

## Geo-Location Examples

**For search engines (country/state/city):**
```json
{
  "source": "google_search",
  "query": "coffee shops",
  "geo_location": "New York,New York,United States"
}
```

**For US e-commerce (ZIP code):**
```json
{
  "source": "amazon_product",
  "query": "B07FZ8S74R",
  "geo_location": "90210"
}
```

**For international e-commerce (country):**
```json
{
  "source": "amazon_product",
  "query": "B07FZ8S74R",
  "geo_location": "Germany"
}
```

## Custom Headers

**Request:**
```bash
curl -X POST 'https://realtime.oxylabs.io/v1/queries' \
  -u "$OXY_WSA_USERNAME:$OXY_WSA_PASSWORD" \
  -H 'Content-Type: application/json' \
  -d '{
    "source": "universal",
    "url": "https://example.com",
    "context": [
      {
        "key": "headers",
        "value": {
          "Accept-Language": "de-DE",
          "Custom-Header": "value"
        }
      }
    ]
  }'
```

## Browser Instructions

For complex interactions (clicking, scrolling, waiting):

**Request:**
```bash
curl -X POST 'https://realtime.oxylabs.io/v1/queries' \
  -u "$OXY_WSA_USERNAME:$OXY_WSA_PASSWORD" \
  -H 'Content-Type: application/json' \
  -d '{
    "source": "universal",
    "url": "https://example.com",
    "render": "html",
    "browser_instructions": [
      {"type": "click", "selector": "button.load-more"},
      {"type": "wait", "wait_time_s": 2},
      {"type": "scroll", "direction": "down", "pixels": 500}
    ]
  }'
```


## Walmart Product

**Request:**
```bash
curl -X POST 'https://realtime.oxylabs.io/v1/queries' \
  -u "$OXY_WSA_USERNAME:$OXY_WSA_PASSWORD" \
  -H 'Content-Type: application/json' \
  -d '{
    "source": "walmart_product",
    "query": "123456789",
    "parse": true
  }'
```

## Error Response

**Request with invalid source:**
```json
{
  "source": "invalid_source",
  "url": "https://example.com"
}
```

**Response:**
```json
{
  "error": {
    "code": "INVALID_SOURCE",
    "message": "Source 'invalid_source' is not supported"
  }
}
```

## Python Example

```python
import requests
import os

response = requests.post(
    "https://realtime.oxylabs.io/v1/queries",
    auth=(os.environ["OXY_WSA_USERNAME"], os.environ["OXY_WSA_PASSWORD"]),
    json={
        "source": "amazon_product",
        "query": "B07FZ8S74R",
        "parse": True
    }
)

data = response.json()
product = data["results"][0]["content"]
print(f"Title: {product['title']}")
print(f"Price: ${product['price']}")
```

## JavaScript/Node.js Example

```javascript
const response = await fetch("https://realtime.oxylabs.io/v1/queries", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "Authorization": "Basic " + btoa(`${process.env.OXY_WSA_USERNAME}:${process.env.OXY_WSA_PASSWORD}`)
  },
  body: JSON.stringify({
    source: "google_search",
    query: "web scraping",
    parse: true
  })
});

const data = await response.json();
console.log(data.results[0].content);
```
