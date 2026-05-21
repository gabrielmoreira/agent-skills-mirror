#!/bin/bash
cd "$(dirname "$0")"

echo "Installing pipeline dependencies..."
npm install

echo "Running OpenClaw Twitter Jobs Radar..."
npx ts-node src/index.ts
