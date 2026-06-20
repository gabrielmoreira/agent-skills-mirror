# Web Unblocker Code Examples

## cURL

**Basic request:**
```bash
curl -k -x "https://unblock.oxylabs.io:60000" \
  -U "$OXYLABS_USERNAME:$OXYLABS_PASSWORD" \
  "https://example.com"
```

**With JavaScript rendering:**
```bash
curl -k -x "https://unblock.oxylabs.io:60000" \
  -U "$OXYLABS_USERNAME:$OXYLABS_PASSWORD" \
  -H "x-oxylabs-render: html" \
  "https://example.com/dynamic-page"
```

**With geo-location and session:**
```bash
curl -k -x "https://unblock.oxylabs.io:60000" \
  -U "$OXYLABS_USERNAME:$OXYLABS_PASSWORD" \
  -H "X-Oxylabs-Geo-Location: United States" \
  -H "X-Oxylabs-Session-Id: session123" \
  "https://example.com"
```

**Screenshot as PNG:**
```bash
curl -k -x "https://unblock.oxylabs.io:60000" \
  -U "$OXYLABS_USERNAME:$OXYLABS_PASSWORD" \
  -H "x-oxylabs-render: png" \
  "https://example.com" -o screenshot.png
```

## Python

```python
import requests
import os

proxies = {
    "http": f"http://{os.environ['OXYLABS_USERNAME']}:{os.environ['OXYLABS_PASSWORD']}@unblock.oxylabs.io:60000",
    "https": f"https://{os.environ['OXYLABS_USERNAME']}:{os.environ['OXYLABS_PASSWORD']}@unblock.oxylabs.io:60000"
}

# Basic request
response = requests.get(
    "https://example.com",
    proxies=proxies,
    verify=False  # Required for Web Unblocker
)
print(response.text)
```

**With headers:**
```python
import requests
import os

proxies = {
    "https": f"https://{os.environ['OXYLABS_USERNAME']}:{os.environ['OXYLABS_PASSWORD']}@unblock.oxylabs.io:60000"
}

headers = {
    "x-oxylabs-render": "html",
    "X-Oxylabs-Geo-Location": "Germany"
}

response = requests.get(
    "https://example.com",
    proxies=proxies,
    headers=headers,
    verify=False
)
print(response.text)
```

## Node.js

```javascript
const fetch = require("node-fetch");
const HttpsProxyAgent = require("https-proxy-agent");

const username = process.env.OXYLABS_USERNAME;
const password = process.env.OXYLABS_PASSWORD;

const agent = new HttpsProxyAgent(
  `https://${username}:${password}@unblock.oxylabs.io:60000`
);

// Disable TLS verification
process.env.NODE_TLS_REJECT_UNAUTHORIZED = "0";

async function fetchPage() {
  const response = await fetch("https://example.com", {
    agent,
    headers: {
      "x-oxylabs-render": "html"
    }
  });
  const html = await response.text();
  console.log(html);
}

fetchPage();
```

## PHP

```php
<?php
$username = getenv('OXYLABS_USERNAME');
$password = getenv('OXYLABS_PASSWORD');

$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, "https://example.com");
curl_setopt($ch, CURLOPT_PROXY, "https://unblock.oxylabs.io:60000");
curl_setopt($ch, CURLOPT_PROXYUSERPWD, "$username:$password");
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    "x-oxylabs-render: html"
]);

$response = curl_exec($ch);
curl_close($ch);

echo $response;
?>
```

## Go

```go
package main

import (
    "fmt"
    "io"
    "net/http"
    "net/url"
    "os"
    "crypto/tls"
)

func main() {
    username := os.Getenv("OXYLABS_USERNAME")
    password := os.Getenv("OXYLABS_PASSWORD")

    proxyURL, _ := url.Parse(fmt.Sprintf(
        "https://%s:%s@unblock.oxylabs.io:60000",
        username, password,
    ))

    transport := &http.Transport{
        Proxy: http.ProxyURL(proxyURL),
        TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
    }

    client := &http.Client{Transport: transport}

    req, _ := http.NewRequest("GET", "https://example.com", nil)
    req.Header.Set("x-oxylabs-render", "html")

    resp, _ := client.Do(req)
    defer resp.Body.Close()

    body, _ := io.ReadAll(resp.Body)
    fmt.Println(string(body))
}
```

## Java

```java
import java.net.*;
import java.io.*;

public class WebUnblocker {
    public static void main(String[] args) throws Exception {
        String username = System.getenv("OXYLABS_USERNAME");
        String password = System.getenv("OXYLABS_PASSWORD");

        Proxy proxy = new Proxy(Proxy.Type.HTTP,
            new InetSocketAddress("unblock.oxylabs.io", 60000));

        Authenticator.setDefault(new Authenticator() {
            protected PasswordAuthentication getPasswordAuthentication() {
                return new PasswordAuthentication(username, password.toCharArray());
            }
        });

        URL url = new URL("https://example.com");
        HttpURLConnection conn = (HttpURLConnection) url.openConnection(proxy);
        conn.setRequestProperty("x-oxylabs-render", "html");

        BufferedReader reader = new BufferedReader(
            new InputStreamReader(conn.getInputStream()));
        String line;
        while ((line = reader.readLine()) != null) {
            System.out.println(line);
        }
        reader.close();
    }
}
```
