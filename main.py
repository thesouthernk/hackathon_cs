from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
import os
import base64

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todos los orígenes, o especifica un dominio en la lista
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos HTTP (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todos los headers
)


UPLOAD_FOLDER = 'screenshots'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Pydantic models
class ErrorReport(BaseModel):
    user_email: str
    console_logs: str
    screenshot: str

@app.post("/api/log_error")
async def log_error(report: ErrorReport):
    # Guardar captura de pantalla en el servidor
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    screenshot_path = os.path.join(UPLOAD_FOLDER, f'screenshot_{timestamp}.png')

    with open(screenshot_path, "wb") as f:
        f.write(base64.b64decode(report.screenshot.split(",")[1]))  # Decodificamos la imagen base64

    # Guardar logs de consola
    with open('error_log.txt', 'a') as f:
        f.write(f"Email: {report.user_email}\n")
        f.write(f"Console Logs: {report.console_logs}\n")
        f.write(f"Screenshot saved at: {screenshot_path}\n")
        f.write(f"Timestamp: {timestamp}\n\n")

    return JSONResponse(content={"message": "Error report received successfully"}, status_code=200)


app.mount("/static", StaticFiles(directory="static"), name="static")