# app/services/error_handler.py
from datetime import datetime
import os, base64, json

UPLOAD_FOLDER = 'screenshots'
LOGS_FOLDER = 'logs'
TICKET_FOLDER = 'tickets'

def save_error_report(report, report_id):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    screenshot_path = os.path.join(UPLOAD_FOLDER, f'screenshot_{report_id}.png')
    log_file_path = os.path.join(LOGS_FOLDER, f'log_{report_id}.json')

    # Guardar la captura de pantalla
    with open(screenshot_path, "wb") as f:
        f.write(base64.b64decode(report.screenshot.split(",")[1]))

    # Crear un diccionario con los datos
    error_data = {
        "user_email": report.user_email,
        "console_logs": report.console_logs,
        "network_logs": report.network_logs,
        "timestamp": timestamp
    }

    # Guardar el diccionario en un archivo JSON
    with open(log_file_path, 'w') as f:
        json.dump(error_data, f, indent=4)

    return screenshot_path, log_file_path


def convert_to_json(json_string):
    try:
        # Limpiar la cadena de texto (en caso de que esté envuelta en backticks o tenga otras marcas)
        clean_json_string = json_string.replace('```json', '').replace('```', '').strip()

        # Si el JSON parece tener saltos de línea no escapados y no es necesario manipular, lo dejamos tal cual
        try:
            # Intentar decodificar directamente el JSON
            json_data = json.loads(clean_json_string)
            return json_data
        except json.JSONDecodeError:
            # Si falla, probablemente necesitemos escaparlo
            # Escapamos los saltos de línea y los posibles caracteres problemáticos
            
            
            clean_json_string2 = clean_json_string.replace("'", '')
            clean_json_string3 = clean_json_string2.strip()
            clean_json_string4 = clean_json_string3.replace("\n", " ")
            # Intentamos nuevamente cargarlo después de limpiar
            json_data = json.loads(clean_json_string4)
            return json_data

    except json.JSONDecodeError as e:
        print(f"Error al decodificar JSON: {e}")
        return None
    
def create_ticket(report_id, context):
    ticket_path = os.path.join(TICKET_FOLDER, f'ticket_{report_id}.json')

    # Guardar el diccionario en un archivo JSON
    with open(ticket_path, 'w') as f:
        json.dump(context, f, indent=4)

    return "success"
