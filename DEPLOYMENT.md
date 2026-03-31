# Deployment Guide — copom-streamlit

The Streamlit app is hosted on [Streamlit Community Cloud](https://streamlit.io/cloud) (free).
It connects to the `copom-rag-api` backend hosted on Render.

---

## Production Stack

| Component | Service | URL |
|-----------|---------|-----|
| Frontend hosting | [Streamlit Community Cloud](https://share.streamlit.io) (free) | `https://copom-rag.streamlit.app` |
| Backend API | Render (`copom-rag-api`) | `https://copom-rag-api.onrender.com` |

---

## Streamlit Cloud Configuration

| Setting | Value |
|---------|-------|
| Repository | `MateusRestier/copom-streamlit` |
| Branch | `main` |
| Main file | `app.py` |
| Python version | 3.11 |
| Dependencies | `requirements.txt` |

---

## Secrets (Environment Variables)

Secrets are set in the Streamlit Cloud dashboard and are never stored in the repository.

| Variable | Description |
|----------|-------------|
| `COPOM_API_URL` | Full URL of the backend API, e.g. `https://copom-rag-api.onrender.com` |
| `COPOM_API_KEY` | Leave empty if API auth is disabled; set to the `COPOM_API_KEY` value from Render if auth is enabled |

---

## Updating Secrets

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Find the app `copom-rag` → click the **⋮** menu → **Settings**
3. Go to the **Secrets** tab
4. Edit the TOML content and click **Save**
5. The app restarts automatically within ~1 minute

Example secrets file (TOML format):
```toml
COPOM_API_URL = "https://copom-rag-api.onrender.com"
COPOM_API_KEY = ""
```

---

## Updating the API URL

If the Render service URL changes (e.g. after recreating the service):

1. Go to Streamlit Cloud → app settings → Secrets
2. Update `COPOM_API_URL` to the new URL
3. Save — the app restarts automatically

---

## Auto-Deploy

Streamlit Cloud redeploys automatically on every push to the `main` branch of
`MateusRestier/copom-streamlit`. No manual action needed after a code change.

---

## Manual Reboot

If the app is stuck or behaving unexpectedly:

1. [share.streamlit.io](https://share.streamlit.io) → app `copom-rag`
2. Click **⋮** → **Reboot app**

---

## Keep-Alive Strategy

### Problem

Both free-tier services sleep on inactivity:

| Service | Sleep trigger | Wake-up cost |
|---------|--------------|--------------|
| Streamlit Community Cloud | **12 h** without a visitor | ~30 s (user sees a "wake up" button) |
| Render (copom-rag-api) | 15 min without a request | 30–60 s cold start on first request |

### Solution

**Render** is kept alive by **UptimeRobot**, which pings the `/health` endpoint every 14 minutes.

**Both services** are additionally covered by a **GitHub Actions scheduled workflow**
(`.github/workflows/keep-alive.yml`) that pings the Render API and the Streamlit app
**6 times a day, every 4 hours** — well within the 12-hour sleep window even accounting
for the natural scheduler delay (~30 min) of GitHub Actions:

| BRT | UTC cron |
|-----|----------|
| 00:00 | `0 3 * * *` |
| 04:00 | `0 7 * * *` |
| 08:00 | `0 11 * * *` |
| 12:00 | `0 15 * * *` |
| 16:00 | `0 19 * * *` |
| 20:00 | `0 23 * * *` |

The Streamlit ping uses `curl --max-redirs 3` (no `-L`) to avoid the infinite redirect loop
that Streamlit triggers on headless requests. The Render ping uses `curl -f --max-time 90`
against the `/health` endpoint. Since the repo is public, GitHub Actions minutes are free
and unlimited.

### Required GitHub Secrets

| Secret | Value |
|--------|-------|
| `STREAMLIT_URL` | `https://copom-rag.streamlit.app` |
| `RENDER_URL` | `https://copom-rag-api.onrender.com` |

Set them at: **GitHub → repo Settings → Secrets and variables → Actions → New repository secret**.

---

## Troubleshooting

### "Nao foi possivel conectar a API"

The backend API on Render is asleep (free tier spins down after 15 minutes of inactivity).
The first request after a sleep period takes 30–60 seconds. Wait and try again.

To prevent this, set up UptimeRobot to ping the API every 14 minutes
(see [copom-rag-api DEPLOYMENT.md](../copom-rag-api/DEPLOYMENT.md#free-tier-limitations)).

### "Error installing requirements" on deploy

Streamlit Cloud uses `requirements.txt` for dependencies. Make sure the file exists in the
repo root and contains all required packages. Do not rely solely on `pyproject.toml` —
Streamlit Cloud may try to use Poetry with it, which will fail.

### App shows stale data

The app does not cache API responses. If the data looks outdated, the issue is in the
database — run a new ingestion from `copom-vector-pipeline`.
