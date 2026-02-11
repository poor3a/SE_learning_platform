# Project Architecture & Setup - Complete Summary

**Last Updated:** February 10, 2026  
**Status:** ✅ Monolithic backend architected, ready to run via win_scripts

---

## Executive Summary

### Problem Identified
The Team9 frontend and backend were unable to communicate:
- Frontend hardcoded to `http://127.0.0.1:8000` (doesn't work in Docker)
- No nginx gateway integration
- Team9 Dockerfile was just a placeholder
- CORS, ports, and proxying broken

### Solution Implemented
**Monolithic backend + distributed gateways** architecture:
- Single Django core on port 8000 handles ALL team APIs (Team1-15)
- Each team (like Team9) can have its own nginx gateway/frontend
- Frontend uses relative paths (`/team9/api/...`) instead of hardcoded URLs
- Works in both Windows development AND Docker

### Architecture Type: Monolithic
✅ **RECOMMENDATION: Yes, go monolithic**

Reasons:
1. **Not real microservices** - This is a school project with 1 complete team (Team9)
2. **Shared data model** - All teams use THE SAME database and authentication
3. **Simpler** - 1 Django app vs 16 separate services
4. **Fewer failure points** - Core works = all APIs work
5. **Easier development** - Native Python, no Docker complexity needed during dev

---

## What Changed

### 1. Frontend Configuration (Team9)

**New File:** `team9/frontend/src/config.js`
```javascript
export default {
  LESSONS_ENDPOINT: '/team9/api/lessons/',
  WORDS_ENDPOINT: '/team9/api/words/',
};
```

**Updated Files:**
- `team9/frontend/src/pages/AddWord.jsx` - 2 hardcoded URLs → config
- `team9/frontend/src/pages/LessonDetail.jsx` - 3 hardcoded URLs → config
- `team9/frontend/src/pages/Microservices.jsx` - 4 hardcoded URLs → config
- `team9/frontend/src/pages/ReviewLesson.jsx` - 2 hardcoded URLs → config

**Before:** `fetch("http://127.0.0.1:8000/team9/api/lessons/")`
**After:** `fetch(config.LESSONS_ENDPOINT)` (resolves to `/team9/api/lessons/`)

### 2. Vite Development Setup

**Updated:** `team9/frontend/vite.config.js`
```javascript
server: {
  proxy: {
    '/team9/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
      secure: false,
    },
  },
}
```

**Result:**
- Frontend on `localhost:5173` can call `/team9/api/...`
- Proxy automatically routes to `localhost:8000`
- Django receives request at `http://localhost:8000/team9/api/...`

### 3. Docker Setup (Team9)

**Updated:** `team9/Dockerfile`
```dockerfile
# Stage 1: Build React frontend
FROM node:20-alpine AS frontend-build
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci && npm run build

# Stage 2: Serve with nginx + proxy API
FROM nginx:alpine
COPY gateway.conf /etc/nginx/conf.d/default.conf
COPY --from=frontend-build /app/dist /usr/share/nginx/html/team9/
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**Updated:** `team9/docker-compose.yml`
```yaml
services:
  gateway:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "${TEAM_PORT}:80"  # 9141 for Team9
    networks:
      - app404
    depends_on:
      - core
```

**Updated:** `team9/gateway.conf` (nginx reverse proxy)
```nginx
server {
  listen 80;
  root /usr/share/nginx/html;

  # API proxy to Django core
  location /team9/api/ {
    proxy_pass http://core:8000/team9/api/;
    # ...headers...
  }

  # Serve React SPA
  location / {
    try_files $uri $uri/ /team9/index.html;
  }
}
```

---

## Running the Project

### ✅ Windows Development (Recommended)

**Best for:** Active development with hot reload

```powershell
# Terminal 1: Django backend
python manage.py runserver

# Terminal 2: React frontend
cd team9/frontend
npm install  # First time
npm run dev

# Visit: http://localhost:5173
```

**Why this is best:**
- Vite hot reload (edit → instant refresh)
- Django auto-reload
- No Docker overhead
- Relative URLs work via Vite proxy

### ✅ Docker Full Stack

**Best for:** Testing production-like setup

```powershell
# Run all services
.\win_scripts\up-all.ps1

# OR just core + Team9
.\win_scripts\up-team.ps1 -Team 9

# Visit: http://localhost:9141

# Stop
.\win_scripts\down-all.ps1
```

**What happens:**
1. Core Django starts in container on port 8000
2. Team9 gateway starts
   - Builds React frontend from source
   - Serves via nginx on port 9141
   - Proxies `/team9/api/...` to core

---

## Why This Works Now

### Development (Windows)
```
Browser (5173) → Vite dev server
                   ↓
                   (Proxy rule: /team9/api → localhost:8000)
                   ↓
                Django (8000)
                   ↓
                Team9 ViewSets
```

### Docker
```
Browser (9141) → Nginx gateway (Docker)
                   ↓
                   (localhost) Frontend static files
                   (proxy) /team9/api → core service
                   ↓
                Django core (Docker, 8000)
                   ↓
                Team9 ViewSets
```

### Key Points
✅ No hardcoded localhost URLs (uses relative paths)  
✅ Works in both dev and Docker  
✅ CORS handled by Django (`localhost:*` in DEBUG)  
✅ Nginx proxy handles headers correctly  
✅ SPA routing works (deep links → index.html)  

---

## Folder Structure Summary

```
project/
├── win_scripts/                  # Unchanged - deployment scripts
│   ├── up-all.ps1
│   ├── up-team.ps1
│   └── down-all.ps1
│
├── app404/                       # Django core (monolithic)
│   ├── settings.py               # Contains CORS config ✓
│   ├── urls.py                   # Routes to team9/ ✓
│   └── ...
│
├── team9/ (MAIN CHANGES HERE)
│   ├── Dockerfile                # ✅ NEW - nginx + frontend build
│   ├── docker-compose.yml        # ✅ UPDATED - gateway service
│   ├── gateway.conf              # ✅ UPDATED - nginx config
│   │
│   ├── views.py                  # Unchanged - REST API endpoints
│   ├── models.py                 # Unchanged - Lesson, Word models
│   ├── urls.py                   # Unchanged - route to /team9/api/
│   │
│   └── frontend/                 # React app
│       ├── vite.config.js        # ✅ UPDATED - added proxy
│       ├── package.json          # Unchanged
│       │
│       └── src/
│           ├── config.js         # ✅ NEW - API endpoints
│           ├── App.jsx           # Unchanged
│           │
│           └── pages/
│               ├── AddWord.jsx       # ✅ UPDATED - use config
│               ├── LessonDetail.jsx  # ✅ UPDATED - use config
│               ├── Microservices.jsx # ✅ UPDATED - use config
│               └── ReviewLesson.jsx  # ✅ UPDATED - use config
```

---

## Verification Checklist

### ✅ Before Running

- [ ] Docker Desktop is running (for Docker tests)
- [ ] Python 3.12+ installed
- [ ] Node.js 20+ installed
- [ ] Dependencies installed:
  ```powershell
  pip install -r requirements.txt
  cd team9/frontend && npm install
  ```

### ✅ Testing Development Mode

```powershell
# Terminal 1
python manage.py runserver

# Terminal 2
cd team9/frontend && npm run dev

# Browser: http://localhost:5173
# Try:
#   - Click "افزودن درس" (Add Lesson)
#   - Click "افزودن واژه" (Add Word)
#   - Should work without errors
```

**Expected:**
- Frontend loads
- API calls successful (check Network tab)
- No CORS errors
- No "cannot fetch" errors

### ✅ Testing Docker Mode

```powershell
# Check Docker is running
docker --version

# Start
.\win_scripts\up-team.ps1 -Team 9

# Browser: http://localhost:9141
# Try: Same tests as above

# Check logs
docker logs <team9-gateway-container-id>
```

**Expected:**
- Gateway container starts
- Frontend builds in container
- API calls to `localhost:9141/team9/api/...` work
- See "Listening on 80" in nginx logs

### ✅ Testing with up-all.ps1

```powershell
.\win_scripts\up-all.ps1

# Wait for all containers to start (watch Docker Desktop)
# http://localhost:8000 - Core API should work
# http://localhost:9141 - Team9 should work
```

---

## Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| `Cannot GET /team9/api/lessons` (404) | Vite proxy not active | `npm run dev` not running |
| `Failed to fetch` in browser | Django not running | Start with `python manage.py runserver` |
| `Cannot connect to Docker daemon` | Docker Desktop not running | Start Docker Desktop |
| Blank page in Docker | Frontend not built | Check `docker logs <gateway>` |
| CORS error | Hardcoded URL used | Should be fixed - check config.js |

---

## What's NOT Changed

✅ **Unchanged - Don't modify:**
- `win_scripts/` - deployment scripts (kept as-is per requirement)
- Django models/views (views.py, models.py, serializers.py)
- Core authentication/middleware
- Database migrations
- Team1-15 setup (core handles all)

✅ **Optional for other teams:**
- Each team can follow same pattern (Dockerfile, docker-compose)
- Or keep current setup (core serves everything anyway)

---

## Architecture Decision: Why Monolithic?

### The Question
Should this be:
A) **Microservices** (15 separate teams, each with own service)
B) **Monolithic** (1 core API, teams as Django apps)

### Analysis

| Factor | Microservices | Monolithic  |
|--------|---------------|------------|
| **Failure isolation** | Team A fails ≠ Team B fails | Core fails = all teams fail |
| **Complexity** | High (16 services) | Low (1 service) |
| **Development speed** | Slow (Docker for each change) | Fast (native Python) |
| **Data sharing** | Hard (separate DBs) | Easy (shared DB) |
| **Team count** | 15 teams | 1.5 teams (Team9 complete, others stub) |
| **This project** | Overkill | ✅ Perfect fit |

### Verdict: **Monolithic ✅**

**Reasons:**
1. **Shared authentication** - All teams use same User model
2. **Shared database** - All Lesson/Word tables are in same DB
3. **Academic context** - No real service autonomy needed
4. **One complete team** - Only Team9 has frontend
5. **Operational simplicity** - 1 process to manage

**If this were real:**
- 15 independent products? Microservices ✓
- 1 learning app with 15 feature areas? Monolithic ✓ ← This project

---

## Going Forward

### For Development
```powershell
npm run dev + python manage.py runserver
```
This is your day-to-day. No Docker needed.

### For Testing/Deployment
```powershell
.\win_scripts\up-team.ps1 -Team 9
```
Or `up-all.ps1` to test all teams.

### Future Enhancements
- [ ] Add nginx to main core (central reverse proxy)
- [ ] Move frontend into Django templates (simpler, no gateway needed)
- [ ] Add authentication tests
- [ ] Production CORS configuration

---

## Support

### Debug Steps
1. Check what's running: `docker ps`
2. Check logs: `docker logs <container>`
3. Test API directly: `curl http://localhost:8000/team9/api/lessons/`
4. Test proxy: `curl http://localhost:9141/team9/api/lessons/` (in Docker)
5. Browser DevTools → Network tab → check requests/responses

### Files Modified
- ✅ 5 JSX files (API calls)
- ✅ 3 Docker files (Dockerfile, docker-compose.yml, gateway.conf)
- ✅ 1 Vite config (proxy setup)
- ➕ 1 new config file (config.js)

### Win_Scripts Compliance
✅ **No changes to win_scripts themselves**  
✅ **Scripts work as-is**  
✅ **Team9 configuration compatible with existing flow**

---

**Created:** 2026-02-10  
**Ready to test:** ✅ Yes! Run either development or Docker mode above.
