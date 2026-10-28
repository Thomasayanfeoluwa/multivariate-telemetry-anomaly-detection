# SWaT Monitoring Frontend

This React, TypeScript, and Vite application provides a local monitoring interface for the SWaT historical-replay API. The frontend is a prototype; Vercel is the planned hosting target.

## Run locally

From this directory:

```powershell
npm ci
npm run dev
```

The API client defaults to `http://127.0.0.1:8000`. Set `VITE_API_BASE_URL` when the API is available at a different origin. Start the API separately as described in the root [README](../README.md).

## Checks

```powershell
npm run build
npm run lint
```

Automated frontend tests have not been added yet.
