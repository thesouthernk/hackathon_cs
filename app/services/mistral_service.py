# app/services/mistral_service.py
import os
from mistralai import Mistral
import json
client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))
URL_IMG = os.getenv("BASE_URL")+'/screenshots/'
def get_image_error_description(image: str):
    image_url = URL_IMG+f'{image}'
    model = "pixtral-12b-2409"
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": """<prompt>
    <description>
        El agente de IA debe analizar una imagen y detectar si existe un modal de error visible en la interfaz de usuario. Este modal de error puede provenir de librerías de JavaScript como SweetAlert (swal), Toast, Notyf o AlertifyJS.
    </description>
    <steps>
        <step>
            <action>Analizar la imagen proporcionada.</action>
        </step>
        <step>
            <action>Detectar si existe un modal de error o alerta en la imagen.</action>
            <source>Librerías: SweetAlert (swal), Toast, Notyf, AlertifyJS.</source>
        </step>
        <step>
            <action>Si se detecta un modal de error, transcribir el mensaje de error contenido en el modal.</action>
        </step>
        <step>
            <action>Determinar el tipo de error. Ejemplo: "warning" o "api error".</action>
        </step>
        <step>
            <action>Devolver la salida en formato JSON con las claves: "error_detected", "error_description" y "type_error".</action>
        </step>
    </steps>
    <expected_output>
        <output_format>JSON</output_format>
        <json_structure>
            <key>error_detected</key>
            <description>Indica si se detectó o no un modal de error. Valores posibles: true o false.</description>
            <key>error_description</key>
            <description>La descripción o mensaje que indica el modal de error.</description>
            <key>type_error</key>
            <description>El tipo de error detectado. Ejemplos: "warning", "api error", etc.</description>
        </json_structure>
    </expected_output>
</prompt>
"""
                },
                {
                    "type": "image_url",
                    "image_url": image_url
                }
            ]
        }
    ]
    chat_response = client.chat.complete(model=model, messages=messages)
    return chat_response.choices[0].message.content


def get_the_right_solution(situation: dict):
    model = "mistral-large-latest"
    
    # Convertimos el diccionario situation a una cadena JSON legible
    situation_json = json.dumps(situation, indent=4)
    
    messages = [
        {
            "role": "user",
            "content": """<prompt>
Eres un asistente que analiza informes de error y determina si es necesario llamar a alguna API para resolver el problema. Tu respuesta debe ser concisa y proporcionar solo las siguientes variables:

execution_needed: Un booleano (true o false) indicando si es necesario ejecutar alguna API.
apis_to_call: Una lista de objetos, donde cada objeto contiene:
url: La URL de la API que se debe llamar.
method: El método HTTP (GET, POST, etc.).
required_vars: Una lista de las variables requeridas por esa API.


# ------------ APIs utilitarias para resolver problemas ------------

# 1. API para restablecer contraseña
class ResetPasswordRequest(BaseModel):
    email: str

@router.post("/reset_password")
async def reset_password(request: ResetPasswordRequest):
    # Simulación de que se envía el correo de restablecimiento
    if request.email == "admin@example.com":
        return {"message": "Se ha enviado un enlace de restablecimiento de contraseña a tu correo electrónico."}
    else:
        raise HTTPException(status_code=404, detail="Correo electrónico no registrado.")


# 2. API para listar números telefónicos disponibles para el cliente (para activar chatbot)
@router.get("/list_phone_numbers")
async def list_phone_numbers():
    # Simulación de una lista de números telefónicos asociados al cliente
    phone_numbers = [
        {"id": "1", "number": "+1234567890"},
        {"id": "2", "number": "+0987654321"},
    ]
    return {"available_phone_numbers": phone_numbers}



# 3. API para solicitar verificación de cuenta
class RequestVerificationRequest(BaseModel):
    email: str

@router.post("/request_verification")
async def request_verification(request: RequestVerificationRequest):
    # Simulación de solicitud de verificación de cuenta
    return {"message": f"Se ha enviado un nuevo enlace de verificación a {request.email}. Revisa tu bandeja de entrada."}


# 4. API para asociar un numero de telefono a un bot
class AssociatePhoneNumberRequest(BaseModel):
    chatbot_id: str
    phone_number: str

@router.post("/associate_phone_number_to_chatbot")
async def associate_phone_number_to_chatbot(request: AssociatePhoneNumberRequest):
    # Simulación de la asociación del número de teléfono al chatbot
    # Aquí normalmente interactuarías con una base de datos para realizar la asociación
    if request.chatbot_id and request.phone_number:
        # Simulación de asociación exitosa
        return {"message": f"El número {request.phone_number} ha sido asociado correctamente al chatbot {request.chatbot_id}."}
    else:
        raise HTTPException(status_code=400, detail="El ID del chatbot o el ID del número telefónico no son válidos.")
    


# 5. API para solicitar ayuda con configuraciones avanzadas
class AdvancedSettingsHelpRequest(BaseModel):
    setting: str

@router.post("/request_advanced_settings_help")
async def request_advanced_settings_help(request: AdvancedSettingsHelpRequest):
    return {"message": f"Se ha enviado tu solicitud para modificar la configuración '{request.setting}' al equipo de soporte."}



# 6. API para obtener deuda
@router.get("/get_debt")
async def get_debt():
    # Simulación de datos de deuda
    debt_data = {
        "amount_due": 120.50,
        "due_date": "2024-11-15",
        "currency": "USD"
    }
    return debt_data


# 7. API para solicitar link de pago
class RequestPaymentLinkRequest(BaseModel):
    email: str

@router.post("/request_payment_link")
async def request_payment_link(request: RequestPaymentLinkRequest):
    # Simulación de la generación de un link de pago
    fake_payment_link = f"https://fakepayment.com/pay?user={request.email}&amount=120.50"
    return {"payment_link": fake_payment_link, "message": "Se ha generado un link de pago. Haz clic en el enlace para proceder con el pago."}


Instrucciones:

Analiza el informe de error y determina si es necesario llamar a alguna API para resolver el problema.
Si es necesario, establece execution_needed en true y en apis_to_call proporciona una lista con las APIs que se deben llamar, incluyendo sus URLs, métodos y variables requeridas.
Si no es necesario llamar a ninguna API, establece execution_needed en false y deja apis_to_call como una lista vacía.
No proporciones ningún razonamiento o explicación adicional.

Formato de Respuesta:

{
  "execution_needed": true,
  "apis_to_call": [
    {
      "url": "/list_phone_numbers",
      "method": "GET",
      "required_vars": [],
      "values":[]
    },
    {
      "url": "/associate_phone_number_to_chatbot",
      "method": "POST",
      "required_vars": ["chatbot_id", "phone_number"],
      "values":{"chatbot_id":1, "phone_number":"requested"}, (Siempre se usa requested si es un valor que se requiere que el usuario confirme, si es algo sencillo como su correo se asume, si es algo mas importante se pregunta)
    }
  ]
}


</prompt>

Informe de Error: 
""" + situation_json
        }
    ]

    chat_response = client.chat.complete(model=model, messages=messages, temperature=0)
    return chat_response.choices[0].message.content



def answer_to_user(error_data,api_requirements,final_output):
    model = "ministral-8b-latest"
    error_data_str=json.dumps(error_data)
    api_requirements_str=json.dumps(api_requirements)
    final_output_str =json.dumps(final_output)
    messages = [
        {
            "role": "user",
            "content": """Actúa como una API para el encargado de soporte al cliente.

Recibiras la siguiente información:

Un JSON con información detallada del error.
Un JSON con recomendaciones de qué APIs podrían resolver el problema, o podría indicar que no se puede resolver con una API.
Un JSON que contiene la información resultante de las APIs que se ejecutaron; si no se ejecutó ninguna, este JSON estará vacío.

Instrucciones:

Toma una decisión sobre si enviar o no el correo al usuario:

Envía el correo cuando se requiere información adicional del usuario. Por ejemplo, si una API indica que necesita un número de contacto y no lo tenemos, debes solicitar ese dato al usuario.
Envía el correo si se ejecutó una API exitosamente y deseas informar al usuario sobre la resolución de su problema de manera clara y comprensible.
No envíes el correo si no hay APIs disponibles para resolver el problema, si las APIs fallaron o si no se encontró la información necesaria. En estos casos, prepara una respuesta recomendada pero no la envíes.
Escribe la respuesta al usuario:

Sé protocolar pero amistoso, utiliza emojis para dar un toque cercano y moderno.
Evita términos técnicos; explica las acciones o solicitudes de manera sencilla y comprensible.
Adopta un tono startupero, mostrando entusiasmo y cercanía.
Utiliza Markdown para dar formato al correo, incluyendo saltos de línea y resaltando las partes importantes. Presenta la información de manera clara y estructurada, casi como una minuta.
Salida:

Devuelve únicamente un JSON con los siguientes campos:
{ "decision": true o false, "answer": "el correo escrito para el usuario en formato Markdown" }

No incluyas ningún texto adicional antes o después del JSON.
Solo devuelve el JSON en el formato exacto indicado.
Ejemplos:

Si solicitas información:

{"decision": true, "answer": "¡Hola! 😊\nEsperamos que estés teniendo un excelente día.\nPara poder ayudarte de la mejor manera posible con tu solicitud, necesitamos que nos proporciones el número al que le quieres asignar el chatbot. Esto nos permitirá brindarte una solución más rápida y efectiva.\n¡Gracias por tu comprensión y colaboración! 🚀", info_error: "el robot necesita tener configurado un numero, se reviso la api de obtener numeros para preguntar que numero necesita"}

Si informas una acción realizada:

{"decision": true, "answer": "¡Hola! 😊\nHemos solicitado la recuperación de contraseña para que puedas desbloquear tu cuenta. Te llegará un correo automático de nuestro sistema.\n**¿Hay algo más en lo que podamos ayudarte?**\n¡Gracias por confiar en nosotros! 🚀", info_error: "La cuenta se encontraba bloqueada por lo que se gatilla api de recuperacion de contraseña para que le llegue correo al usuario"}

Si es una sugerencia de respuesta:

{"decision": false, "answer": "¡Hola! 😊\nQueremos informarte que hemos escalado tu solicitud al equipo especializado para brindarte una solución lo más pronto posible.\nTe mantendremos al tanto de cualquier actualización.\nAgradecemos tu paciencia y comprensión. Si tienes alguna otra consulta, no dudes en contactarnos.\n¡Gracias por ser parte de nuestra comunidad! 🚀", info_error: "No se puede resolver con las apis generales se requiere asistencia del equipo, la api no existia error 404"}

Recuerda:

Tú manejas los detalles técnicos internamente; el usuario solo necesita la información esencial presentada de manera amigable.
No incluyas ningún texto fuera del JSON.
Tu respuesta debe ser únicamente el JSON, sin texto adicional.
Ahora, con base en la información proporcionada, toma tu decisión y redacta la respuesta adecuada, y entrégamela en el formato JSON con las dos variables solicitadas: decision y answer.
Finalmente ademas agregame una variable con la info del error descrita ojala en formato lista hacia abajo todo lo que se detecto y se recomienda hacer la puedes devolver bajo el nombre de variable info_error
iformacion:
""" + "data de error: \n" + error_data_str + "\nInfo Api utiles: \n" + api_requirements_str+ "\nInfo apis usadas o faltantes por usar: \n" +final_output_str
            }
        ]

    chat_response = client.chat.complete(model=model, messages=messages, temperature=0)
    return chat_response.choices[0].message.content