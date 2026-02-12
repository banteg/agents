# Deploy to demo.creatorvaults.fun

## Quick Deploy (Vercel)

```bash
cd /home/akitav2/projects/agents/demo
npx vercel --prod
```

When prompted:
- Project name: `creatorvaults-demo`
- Domain: `demo.creatorvaults.fun` (set in Vercel dashboard)

That's it!

---

## Alternative: Manual Deploy

### GitHub Pages

1. Create repo: `creatorvaults-demo`
2. Push this directory
3. Enable Pages in repo settings
4. Point `demo.creatorvaults.fun` CNAME to `<username>.github.io`

### Netlify

1. Drag the `demo` folder to Netlify
2. Set custom domain: `demo.creatorvaults.fun`

### Any Static Host

Upload `index.html` to any static file host. That's the entire app.

---

## DNS Setup (if needed)

Point `demo.creatorvaults.fun` to your host:

**Vercel:**
```
CNAME demo cname.vercel-dns.com.
```

**Netlify:**
```
CNAME demo <your-site>.netlify.app.
```

**GitHub Pages:**
```
CNAME demo <username>.github.io.
```

---

## Test Locally

```bash
./serve.sh

# Then open: http://localhost:3000
```

---

##Done!

The demo is a single HTML file. No build, no dependencies, no backend.

Just deploy and go.

