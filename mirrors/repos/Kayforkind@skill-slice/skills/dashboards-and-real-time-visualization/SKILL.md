---
name: dashboards-and-real-time-visualization
description: "Engineers live telemetry views: pick SVG/Canvas2D/WebGL by mark count, cap a ring buffer, ingest WebSockets off the React render path, downsample with LTTB, scale for devicePixelRatio, and flag stale streams. Pick this chair when shipping live charts, incident canvases, brush-linked analytics, or bandwidth-tight field dashboards. Not for static quarterly BI decks or batch ETL with no socket."
version: 1.0.1
risk: safe
source: modernized
date_modernized: "2026-05-31"
tags:
  - dashboard
  - real-time
  - streaming
  - data-visualization
tools:
  - gemini
  - codex
---

# Dashboards and Real-Time Visualization

## Overview

This skill covers the design, engineering, and performance optimization of real-time streaming dashboards and telemetry visualization interfaces. In operational environments, a dashboard is a complex system subject to hardware, network, and layout constraints. This skill provides instructions on managing high-frequency updates, optimizing layout scanning paths, choosing rendering engines, and implementing responsive interactions.

### Sources Checked (2026-05-31)

- D3 official documentation: https://d3js.org/
- Observable Plot: https://observablehq.com/plot/
- W3C WCAG 2.2: https://www.w3.org/TR/WCAG22/

### Reclassification Note

- Suggested modernized category: AI-ML-Data-Science/Data-Visualization

---

## When to Use

Use this skill when designing or implementing:

1. **WebSocket-Driven Telemetry Visualizers** — Live charts consuming high-frequency data streams (e.g., server resource usage, IoT sensors, trade feeds).
2. **Incident Response Dashboards** — Interfaces built for rapid anomaly detection, historical comparisons, and incident triage.
3. **Cross-Filtered Analytics Views** — Coordinated dashboards where selecting a region on one chart dynamically filters three other charts.
4. **Resource-Constrained Mobile Views** — Dashboards optimized for operators in the field with low bandwidth, high battery drain constraints, and touch interactions.

**Trigger keywords:** real-time dashboard, live visualization, streaming chart, WebSocket telemetry, Canvas chart, ring buffer, LTTB downsampling, incident response dashboard, cross-filtered analytics.

---

## Prerequisites

- Node.js 18+ and a modern browser (Chrome 110+, Firefox 110+, Safari 16+) for Canvas/WebSocket APIs.
- TypeScript 5+ recommended for type-safe buffer and streaming implementations.
- Familiarity with `requestAnimationFrame`, Canvas2D API, and WebSocket lifecycle events.
- For Windows hosts (PowerShell primary): ensure line endings are LF in source files to avoid git checkout issues — run `git config core.autocrlf false` in the repo root.

---

## Procedure

### 1. Choose the Rendering Engine

The rendering engine is the most critical decision for dashboard stability. Match the engine to the expected data volume and interaction model.

| Parameter | SVG (D3, Recharts) | Canvas2D (Chart.js) | WebGL (deck.gl, Three.js) |
| :--- | :--- | :--- | :--- |
| **Max Marks (Stable)** | ~1,000 DOM elements | ~50,000 pixels/shapes | 500,000+ coordinates |
| **CPU Overhead** | High (Repaints DOM tree) | Medium (Redraws static pixels) | Low (Delegates to GPU) |
| **GPU Acceleration** | Minimal (Browser dependent) | Moderate (Hardware accelerated raster) | Maximum (Direct shader pipeline) |
| **Event Listeners** | Native (`onClick` directly) | Manual (Calculate coordinates on tap) | Manual (Raycasting) |
| **Accessibility (DOM)** | Excellent (Screen readers scan tags) | None (Requires hidden ARIA fallback table) | None (Requires hidden ARIA fallback table) |
| **Best Operational Use** | Clean, interactive metrics tables | High-frequency CPU timeline charts | Spatial maps, network graphs, IoT nodes |

**Decision rule:**
- ≤ 1,000 marks and native accessibility required → SVG.
- 1,000–50,000 marks, high-frequency updates → Canvas2D.
- 50,000+ marks or spatial/geospatial → WebGL.

> [!WARNING]
> Do not use SVG paths to render datasets exceeding 2,000 points. The browser's layout recalculation and DOM rendering system will choke, dropping the viewport frame rate below 10 frames per second.

### 2. Implement a Ring Buffer for Memory Management

Never append data to arrays infinitely. Establish a maximum window size (e.g., last 500 points) and use a circular queue (ring buffer) to drop old points.

```typescript
export interface DataPoint {
  timestamp: number;
  value: number;
}

export class CircularBuffer {
  private buffer: DataPoint[];
  private head = 0;
  private tail = 0;
  private size = 0;
  private readonly capacity: number;

  constructor(capacity: number) {
    this.capacity = capacity;
    this.buffer = new Array<DataPoint>(capacity);
  }

  public push(point: DataPoint): void {
    this.buffer[this.head] = point;
    this.head = (this.head + 1) % this.capacity;

    if (this.size === this.capacity) {
      this.tail = (this.tail + 1) % this.capacity;
    } else {
      this.size++;
    }
  }

  public toArray(): DataPoint[] {
    const result: DataPoint[] = [];
    let idx = this.tail;
    for (let i = 0; i < this.size; i++) {
      result.push(this.buffer[idx]);
      idx = (idx + 1) % this.capacity;
    }
    return result;
  }

  public isFull(): boolean {
    return this.size === this.capacity;
  }

  public clear(): void {
    this.head = 0;
    this.tail = 0;
    this.size = 0;
  }
}
```

### 3. Separate Raw Data Streams from Render State

Keep incoming data streams in raw queues. Do not trigger React state updates for every single packet. Pull data from the queue at a throttled interval (e.g., 60fps / 16.6ms) for rendering.

**Pattern:**
1. WebSocket `onmessage` → push to `bufferRef.current` (no `setState`).
2. `requestAnimationFrame` loop → read `bufferRef.current.toArray()` → draw to canvas.
3. Only call `setState` for lightweight UI metadata (connection status, last value).

### 4. Implement the WebSocket Streaming Component

Below is a Canvas-based real-time line chart in React. It renders a grid, coordinates drawing tasks, and handles disconnection and stale data indicators.

```tsx
import React, { useEffect, useRef, useState } from 'react';
import { CircularBuffer, DataPoint } from './CircularBuffer';

interface RealTimeChartProps {
  wsUrl: string;
  maxPoints?: number;
}

export const RealTimeChart: React.FC<RealTimeChartProps> = ({ wsUrl, maxPoints = 300 }) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const bufferRef = useRef<CircularBuffer>(new CircularBuffer(maxPoints));
  const [connectionStatus, setConnectionStatus] = useState<'CONNECTED' | 'DISCONNECTED'>('DISCONNECTED');
  const [lastValue, setLastValue] = useState<number | null>(null);

  useEffect(() => {
    const ws = new WebSocket(wsUrl);
    ws.onopen = () => setConnectionStatus('CONNECTED');
    ws.onclose = () => setConnectionStatus('DISCONNECTED');
    ws.onerror = () => setConnectionStatus('DISCONNECTED');

    ws.onmessage = (event) => {
      const parsedData = JSON.parse(event.data);
      const point: DataPoint = {
        timestamp: parsedData.timestamp || Date.now(),
        value: parsedData.value
      };
      bufferRef.current.push(point);
      setLastValue(point.value);
    };

    return () => ws.close();
  }, [wsUrl]);

  // Render loop using requestAnimationFrame
  useEffect(() => {
    let animationId: number;

    const render = () => {
      const canvas = canvasRef.current;
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      if (!ctx) return;

      const data = bufferRef.current.toArray();
      const width = canvas.width;
      const height = canvas.height;

      // Clear canvas with dark layout background
      ctx.fillStyle = '#0a0a0a';
      ctx.fillRect(0, 0, width, height);

      if (data.length < 2) {
        ctx.fillStyle = '#737373';
        ctx.font = '12px monospace';
        ctx.fillText('WAITING FOR TELEMETRY...', 20, 30);
        animationId = requestAnimationFrame(render);
        return;
      }

      // Draw grid
      ctx.strokeStyle = '#262626';
      ctx.lineWidth = 1;
      for (let x = 0; x < width; x += 50) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, height);
        ctx.stroke();
      }
      for (let y = 0; y < height; y += 40) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
      }

      // Map values to coordinates
      const minVal = Math.min(...data.map(p => p.value));
      const maxVal = Math.max(...data.map(p => p.value));
      const range = maxVal - minVal || 1;

      ctx.strokeStyle = connectionStatus === 'CONNECTED' ? '#10b981' : '#ef4444';
      ctx.lineWidth = 2;
      ctx.beginPath();

      for (let i = 0; i < data.length; i++) {
        const x = (i / (data.length - 1)) * width;
        const y = height - ((data[i].value - minVal) / range) * (height - 40) - 20;

        if (i === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
      }
      ctx.stroke();

      animationId = requestAnimationFrame(render);
    };

    render();
    return () => cancelAnimationFrame(animationId);
  }, [connectionStatus]);

  return (
    <div className="w-full bg-neutral-950 p-6 border border-neutral-800">
      <div className="flex items-center justify-between mb-4">
        <div>
          <span className="text-xs font-mono text-neutral-400 uppercase">SYS_TELEMETRY</span>
          <h2 className="text-3xl font-light text-neutral-100 mt-1">
            {lastValue !== null ? lastValue.toFixed(2) : '--.--'}
          </h2>
        </div>
        <div className="flex items-center gap-2">
          <span className={`w-2.5 h-2.5 rounded-full ${connectionStatus === 'CONNECTED' ? 'bg-emerald-500' : 'bg-red-500'}`} />
          <span className="text-xs font-mono text-neutral-400">{connectionStatus}</span>
        </div>
      </div>
      <canvas ref={canvasRef} width={600} height={300} className="w-full aspect-[2/1] bg-neutral-900" />
    </div>
  );
};
```

### 5. Apply Downsampling for Long Histories (LTTB)

If visualizing long histories, use the Largest Triangle Three Buckets (LTTB) downsampling algorithm to reduce a 100,000 point series to 1,000 points before passing it to the drawing engine.

- LTTB preserves visual shape better than naive every-Nth sampling.
- Downsample on the worker thread if the series exceeds 10,000 points to avoid blocking the render loop.

### 6. Batch Canvas Drawing Calls

> [!TIP]
> Group multiple canvas drawing operations into a single path call (`beginPath()`, loop `lineTo()`, `stroke()`) instead of calling `stroke()` inside a loop. Drawing lines as a single batch operation is up to 50 times faster.

### 7. Handle High-DPI Displays

HTML5 canvas elements look blurry on Retina displays if they are not scaled by the system's `window.devicePixelRatio`. Always adjust the canvas backing store size to match pixel ratios.

```typescript
const dpr = window.devicePixelRatio || 1;
canvas.width = displayWidth * dpr;
canvas.height = displayHeight * dpr;
canvas.style.width = `${displayWidth}px`;
canvas.style.height = `${displayHeight}px`;
ctx.scale(dpr, dpr);
```

### 8. Handle Tab Backgrounding

Browsers throttle or freeze `requestAnimationFrame` loops when a tab is hidden in the background. Sockets can buffer data or overflow. Use the Page Visibility API (`document.hidden`) to pause WebSocket feeds or clear buffers when tabs are inactive.

```typescript
document.addEventListener('visibilitychange', () => {
  if (document.hidden) {
    ws.close(); // or pause feeding
    bufferRef.current.clear();
  } else {
    // reconnect
  }
});
```

### 9. Sort Out-of-Order Packets

Network packets from WebSockets can arrive out of chronological order. Verify and sort timestamps on insertion to the circular buffer to prevent lines from drawing backward.

### 10. Implement Coordinated Views and Progressive Disclosure

1. **Overview First, Detail on Demand** — Display general statuses as micro-charts (sparklines). Allow the user to click to expand a full-resolution time chart.
2. **Brush and Link** — Selecting a specific time range in a master timeline must automatically apply identical time-range filters to all secondary metrics on the page.
3. **Active Annotation** — Overlay vertical marker lines on charts corresponding to system events (e.g., "Build #104 Deployed" or "Node Restarted") to give context to telemetry spikes.

### 11. Indicate Stale Data

> [!IMPORTANT]
> When rendering data that has stopped streaming (e.g., server offline), do not leave the chart flatlining as if values are normal. Change the line color to neutral grey and overlay a prominent "DATA STREAM STALE" alert box on the canvas.

---

## Pitfalls

### Anti-Patterns to Avoid

- **The Garbage Collector Avalanche**: Allocating new JavaScript objects or arrays for every incoming WebSocket packet. This causes frequent garbage collection pauses, making charts stutter. Always reuse objects or write to fixed buffers.
- **The Equal-Weight Grid**: Layouts that present 20 metrics tiles in identical square shapes. Users cannot focus on critical telemetry if everything carries equal visual weight. Create a primary focal timeline.
- **Hover-Dependent Actions**: Hiding critical details (like warning text or exact values) behind hover states. Touch-screen mobile operators cannot hover over elements.
- **Ambient Glow Clutter**: Adding heavy CSS animations, drop shadows, or blinking effects to normal status indicators. Limit motion and highlights strictly to warnings and critical errors.

### Edge Cases

- **Tab Backgrounding**: `requestAnimationFrame` freezes when tabs are hidden. Sockets may buffer and overflow. Use Page Visibility API to pause/clear.
- **Out-of-Order Packets**: WebSocket packets can arrive out of chronological order. Sort timestamps on insertion to prevent backward-drawing lines.
- **High-DPI Canvas Blur**: Canvas elements blur on Retina displays if not scaled by `window.devicePixelRatio`. Always adjust the backing store size.
- **SVG Overload**: SVG paths exceeding 2,000 points will drop frame rate below 10 FPS due to DOM layout recalculation.

---

## Verification

### Architecture Verification Checklist

- [ ] Has the telemetry buffer capacity been capped to prevent browser tab out-of-memory (OOM) crashes?
- [ ] Does the connection manager implement an exponential backoff reconnect algorithm when WebSocket connections drop?
- [ ] Are raw metrics downsampled before rendering charts containing over 5,000 data points?
- [ ] Is the repaint budget strictly checked? Ensure canvas drawing calls take less than 12ms inside `requestAnimationFrame`.

### Usability & Scanning Checklist

- [ ] Are labels, status values, and unit tags readable without interactive hovers?
- [ ] Does the interface clearly indicate when data is stale (e.g., if no socket packet has been received for 10 seconds)?
- [ ] Are the critical alert thresholds drawn as static horizontal marker lines directly on the chart plane?

### Runtime Checks

1. **Memory leak check** — Open DevTools → Memory tab → take heap snapshot, let dashboard run for 5 minutes, take another snapshot. Heap should not grow beyond the ring buffer capacity.
2. **Frame rate check** — Open DevTools → Performance → Record 10 seconds while streaming. Confirm `requestAnimationFrame` callbacks stay under 16.6ms and no long tasks exceed 50ms.
3. **Stale data check** — Disconnect the WebSocket server. Confirm the chart line turns grey and a "DATA STREAM STALE" alert appears within the expected timeout window (e.g., 10 seconds).
4. **Background tab check** — Switch to another browser tab for 30 seconds, return. Confirm no buffer overflow or backward-drawing lines. Buffer should have been cleared or paused.
5. **High-DPI check** — Open on a Retina/4K display. Confirm canvas lines and text are crisp, not blurry.

---

## Related Skills

- [[frontend-design]] — layout styling and minimalism guidelines
- [[scroll-experience]] — canvas rendering techniques and animations
- [[ui-ux-pro-max]] — data visualization accessibility standards
- [[react-best-practices]] — React hooks and performance optimization guidelines
