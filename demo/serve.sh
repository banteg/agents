#!/bin/bash

echo "🎬 Creator Vaults Demo"
echo ""
echo "Starting local server..."
echo ""
echo "Open: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop"
echo ""

cd "$(dirname "$0")"

# Try different server options
if command -v python3 &> /dev/null; then
    python3 -m http.server 3000
elif command -v python &> /dev/null; then
    python -m SimpleHTTPServer 3000
elif command -v npx &> /dev/null; then
    npx serve -l 3000
else
    echo "No server found. Install Node.js or Python."
    exit 1
fi

