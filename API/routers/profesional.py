import re
import sqlite3

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, field_validator

from db import get_db
from security import hash_password

router = APIRouter(prefix="/profesionales", tags=["profesionales"])

EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"


class ProfesionalCreate(BaseModel):
    nombre: str
    apellido: str
    email: str
    telefono: str | None = None
    password: str
    descripcion: str | None = None
    experiencia_anios: int | None = None
    disponible: bool = True

    @field_validator("nombre", "apellido")
    @classmethod
    def nombre_y_apellido_validos(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("No puede estar vacío")
        if len(value) > 100:
            raise ValueError("No puede superar los 100 caracteres")
        return value

    @field_validator("email")
    @classmethod
    def email_valido(cls, value: str) -> str:
        value = value.strip().lower()
        if not re.fullmatch(EMAIL_REGEX, value):
            raise ValueError("Formato de email inválido")
        return value

    @field_validator("telefono")
    @classmethod
    def telefono_valido(cls, value):
        if value is not None:
            value = value.strip()
            if len(value) > 20:
                raise ValueError("No puede superar los 20 caracteres")
        return value

    @field_validator("password")
    @classmethod
    def password_valida(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Debe tener al menos 8 caracteres")
        return value

    @field_validator("descripcion")
    @classmethod
    def descripcion_valida(cls, value):
        if value is not None:
            value = value.strip()
            if len(value) > 5000:
                raise ValueError("No puede superar los 5000 caracteres")
        return value

    @field_validator("experiencia_anios")
    @classmethod
    def experiencia_no_negativa(cls, value):
        if value is not None and value < 0:
            raise ValueError("No puede ser negativa")
        return value


@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_profesional(datos: ProfesionalCreate):
    conn = get_db()
    try:
        cur = conn.cursor()

        cur.execute("SELECT id FROM usuario WHERE email = ?", (datos.email,))
        if cur.fetchone() is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un usuario con ese email",
            )

        password_hash = hash_password(datos.password)
        cur.execute(
            """
            INSERT INTO usuario (nombre, apellido, email, telefono, password_hash, tipo_usuario, activo)
            VALUES (?, ?, ?, ?, ?, 'profesional', 1)
            """,
            (datos.nombre, datos.apellido, datos.email, datos.telefono, password_hash),
        )
        usuario_id = cur.lastrowid

        cur.execute(
            """
            INSERT INTO profesional (usuario_id, descripcion, experiencia_anios, disponible, promedio_calificacion)
            VALUES (?, ?, ?, ?, 0)
            """,
            (usuario_id, datos.descripcion, datos.experiencia_anios, datos.disponible),
        )
        profesional_id = cur.lastrowid

        conn.commit()
    except HTTPException:
        conn.rollback()
        raise
    except sqlite3.IntegrityError:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El email ya está registrado",
        ) from None
    except Exception:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al crear el profesional",
        ) from None
    finally:
        conn.close()

    return {
        "mensaje": "Profesional creado correctamente",
        "usuario_id": usuario_id,
        "profesional_id": profesional_id,
    }