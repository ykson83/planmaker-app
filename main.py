from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent


@app.get("/", include_in_schema=False)
def home() -> FileResponse:
  return FileResponse(BASE_DIR / "static" / "index.html")


app.mount("/static", StaticFiles(directory=BASE_DIR / "static", html=True), name="static")


@app.get("/health")
def health():
  return {"status": "ok"}
