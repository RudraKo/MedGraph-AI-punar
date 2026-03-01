# MedGraph.AI

MedGraph.AI is a medical drug interaction detection platform built for hackathons.

## Architecture
- React Frontend -> port 5173
- Node.js Auth Server -> port 3000
- Python FastAPI Backend -> port 8000
- MongoDB Atlas (Cloud)

## Start Commands

Terminal 1 - FastAPI
```bash
cd backend && pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Terminal 2 - Node.js Auth
```bash
cd auth && npm install
npx ts-node-dev --respawn server.ts
```

Terminal 3 - React Frontend
```bash
cd frontend && npm install
npm run dev
```

Seed Atlas (run once, needs Data/ folder with CSVs)
```bash
pip install pymongo motor python-dotenv certifi fuzzywuzzy python-Levenshtein
python seed_atlas.py
```
