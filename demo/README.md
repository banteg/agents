# Creator Vaults Demo

A minimal, beautiful web experience showing why creator coins behave like memecoins.

## What it is

- Single HTML file, no build step
- 4:30 audio track with synced visual scenes
- Real data from $JESSE and $thenickshirley token launches
- 8 scenes that activate based on playback time
- Mobile responsive
- Ready to deploy anywhere

## Local testing

```bash
# Option 1: Python
python3 -m http.server 8000

# Option 2: Node
npx serve

# Then open: http://localhost:8000
```

## Deploy to Vercel (demo.creatorvaults.fun)

```bash
# Install Vercel CLI if needed
npm i -g vercel

# Deploy
cd /home/akitav2/projects/agents/demo
vercel

# Follow prompts:
# - Link to existing project or create new
# - Set project name: creatorvaults-demo
# - Set domain: demo.creatorvaults.fun
```

## Deploy to any static host

Just upload `index.html` to:
- Netlify (drag & drop)
- Vercel
- GitHub Pages
- S3 + CloudFront
- Any static host

## Audio file

Currently hosted at:
```
https://assets.creatorvaults.fun/audio/creatorvaults_FINAL_music_finishes.mp3
```

To self-host:
1. Place audio file in same directory as index.html
2. Update src in HTML: `<source src="./creatorvaults_FINAL_music_finishes.mp3">`

## Features

- ✅ Plays 4:30 audio track
- ✅ 8 synced scenes (Thesis → Mechanism → Pattern → Jesse → Curve → Turn → Vaults → Close)
- ✅ Real data: $JESSE (73-87% decline), $thenickshirley (73% decline)
- ✅ Links to DexScreener for verification
- ✅ Timeline scrubber for navigation
- ✅ Minimal, cinematic design
- ✅ Mobile responsive
- ✅ No JavaScript framework needed
- ✅ No build step

## Data sources

All data is real and verifiable:
- $JESSE: https://dexscreener.com/base/0xc39acb3ce11ebcd3e1c5d67cdfb8707ab12674449fdab859327a8aabee03cd10
- $thenickshirley: https://dexscreener.com/base/0x2ad29751705d81aeb0aa31987d17fe76b0c88d3c038c0a198f3c7bf8c1f2b750
- Empirical data from Base chain, November 2025 - January 2026

## File structure

```
demo/
├── index.html          ← The entire app (self-contained)
└── README.md          ← This file
```

That's it. One file. No dependencies.

## Customization

All styling is in the `<style>` tag. Key variables:
- Background: `#000`
- Text: `#fff`
- Accent: `rgba(255,255,255,0.4)`
- Border: `rgba(255,255,255,0.1)`

Scenes are in `<div class="scene">` elements with `data-start` and `data-end` attributes (in seconds).

## Browser support

Works in all modern browsers. Requires:
- HTML5 `<audio>`
- ES6 JavaScript
- CSS Grid

## License

Use however you want.

