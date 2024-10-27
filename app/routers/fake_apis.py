# app/routers/fake_apis.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

# ------------ APIs que fallan ------------

# 1. API de Login que siempre falla
class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
async def login_user(request: LoginRequest):
    if request.username == "admin" and request.password == "admin":
        raise HTTPException(status_code=403, detail="La cuenta está bloqueada por múltiples intentos fallidos.")
    else:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas.")


# 2. API de activación de chatbot que falla por falta de configuración
class ActivateChatbotRequest(BaseModel):
    chatbot_id: str
    activate: bool

@router.post("/activate_chatbot")
async def activate_chatbot(request: ActivateChatbotRequest):
    if not request.activate:
        return {"message": "El chatbot no fue activado."}
    
    raise HTTPException(status_code=400, detail="Falta configuración: no se ha asociado un número telefónico al chatbot.")


# 3. API de cambio de contraseña que falla por verificación
class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

@router.post("/change_password")
async def change_password(request: ChangePasswordRequest):
    raise HTTPException(status_code=403, detail="No se pudo verificar tu identidad. Contacta a soporte para cambiar tu contraseña.")


# 4. API de creación de cuenta que siempre falla por correo duplicado
class CreateAccountRequest(BaseModel):
    email: str
    password: str

@router.post("/create_account")
async def create_account(request: CreateAccountRequest):
    if request.email == "example@example.com":
        raise HTTPException(status_code=409, detail="El correo electrónico ya está registrado.")
    raise HTTPException(status_code=500, detail="Error inesperado al crear la cuenta.")


# 5. API de restauración de servicio con bloqueo administrativo
@router.post("/restore_service")
async def restore_service(service_id: str):
    raise HTTPException(status_code=423, detail="El servicio está suspendido debido a un retraso con el pago. Contacta a soporte para ponerte el dia y te comenten lo adeudado.")


# 6. API de configuración avanzada que falla por falta de permisos
class AdvancedSettingsRequest(BaseModel):
    setting: str
    value: str

@router.post("/advanced_settings")
async def advanced_settings(request: AdvancedSettingsRequest):
    raise HTTPException(status_code=403, detail="Esta configuración solo puede ser modificada por el equipo de soporte.")


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
