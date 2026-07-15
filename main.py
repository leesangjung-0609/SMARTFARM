import sqlite3

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime
from pathlib import Path 



app = FastAPI()
WEB_DIR = Path("public/smartfarm_demo_final(maybe)")
DB_PATH = Path("sensors.db")


app.mount("/static",StaticFiles(directory=WEB_DIR), name="static")

latest_sensor = {
	"distance":None,
	"created_at":None,
}

class SensorData(BaseModel):
	distance: float

def init_db():
	with sqlite3.connect(DB_PATH) as conn:
		conn.execute(
			"""
				CREATE TABLE IF NOT EXISTS sensor_logs(
					id INTEGER PRIMARY KEY AUTOINCREMENT,
					distance REAL NOT NULL,
					created_at  TEXT NOT NULL
				)
			"""
		)
		conn.commit()

def save_sensor(distance: float, created_at: str):
		with sqlite3.connect(DB_PATH) as conn:
			conn.execute(
				"INSERT INTO sensor_logs (distance, created_at) VALUES (?,?)",
				(distance, created_at),
			)
			conn.commit()


def get_sensor_history():
	with sqlite3.connect(DB_PATH) as conn:
		conn.row_factory = sqlite3.Row
		rows = conn.execute(
			"""
				SELECT id, distance, created_at
				FROM sensor_logs
				ORDER BY id DESC
				LIMIT 50
			"""
			).fetchall()
	return [dict(row) for row in rows]

@app.on_event("startup")
def startup():
	init_db()






@app.get("/")
def home():
	return FileResponse(WEB_DIR/"main.html")


@app.get("/main.html")
def main_page():
	return FileResponse(WEB_DIR/"main.html")


@app.get("/sub_html/main.html")
def sub_main_page():
	return FileResponse(WEB_DIR/"main.html")


@app.get("/sub_html/{page_name}.html")
def sub_page(page_name: str):
	file_path = WEB_DIR / "sub_html" / f"{page_name}.html"

	if not file_path.exists():
		raise HTTPException(status_code=404, detail="Sub page not found")
	return FileResponse(file_path)

@app.get("/sensor/history")
def sensor_history():
	return get_sensor_history()


@app.get("/sensor")
def get_sensor():
	return latest_sensor

@app.post("/sensor")
def post_sensor(data: SensorData):
	created_at = datetime.now().isoformat()

	latest_sensor["distance"] = data.distance
	latest_sensor["created_at"] = created_at
	save_sensor(data.distance, created_at)

	return {
		"status": "saved",
		"data": latest_sensor,
	}

