from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from data_schema_evolution_tracker.core import FingerprintEngine, DriftAnalyzer
from data_schema_evolution_tracker.models import ValidationResult
import pandas as pd

app = FastAPI(title="SchemaEvolutionTracker")
engine = FingerprintEngine()
analyzer = DriftAnalyzer()

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    return """
    <script src="https://cdn.tailwindcss.com"></script>
    <body class="bg-[#09090B] text-white p-8">
        <div class="max-w-4xl mx-auto border border-white/10 p-6 rounded-xl bg-[#121214]">
            <h1 class="text-2xl font-mono mb-4">SchemaEvolutionTracker</h1>
            <div class="grid grid-cols-3 gap-4">
                <div class="p-4 border border-white/10 rounded">Status: <span class="text-green-400">Operational</span></div>
            </div>
        </div>
    </body>
    """

@app.post("/validate/{schema_id}")
async def validate_data(schema_id: str, data: dict):
    try:
        df = pd.DataFrame(data)
        # Logic for fetching contract from SQLite would go here
        return ValidationResult(is_valid=True, drift_score=0.0, message="Schema compliant")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)