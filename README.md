## Project Aiden

FastAPI backend + Vite frontend AI society simulation.

### Current Structure

- `backend/` -> Python FastAPI service (`/ws/society`, `/api/society/task`)
- `frontend/` -> Vite/React UI (status pill, health bars, event feed)

### Run Locally

Backend (port 8000):

```bash
cd backend
pip install -r requirements.txt
cd ..
PYTHONPATH=backend python -m uvicorn backend.main:app --port 8000
```

Frontend (port 5173):

```bash
cd frontend
npm install
npm run dev
```

### Windows PowerShell Commands

Backend:

```powershell
Set-Location "c:\Users\khanf\OneDrive\Documents\Project Aiden"
$env:PYTHONPATH = "backend"
c:/python314/python.exe -m uvicorn backend.main:app --port 8000
```

Frontend:

```powershell
Set-Location "c:\Users\khanf\OneDrive\Documents\Project Aiden\frontend"
npm run dev
```

### Notes

- The old `src/frontend` path is deprecated. Use `frontend`.
- If port 8000 is busy, stop the existing listener before starting backend.

### Root Convenience Scripts

From project root:

```bash
npm run dev:all
npm run dev:frontend
npm run dev:backend
```

`npm run dev:all` starts backend and frontend together in separate PowerShell terminals.
It also sets `SOCIETY_TICK_ACTIVE=5` and `SOCIETY_TICK_IDLE=30` so live events appear quickly.

If backend port 8000 is already occupied:

```bash
npm run dev:backend:clean
```
