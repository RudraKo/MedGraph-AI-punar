# MediGraph.AI – V2 Product Architecture & Execution Plan

*From the desk of the Principal Architect*

What we currently have is an excellent, mathematically sound clinical engine (OCR + Interactions + Optimizer). What we need is a **sticky, patient-centric healthcare product** that wins hackathons on both technical depth and UX execution. 

To bridge this gap without over-engineering, we maintain our clean layered architecture but radically expand our domain to encompass User Identity, Adherence Tracking, and Real-world Integrations (Maps/Notifications).

This document is the blueprint to execute this transition in 30 well-defined steps.

---

## 1. Domain Entities & Database Schema Evolution

We are transitioning from a stateless processing engine to a stateful patient management platform.

### Enhanced ER Structure (To be mapped via SQLAlchemy)

**1. User (Base Entity)**
- `id` (UUID, PK)
- `email`, `password_hash`, `phone`
- `role` (Enum: PATIENT, CARETAKER, ADMIN)
- `is_verified` (Boolean)

**2. PatientProfile (1:1 with User where role=PATIENT)**
- `user_id` (FK)
- `age`, `height`, `weight`
- `chronic_conditions` (JSON/Array)
- `allergies` (JSON/Array)
- `caretaker_id` (FK to User, nullable)

**3. Prescription (1:N with PatientProfile)**
- `id` (UUID, PK)
- `patient_id` (FK)
- `upload_date`
- `image_url`
- `analysis_status` (Enum: PENDING, PROCESSED)

**4. MedicationSchedule (1:N with Prescription)**
- `id` (UUID, PK)
- `prescription_id` (FK)
- `drug_name`
- `scheduled_time` (Time)
- `dosage`

**5. AdherenceLog (1:N with MedicationSchedule)**
- `id` (UUID, PK)
- `schedule_id` (FK)
- `status` (Enum: TAKEN, MISSED, SNOOZED)
- `logged_at` (Timeline)
- `escalated_to_caretaker` (Boolean)

---

## 2. Updated Folder Structure

We expand our current `/backend/app/services` and `/routers` to house the new domains while honoring SOLID principles.

```text
backend/app/
├── api/
│   ├── dependencies.py      (Extending DI: get_current_user, get_db)
│   └── v1/
│       ├── auth.py          (JWT generation, login, register)
│       ├── users.py         (Profiles, onboarding, linkages)
│       ├── adherence.py     (Logging doses, adherence metrics)
│       ├── notifications.py (Triggering push/SMS warnings)
│       └── maps.py          (Nearby pharmacy locator)
├── core/
│   ├── config.py            (JWT keys, Google Maps API keys)
│   └── security.py          (Bcrypt hashing, JWT encoding)
├── infrastructure/
│   ├── db/
│   │   └── models.py        (SQLAlchemy schema for Users/Logs)
│   └── external/
│       ├── sms_client.py    (Twilio/Vonage integration)
│       └── maps_client.py   (Google/Mapbox Places API wrappers)
└── services/
    ├── adherence/           (Missed dose logic, escalation rules)
    └── recommendations/     (Hydration/Diet logic based on drug classes)
```

---

## 3. Backend Implementation & Middleware

### 3.1 JWT & Role-Based Access Control (RBAC)
We implement stateless JWT auth using PyJWT.
1. **`create_access_token(data: dict)`**: Encodes DB `user_id` and `role`.
2. **`get_current_user` Dependency**: Decodes JWT, fetches User from the repo.
3. **`require_role(allowed_roles: list)` Dependency**: Rejects 403 if the user's role isn't explicitly permitted.

### 3.2 Core API Endpoints

**Auth & Onboarding:**
- `POST /api/v1/auth/register` (Hashes password, creates User)
- `POST /api/v1/auth/login` (Returns JWT)
- `POST /api/v1/users/onboard` (Populates PatientProfile: age, allergies, caretaker link)

**Patient Workflow:**
- `POST /api/v1/prescriptions/upload` (Triggers OCR + Graph + Optimizer pipeline)
- `GET /api/v1/schedules/today` (Fetches optimized itinerary)
- `POST /api/v1/adherence/log` (Marks a dose as TAKEN or MISSED)
- `GET /api/v1/reports/pdf` (Generates downloadable clinical summary)

**Caretaker Workflow:**
- `GET /api/v1/caretaker/patients` (Lists assigned dependents)
- `GET /api/v1/caretaker/alerts` (Fetches missed dose escalations)

**Location Context:**
- `GET /api/v1/maps/pharmacies?lat=X&lng=Y` (Filters 24h, distance sort)

---

## 4. Frontend Architecture (React + Tailwind + Vite)

### 4.1 Component Hierarchy
```text
frontend/src/
├── components/
│   ├── auth/                (Login, Multi-step Onboarding Form)
│   ├── dashboard/
│   │   ├── RiskRadialMeter.tsx   (Color-coded 0-100 severity dial)
│   │   ├── TimelineScheduler.tsx (Vertical day-view of medications)
│   │   └── AdherenceChart.tsx    (Recharts line graph of past 7 days)
│   ├── map/
│   │   └── PharmacyLocator.tsx   (Mapbox-gl integration)
│   └── visualization/
│       └── InteractionGraph.tsx  (Cytoscape.js component)
├── pages/
│   ├── layouts/
│   │   └── RoleProtectedLayout.tsx (Redirects based on JWT role)
│   ├── PatientDashboard.tsx
│   ├── CaretakerDashboard.tsx
│   └── AdminDashboard.tsx
└── store/
    └── userStore.ts          (Zustand store for JWT state and Profile info)
```

### 4.2 Key Features
- **Map Integration:** Use Mapbox GL JS for slick web maps. Hit the backend `/maps/pharmacies` (which queries Google Places API server-side to hide the API key) to plot points.
- **Alarm System:** Use the native browser Notifications API + Service Workers for local alarms, falling back to backend-triggered SMS (via Twilio) for critical escalations.
- **Recommendation Engine:** Rule-based cards mapping drug tags to lifestyle tags (e.g., if `Aspirin` detected, UI shows "Take with food" card).

---

## 5. Security & Deployment Plan

### Security Hardening Checklist
- [ ] Passwords hashed via `bcrypt` (never stored in plaintext).
- [ ] JWT signed with `HS256` using a strong `.env` secret.
- [ ] Role Guards implemented on *both* Frontend (UI hiding) and Backend (API rejection).
- [ ] Database credentials isolated via environment variables.

### Deployment Architecture (Single-box Staging)
- **Database:** SQLite upgraded to PostgreSQL for production stability.
- **Backend:** FastAPI wrapped in Docker, run via `gunicorn` + `uvicorn` workers.
- **Frontend:** Vite built to static assets, served via `nginx` reverse proxy.
- **Hosting:** Render.com, DigitalOcean App Platform, or Railway for 1-click CI/CD.

---

## 6. Execution & Commit Plan (30 Atomic Steps)

This commit timeline is designed to be built incrementally, ensuring the app is always in a working, deployable state.

### Phase 1: Identity & Authentication (Commits 1-6)
1. `build: add PyJWT and passlib for secure authentication`
2. `feat(db): establish User and PatientProfile SQLAlchemy models`
3. `feat(auth): implement bcrypt password hashing and token encoding utils`
4. `feat(api): create registration and login endpoint routing`
5. `feat(auth): implement get_current_user and require_role FastAPI dependencies`
6. `test(auth): add unit tests for jwt issuance and role-based guards`

### Phase 2: Onboarding & Frontend Setup (Commits 7-13)
7. `feat(api): implement advanced onboarding endpoint for patient profiles`
8. `feat(ui): scaffold Vite frontend with Tailwind and React Router v6`
9. `feat(ui): build multi-step patient onboarding form component`
10. `feat(store): configure Zustand for global user session state`
11. `feat(ui): implement RoleProtector middleware wrapper for React routes`
12. `feat(ui): build dedicated login and registration interface layouts`
13. `refactor(ui): wire axios interceptors to automatically attach JWT to headers`

### Phase 3: Bringing in the Core Engine (Commits 14-19)
14. `feat(db): establish Prescription and Scheduling Models targeting patient foreign keys`
15. `feat(api): connect existing OCR and graph engines to authenticated user sessions`
16. `feat(ui): integrate Cytoscape InteractionGraph into authenticated patient dashboard`
17. `feat(ui): build RiskRadialMeter to visualize peak contraindication severity`
18. `feat(ui): implement interactive TimelineScheduler widget for medication routing`
19. `perf(backend): offload heavy image OCR processing to background async tasks`

### Phase 4: Adherence & Caretaker Workflows (Commits 20-25)
20. `feat(db): construct AdherenceLog schema and associated migration`
21. `feat(api): expose endpoints for logging missed/taken medication events`
22. `feat(ui): build caretaker dashboard layout for dependent monitoring`
23. `feat(api): implement escalation logic routing missed doses to caretaker profiles`
24. `feat(alerts): configure browser Notification API for upcoming dose warnings`
25. `feat(alerts): integrate initial server-side SMS fallback logic adapter`

### Phase 5: Polish & External Integrations (Commits 26-30)
26. `feat(recommend): implement rule-based lifestyle and hydration suggestion engine`
27. `feat(maps): create backend proxy for external Places API queries`
28. `feat(ui): integrate Mapbox component to render proximity-sorted pharmacies`
29. `feat(ui): construct responsive Admin dashboard for telemetry and user auditing`
30. `chore(deploy): finalize Dockerfile and Nginx configurations for production handoff`
