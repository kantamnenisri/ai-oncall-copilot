from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv(override=True)

app = FastAPI(title="AI On-Call Copilot API")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')
else:
    model = None

# Mock Data
class Incident(BaseModel):
    id: str
    title: str
    severity: str
    status: str
    description: str
    logs: List[str]
    metrics: dict

class IncidentCreate(BaseModel):
    title: str
    severity: str
    description: str
    logs: List[str]
    metrics: dict

mock_incidents = [
    {
        "id": "INC-001",
        "title": "High Error Rate in Checkout Service",
        "severity": "Critical",
        "status": "Active",
        "description": "Checkout service is returning 500 errors for 20% of requests.",
        "logs": [
            "2026-03-11 09:30:01 ERROR checkout_service: Connection timeout to payment_gateway",
            "2026-03-11 09:30:05 ERROR checkout_service: Failed to process order #12345",
            "2026-03-11 09:31:10 WARNING checkout_service: Retrying connection to payment_gateway..."
        ],
        "metrics": {
            "error_rate": "22%",
            "latency_p95": "450ms",
            "cpu_usage": "78%"
        }
    },
    {
        "id": "INC-002",
        "title": "Database Connection Pool Exhaustion",
        "severity": "High",
        "status": "Active",
        "description": "Users reporting slow loading times. DB connection pool is at 98% capacity.",
        "logs": [
            "2026-03-11 08:45:12 WARN db_proxy: Connection pool near limit (95/100)",
            "2026-03-11 08:46:00 ERROR web_api: SQLAlchemy QueuePool limit of size 10 overflow 10 reached"
        ],
        "metrics": {
            "db_connections": "98/100",
            "active_queries": "45",
            "memory_usage": "82%"
        }
    }
]

class ChatRequest(BaseModel):
    incident_id: str
    message: str
    history: Optional[List[dict]] = []

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "ai-oncall-copilot"}

@app.get("/incidents", response_model=List[Incident])
async def get_incidents():
    return mock_incidents

@app.post("/incidents", response_model=Incident)
async def create_incident(incident_data: IncidentCreate):
    new_id = f"INC-{len(mock_incidents) + 1:03d}"
    new_incident = {
        "id": new_id,
        "status": "Active",
        **incident_data.model_dump()
    }
    mock_incidents.append(new_incident)
    return new_incident

@app.get("/incidents/{incident_id}", response_model=Incident)
async def get_incident(incident_id: str):
    incident = next((i for i in mock_incidents if i["id"] == incident_id), None)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident

@app.post("/chat")
async def chat_with_copilot(request: ChatRequest):
    incident = next((i for i in mock_incidents if i["id"] == request.incident_id), None)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    context = f"""
    You are an expert On-Call Reliability Engineer Copilot. 
    You are helping troubleshoot the following incident:
    Title: {incident['title']}
    Severity: {incident['severity']}
    Description: {incident['description']}
    Logs: {chr(10).join(incident['logs'])}
    Metrics: {incident['metrics']}
    User Question: {request.message}
    """
    
    try:
        if not model:
            raise Exception("Model not initialized")
        response = model.generate_content(context)
        return {"response": response.text}
    except Exception as e:
        service_name = incident['title'].split()[-1]
        briefing = f"### 🛡️ Incident Briefing: {incident['id']}\n"
        briefing += f"The `{incident['title']}` is currently impact status `{incident['status']}`. "
        briefing += f"Symptoms indicate {incident['description']}. Primary metrics show {incident['metrics']}.\n\n"
        top_checks = "### 🔍 Top Priority Checks\n1. **Deployment Audit**: Investigate changes in the last deployment to `{service_name}`.\n2. **Resource Saturation**: Check for memory leaks or CPU throttling.\n3. **Downstream Dependencies**: Verify health of connected databases.\n\n"
        slack_message = "### 💬 Slack Update (Copy-paste)\n```\n🚨 *INCIDENT UPDATE: {incident['id']}*\n*Service:* {service_name}\n*Severity:* {incident['severity']}\n*Status:* Investigating\n```\n\n"
        postmortem = f"### 📝 Post-mortem Draft\n**Incident:** {incident['title']}\n**Impact:** Customers experienced increased latency and errors.\n"
        full_simulation = f"**[OFFLINE SIMULATION - API Error: {str(e)[:30]}]**\n\n" + briefing + top_checks + slack_message + postmortem
        return {"response": full_simulation}

# Serve static files for the frontend
if os.path.exists("static"):
    app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # If the file exists in static, serve it
        file_path = os.path.join("static", full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        # Otherwise serve index.html for React routing
        return FileResponse("static/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
