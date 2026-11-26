import asyncio
import json
import sqlite3
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# --- Core Infrastructure ---

class SchemaEvolutionTracker:
    """
    Thread-safe SQLite-backed tracker for schema evolution events.
    """
    def __init__(self, db_path: str = "schema_tracker.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS evolution_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    schema_name TEXT NOT NULL,
                    version TEXT NOT NULL,
                    change_type TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    timestamp REAL NOT NULL
                )
            """)
            conn.commit()

    def log_event(self, schema_name: str, version: str, change_type: str, payload: Dict[str, Any]):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO evolution_events (schema_name, version, change_type, payload, timestamp) VALUES (?, ?, ?, ?, ?)",
                (schema_name, version, change_type, json.dumps(payload), time.time())
            )

    def get_history(self) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM evolution_events ORDER BY timestamp DESC")
            return [dict(row) for row in cursor.fetchall()]

# --- Web Application ---

app = FastAPI(title="SchemaEvolutionTracker")
tracker = SchemaEvolutionTracker()

class EvolutionEvent(BaseModel):
    schema_name: str
    version: str
    change_type: str
    payload: Dict[str, Any]

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    return """
    <!DOCTYPE html>
    <html lang="en" class="dark">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body { background-color: #09090B; color: #FAFAFA; font-family: ui-sans-serif, system-ui, sans-serif; }
            .card { background-color: #121214; border: 1px solid #27272A; }
            .mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }
        </style>
    </head>
    <body class="p-8">
        <div class="max-w-5xl mx-auto">
            <header class="mb-10">
                <h1 class="text-2xl font-bold tracking-tight">Schema Evolution Registry</h1>
                <p class="text-zinc-500 text-sm mt-1">Real-time tracking of data structure mutations.</p>
            </header>
            
            <div id="event-list" class="space-y-4">
                <!-- Data injected via JS -->
            </div>
        </div>

        <script>
            async function fetchEvents() {
                const res = await fetch('/api/events');
                const data = await res.json();
                const container = document.getElementById('event-list');
                container.innerHTML = data.map(e => `
                    <div class="card p-5 rounded-lg hover:border-zinc-700 transition-colors">
                        <div class="flex justify-between items-start mb-3">
                            <div>
                                <span class="text-xs font-bold uppercase tracking-wider text-zinc-400">${e.schema_name}</span>
                                <h3 class="text-lg font-mono font-medium">v${e.version}</h3>
                            </div>
                            <span class="px-2 py-1 text-[10px] uppercase font-bold bg-zinc-800 rounded">${e.change_type}</span>
                        </div>
                        <pre class="text-xs text-zinc-500 bg-black p-3 rounded overflow-x-auto">${JSON.stringify(JSON.parse(e.payload), null, 2)}</pre>
                        <div class="mt-4 text-[10px] text-zinc-600 font-mono">
                            ${new Date(e.timestamp * 1000).toLocaleString()}
                        </div>
                    </div>
                `).join('');
            }
            fetchEvents();
            setInterval(fetchEvents, 5000);
        </script>
    </body>
    </html>
    """

@app.get("/api/events")
async def get_events():
    return tracker.get_history()

@app.post("/api/events")
async def post_event(event: EvolutionEvent):
    try:
        tracker.log_event(
            event.schema_name, 
            event.version, 
            event.change_type, 
            event.payload
        )
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)