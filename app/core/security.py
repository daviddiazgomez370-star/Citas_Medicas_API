import hmac
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import jwt
from dotenv import load_dotenv
from pwdlib import PasswordHash
from pwdlib.exceptions import UnknownHashError

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY no está configurada. Defínela como variable de entorno "
        "o en el archivo .env para desarrollo."
    )
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verificar_password(
        password_plano: str,
        password_guardado: str
) -> bool:
    try:
        return password_hash.verify(
            password_plano,
            password_guardado
        )
    except UnknownHashError:
        # Algunas instalaciones previas guardaron contraseñas sin Argon2.
        # Al autenticar correctamente se rehashean en el router de login.
        return hmac.compare_digest(password_plano, password_guardado)
    except Exception:
        return False


def password_requiere_migracion(password_guardado: str) -> bool:
    """Indica si el valor almacenado no puede ser leído por pwdlib/Argon2."""
    try:
        password_hash.verify("verificacion-de-formato", password_guardado)
    except UnknownHashError:
        return True
    except Exception:
        return False

    return False
    
def crear_access_token(
    usuario_id: int,
    rol: str
) -> str:
    
    expiracion = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(usuario_id),
        "rol": rol,
        "exp": expiracion
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM 
    )

    return token
