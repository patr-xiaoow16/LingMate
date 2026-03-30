# LingMate Demo Deployment

This repo's root `frontend/` + `backend/` pair is suitable for a public demo.

## What this setup is for

- Public product demo
- Shareable link for feedback
- Mock lesson generation and in-memory progress

It is not meant for long-term multi-user production usage because backend state resets after service restarts.

## 1. Push this repo to GitHub

Render and Vercel both deploy most easily from a GitHub repository.

## 2. Deploy the backend on Render

This repo includes a ready-to-use [render.yaml](./render.yaml) blueprint for the demo backend.

### Option A: Blueprint deploy

1. In Render, choose `New` -> `Blueprint`.
2. Connect this GitHub repo.
3. Render will detect [render.yaml](./render.yaml).
4. Create the service.

### Option B: Manual deploy

If you prefer to set it up by hand:

- Runtime: `Python`
- Root Directory: `backend`
- Build Command: `python --version`
- Start Command: `python main.py`
- Health Check Path: `/api/health`

Environment variables:

- `HOST=0.0.0.0`
- `PORT=10000`
- `LINGMATE_ANALYSIS_PROVIDER=mock`

After deploy, copy the backend URL, for example:

`https://lingmate-demo-backend.onrender.com`

Your API base will then be:

`https://lingmate-demo-backend.onrender.com/api`

## 3. Deploy the frontend on Vercel

The frontend already includes SPA rewrite support in [frontend/vercel.json](./frontend/vercel.json).

In Vercel:

- Framework Preset: `Vite`
- Root Directory: `frontend`
- Build Command: `npm run build`
- Output Directory: `dist`

Set this environment variable before deploying:

- `VITE_API_BASE=https://your-render-backend.onrender.com/api`

Replace the value with your actual Render backend URL.

## 4. Verify the public demo

After both services are live:

1. Open the Vercel URL.
2. Paste any valid `http` or `https` link on the home page.
3. Confirm the app can open:
   - `/analysis/:lessonId`
   - `/workspace/:lessonId`
   - `/review/:lessonId`
4. Refresh those pages directly to confirm SPA rewrites work correctly.

## Notes

- The demo backend allows cross-origin requests from any origin.
- Lesson data is stored only in memory.
- If Render restarts the service, demo progress resets.
