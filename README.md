# AI On-Call Copilot

An interactive AI-powered "Copilot" for on-call engineers. This tool provides a professional dashboard to troubleshoot incidents, analyze logs/metrics, and identify potential root causes by leveraging Google Gemini AI (with a rich local simulation fallback).

## 🚀 Live Demo
**Deployed on Render:** [https://ai-oncall-copilot.onrender.com](https://ai-oncall-copilot.onrender.com)

## ✨ Features
- **Interactive Troubleshooting**: Chat with an AI context-aware of your incident details.
- **Rich Simulation Fallback**: Provides structured briefings, top checks, Slack updates, and post-mortem drafts even when offline or over API quota.
- **Modern Ops UI**: Dark-mode dashboard built with React and Tailwind CSS.
- **Dockerized**: Ready for seamless deployment on platforms like Render.

## 🛠️ Tech Stack
- **Frontend**: React, TypeScript, Tailwind CSS, Vite.
- **Backend**: FastAPI (Python), Uvicorn.
- **AI**: Google Generative AI (Gemini 2.0 Flash).

## 🚀 Local Setup

### Backend
1. `cd backend`
2. `python -m venv venv`
3. `.\venv\Scripts\activate` (Windows)
4. `pip install -r requirements.txt`
5. Create a `.env` file with `GEMINI_API_KEY=your_key`
6. `python main.py`

### Frontend
1. `cd frontend`
2. `npm install`
3. `npm run build` (to serve via FastAPI) or `npm run dev` (for development)

## 🐳 Docker Deployment
```bash
docker build -t ai-oncall-copilot .
docker run -p 8000:8000 ai-oncall-copilot
```


## 💡 Inspiration
This project is a reference implementation exploring concepts related to 
multi-cloud reliability engineering. The author holds USPTO patent 
applications in this domain (US 19/325,718 and US 19/344,864).
