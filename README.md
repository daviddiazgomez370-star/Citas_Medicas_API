# Sistema de Gestión de Citas Médicas

API REST para administrar pacientes, médicos, disponibilidades y citas médicas. El objetivo del proyecto es ofrecer un flujo seguro de programación de citas: el médico publica su disponibilidad, el paciente reserva un horario disponible y ambos consultan únicamente la información autorizada para su rol.

## Tecnologías utilizadas

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- JWT
- Argon2
- python-dotenv
- Swagger / OpenAPI

## Estructura principal

```text
.
├── app/
│   ├── core/                 # Seguridad: Argon2 y JWT
│   ├── dependencies/         # Autenticación y control de roles
│   ├── models/               # Modelos SQLAlchemy
│   ├── routers/              # Endpoints de la API
│   ├── schemas/              # Validaciones y respuestas Pydantic
│   ├── database.py           # Configuración de SQLite y sesiones
│   ├── database_migrations.py # Migraciones compatibles con datos existentes
│   └── main.py               # Aplicación FastAPI
├── .env.example              # Variables de entorno de ejemplo
├── requirements.txt
└── README.md
```

## Instalación desde cero

1. Crear el entorno virtual:

   ```powershell
   python -m venv venv
   ```

2. Activarlo en Windows PowerShell:

   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

   En macOS o Linux:

   ```bash
   source venv/bin/activate
   ```

3. Instalar las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

4. Crear el archivo de entorno para desarrollo:

   ```powershell
   Copy-Item .env.example .env
   ```

   Edita `.env` y define una clave larga y aleatoria para `SECRET_KEY`. No subas este archivo al repositorio.

5. Ejecutar FastAPI desde la raíz del proyecto:

   ```bash
   uvicorn app.main:app --reload
   ```

La documentación interactiva de Swagger estará disponible en:

[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Roles y permisos

### Paciente

- Puede registrarse e iniciar sesión.
- Puede consultar su perfil mediante `GET /auth/me`.
- Puede consultar la disponibilidad publicada por los médicos.
- Puede crear citas para horarios disponibles.
- Puede consultar únicamente sus propias citas e historial.
- Puede cancelar únicamente sus propias citas.

### Médico

- Puede registrarse e iniciar sesión.
- Puede consultar su perfil mediante `GET /auth/me`.
- Puede crear, consultar, actualizar y eliminar únicamente su propia disponibilidad.
- Puede consultar únicamente su propia agenda.
- Puede confirmar o cancelar únicamente las citas asignadas a él.

## Endpoints

### Autenticación

| Método | Endpoint | Descripción |
|---|---|---|
| POST | `/auth/login` | Inicia sesión y retorna un token JWT. |
| GET | `/auth/me` | Consulta el perfil del usuario autenticado. |

### Pacientes

| Método | Endpoint | Descripción |
|---|---|---|
| POST | `/pacientes/` | Registra un paciente. |
| GET | `/pacientes/zona-paciente` | Verifica acceso exclusivo de paciente. |

### Médicos

| Método | Endpoint | Descripción |
|---|---|---|
| POST | `/medicos/` | Registra un médico y su especialidad. |
| GET | `/medicos/` | Lista los médicos registrados. |
| GET | `/medicos/zona-medico` | Verifica acceso exclusivo de médico. |

### Disponibilidad

| Método | Endpoint | Descripción |
|---|---|---|
| POST | `/disponibilidad/` | Crea disponibilidad propia del médico. |
| GET | `/disponibilidad/mia` | Consulta la disponibilidad propia del médico. |
| GET | `/disponibilidad/medico/{medico_id}` | Consulta disponibilidad de un médico autenticado. |
| PUT | `/disponibilidad/{disponibilidad_id}` | Actualiza disponibilidad propia. |
| DELETE | `/disponibilidad/{disponibilidad_id}` | Elimina disponibilidad propia si no afecta citas activas. |

### Citas

| Método | Endpoint | Descripción |
|---|---|---|
| POST | `/Cita/` | Reserva una cita para un paciente. |
| GET | `/Cita/mis-citas` | Consulta las citas propias del paciente. |
| GET | `/Cita/historial` | Consulta el historial propio, incluidas citas pendientes, confirmadas y canceladas. |
| GET | `/Cita/agenda` | Consulta la agenda propia del médico. |
| PATCH | `/Cita/{cita_id}/estado` | Actualiza el estado de una cita asignada al médico. |
| DELETE | `/Cita/{cita_id}` | Cancela una cita propia del paciente. |

## Validaciones principales

- Correo electrónico con formato válido.
- Teléfono numérico de 10 dígitos.
- Documento numérico y validado según el tipo de registro.
- Contraseña mínima de 6 caracteres.
- Especialidad obligatoria para médicos.
- Fechas y horas de cita no pueden estar en el pasado.
- La disponibilidad exige `hora_fin` posterior a `hora_inicio`.
- No se permiten disponibilidades superpuestas para un mismo médico y fecha.
- No se permiten dos citas activas para el mismo médico, fecha y hora.
- Una cita cancelada libera el horario para una nueva reserva.

## Estados de una cita

- `pendiente`: cita creada por el paciente y a la espera de gestión médica.
- `confirmada`: cita confirmada por el médico asignado.
- `cancelada`: cita cancelada; no puede reactivarse.

## Flujo principal

1. El médico crea un bloque de disponibilidad.
2. El paciente autenticado consulta la disponibilidad y reserva un horario.
3. El médico consulta su agenda y confirma la cita.
4. El paciente consulta sus citas o historial y puede cancelar únicamente las suyas.
5. Al cancelarse una cita, el horario vuelve a estar disponible para otra reserva.

## Respuestas HTTP importantes

| Código | Significado |
|---|---|
| 200 | Operación consultada o actualizada correctamente. |
| 201 | Recurso creado correctamente. |
| 204 | Recurso eliminado o cita cancelada correctamente, sin contenido de respuesta. |
| 401 | No autenticado, token inválido o expirado. |
| 403 | Sin permisos para el rol autenticado. |
| 404 | Cita, médico, perfil médico o disponibilidad no encontrada. |
| 409 | Conflicto de horario, reserva duplicada o transición no permitida. |
| 422 | Datos de entrada inválidos según las validaciones Pydantic. |

## Ejecución rápida

Con el entorno virtual activo y `.env` configurado:

```bash
uvicorn app.main:app --reload
```

Luego abre Swagger en [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) para probar los endpoints.
