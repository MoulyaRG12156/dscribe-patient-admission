# CareDesk — Patient Admission Management App

A responsive patient admission management app built for the DScribe Software Engineer Intern Round 1 task.

## Tech stack
- **Frontend:** React.js + Vite
- **Backend:** Python + Flask (not Node.js)
- **Database:** SQLite (persistent file database)

## Features
- Add, view, edit and delete patient records (delete requires confirmation)
- Search patients by name
- Filter by ward, department and doctor
- Mark admitted patients as discharged
- Responsive dashboard for desktop, tablet and mobile
- Frontend and backend validation; backend rejects invalid values with field-specific messages
- SQLite database persists records across backend restarts

## Patient validation
- Name is required and accepts letters and spaces only
- Age is a whole number from 0 to 120
- Gender, ward, department and doctor must match the backend's allowed lists
- Admission date is required and cannot be in the future
- Status must be `Admitted` or `Discharged`

## Run locally
Requirements: Python 3.10+ and Node.js 18+ (Node is used only for the React frontend build tooling; the backend is Python Flask).

### 1. Start backend
```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
python app.py
```
Backend runs at `http://localhost:5000`. SQLite file `backend/patients.db` is created automatically.

### 2. Start frontend (new terminal)
```bash
cd frontend
npm install
npm run dev
```
Open the Vite URL printed in the terminal (usually `http://localhost:5173`).

## Deployment
### Backend — Render
1. Push this project to a public GitHub repository.
2. In Render, create **New → Web Service** and connect the repository.
3. Set **Root Directory** to `backend`.
4. Build command: `pip install -r requirements.txt`
5. Start command: `gunicorn app:app`
6. Add a persistent disk mounted at `/var/data` and environment variable `DATABASE_PATH=/var/data/patients.db` (important: SQLite on an ephemeral filesystem can be lost on redeploy/restart).
7. After deployment, copy the backend URL, e.g. `https://your-api.onrender.com`.

### Frontend — Vercel
1. Import the same GitHub repository into Vercel.
2. Set **Root Directory** to `frontend`.
3. Add environment variable `VITE_API_URL=https://your-api.onrender.com/api` (replace with your actual Render URL).
4. Deploy. The Vercel URL is your live frontend link.

For production, set the backend `CORS_ORIGINS` environment variable to your exact Vercel origin (for example `https://your-app.vercel.app`).

## API endpoints
- `GET /api/health` — health check
- `GET /api/options` — allowed select values
- `GET /api/patients` — list; optional `search`, `ward`, `department`, `doctor` query parameters
- `POST /api/patients` — create (validated)
- `PUT /api/patients/<id>` — update (validated)
- `PATCH /api/patients/<id>/discharge` — mark discharged
- `DELETE /api/patients/<id>` — delete

## Screenshots
Add screenshots of the running app here before final submission.
