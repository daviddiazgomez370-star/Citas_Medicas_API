"""Migraciones SQLite pequeñas e idempotentes para instalaciones existentes.

No elimina el archivo de base de datos ni las tablas legacy. Solo copia las
cuentas de ``usuario`` a ``usuarios`` y corrige la FK de ``medicos`` cuando
proviene de una versión anterior de la aplicación.
"""

from sqlalchemy.engine import Engine


class LegacySchemaError(RuntimeError):
    """La base contiene datos que no se pueden migrar sin decisión manual."""


USER_COLUMNS = (
    "id",
    "nombre",
    "documento",
    "telefono",
    "email",
    "password",
    "rol",
)


def _table_names(cursor) -> set[str]:
    cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    return {row[0] for row in cursor.fetchall()}


def _migrar_usuarios_legacy(cursor) -> None:
    tables = _table_names(cursor)
    if "usuario" not in tables or "usuarios" not in tables:
        return

    column_list = ", ".join(USER_COLUMNS)
    cursor.execute(f"SELECT {column_list} FROM usuario ORDER BY id")

    for legacy_user in cursor.fetchall():
        user_id, _, documento, _, email, _, _ = legacy_user
        cursor.execute(
            f"SELECT {column_list} FROM usuarios WHERE id = ?",
            (user_id,),
        )
        current_user = cursor.fetchone()

        if current_user is not None:
            if tuple(current_user) != tuple(legacy_user):
                raise LegacySchemaError(
                    "La migración se detuvo: el id "
                    f"{user_id} existe con datos distintos en usuario y usuarios."
                )
            continue

        cursor.execute(
            "SELECT id FROM usuarios WHERE email = ? OR documento = ?",
            (email, documento),
        )
        conflict = cursor.fetchone()
        if conflict is not None:
            raise LegacySchemaError(
                "La migración se detuvo: una cuenta legacy coincide con otro "
                f"registro de usuarios (id {conflict[0]})."
            )

        placeholders = ", ".join("?" for _ in USER_COLUMNS)
        cursor.execute(
            f"INSERT INTO usuarios ({column_list}) VALUES ({placeholders})",
            legacy_user,
        )


def _fk_de_medicos_apunta_a_usuarios(cursor) -> bool:
    cursor.execute("PRAGMA foreign_key_list(medicos)")
    foreign_keys = cursor.fetchall()
    return any(
        row[2] == "usuarios" and row[3] == "usuario_id"
        for row in foreign_keys
    )


def _reconstruir_medicos(cursor) -> None:
    if "medicos" not in _table_names(cursor):
        return

    if _fk_de_medicos_apunta_a_usuarios(cursor):
        return

    cursor.execute(
        """
        CREATE TABLE medicos__migrating (
            id INTEGER NOT NULL,
            usuario_id INTEGER NOT NULL UNIQUE,
            especialidad VARCHAR(200) NOT NULL,
            PRIMARY KEY (id),
            FOREIGN KEY(usuario_id) REFERENCES usuarios (id)
        )
        """
    )
    cursor.execute(
        """
        INSERT INTO medicos__migrating (id, usuario_id, especialidad)
        SELECT id, usuario_id, especialidad FROM medicos
        """
    )
    cursor.execute("DROP TABLE medicos")
    cursor.execute("ALTER TABLE medicos__migrating RENAME TO medicos")
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_medicos_id ON medicos (id)")


def _asegurar_indice_citas(cursor) -> None:
    if "citas" not in _table_names(cursor):
        return

    cursor.execute(
        """
        SELECT medico_id, fecha, hora
        FROM citas
        WHERE estado != 'cancelada'
        GROUP BY medico_id, fecha, hora
        HAVING COUNT(*) > 1
        """
    )
    if cursor.fetchone() is not None:
        raise LegacySchemaError(
            "La migración se detuvo: existen citas activas duplicadas para "
            "el mismo médico, fecha y hora."
        )

    cursor.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS uq_citas_medico_fecha_hora_activa
        ON citas (medico_id, fecha, hora)
        WHERE estado != 'cancelada'
        """
    )


def migrar_esquema_legacy(engine: Engine) -> None:
    """Alinea una base SQLite previa sin perder datos ni borrar el archivo."""
    if engine.dialect.name != "sqlite":
        return

    connection = engine.raw_connection()
    cursor = connection.cursor()
    try:
        # SQLite exige desactivar las FK antes de reconstruir una tabla referida.
        cursor.execute("PRAGMA foreign_keys = OFF")
        _migrar_usuarios_legacy(cursor)
        _reconstruir_medicos(cursor)
        _asegurar_indice_citas(cursor)

        cursor.execute("PRAGMA foreign_key_check")
        violations = cursor.fetchall()
        if violations:
            raise LegacySchemaError(
                "La migración se detuvo por referencias inválidas: "
                f"{violations}"
            )

        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.close()
        connection.close()
