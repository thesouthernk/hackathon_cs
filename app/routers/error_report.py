# app/routers/error_report.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import asyncio
from datetime import datetime
import os, uuid, base64, json
from app.services.error_handler import save_error_report, convert_to_json, create_ticket
from app.services.mistral_service import get_image_error_description, get_the_right_solution, answer_to_user
import requests

router = APIRouter()

UPLOAD_FOLDER = 'screenshots'
LOGS_FOLDER = 'logs'
URL_BASE = os.getenv("BASE_URL")+'/fakeapp'
# Pydantic model
class ErrorReport(BaseModel):
    user_email: str
    console_logs: str
    screenshot: str
    network_logs: list

@router.post("/log_error")
async def log_error(report: ErrorReport):
    report_id = str(uuid.uuid4())
    screenshot_path, log_file_path = save_error_report(report, report_id)
    # Ejecutar asincrónicamente get_error_report sin esperar el resultado
    asyncio.create_task(get_error_report(report_id))
    return JSONResponse(content={"message": "Error report received successfully", "uuid": report_id}, status_code=200)

@router.get("/get_error_report/{report_id}")
async def get_error_report(report_id: str):
    response_json = get_image_error_description(f'screenshot_{report_id}.png')
    image_json = convert_to_json(response_json)
    with open(LOGS_FOLDER + "/log_" + report_id + '.json', 'r', encoding='utf-8') as archivo:
        error_logs = json.load(archivo)
    data = {"image_json": image_json, "error_logs": error_logs}
    print(data)
    api_requirement = get_the_right_solution(data)
    api_requirement_json = convert_to_json(api_requirement)
    print(api_requirement)
    result_string = ""
    error_string = ""
    # Procesar las APIs en el JSON
    requested_vars = []
    apis_to_call =  []
    context_data = []
    for api in api_requirement_json["apis_to_call"]:
        url = URL_BASE + api["url"]
        method = api["method"]
        
        apis_to_call.append(url)
        try:
            values = api["values"]
        # Verificar si alguna variable tiene el valor "requested"
            if len(values)>0:
                missing_vars = [key for key, value in values.items() if value == "requested"]
            else:
                missing_vars=[]
            if missing_vars:
                requested_vars.append(missing_vars)
                error_string += f"Requested variables for API {api['url']}: {', '.join(missing_vars)}\n"
                continue  # No ejecutar esta API si hay variables "requested"

            if method == "GET":
                response = requests.get(url, params=values)
            elif method == "POST":
                response = requests.post(url, json=values)
        except:
            if method == "GET":
                response = requests.get(url)
            elif method == "POST":
                response = requests.post(url)
        # Ejecutar la API si no hay variables faltantes
        # try:
        
        context_data.append(response.json())
        # Agregar la respuesta al string de resultados
        result_string += f"Response from {api['url']}: {response.text}\n"
        # except Exception as e:
        #     error_string += f"Error executing {api['url']}: {str(e)}\n"

    # Mostrar los resultados finales
    final_output = result_string + error_string
    print(final_output)
    #  generamos respuesta
    answer = answer_to_user(data,api_requirement_json,final_output)

    answer_json = convert_to_json(answer)
    #Creamos el ticket 
        # Crear un diccionario con los datos
    context = {
        "ticket_id": report_id,
        "required_vars": requested_vars,
        "apis_to_call": apis_to_call,
        "context_data": context_data,
        "Suggested_Answer":answer_json['answer'],
        "required_human":api_requirement_json['execution_needed'],
        "send":answer_json['decision'],
        "origin":"widget",
        "info_error":answer_json['info_error'],
        "api_requirement_json":api_requirement_json,
        "log_data":data

    }

    create_ticket(report_id, context)
    

    
    return JSONResponse(content=api_requirement, status_code=200)

