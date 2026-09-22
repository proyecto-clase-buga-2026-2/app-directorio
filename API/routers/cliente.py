import re
import sqlite3
from datetime import date

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, field_validator

from db import get_db
from security import hash_password

router = APIRouter(prefix="/clientes", tags=["clientes"])

EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"


class ClienteCreate(BaseModel):
    nombre: str
    apellido: str
    email: str
    telefono: str | None = None
    password: str
    direccion: str | None = None
    fecha_nacimiento: date | None = None

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

    @field_validator("direccion")
    @classmethod
    def direccion_valida(cls, value):
        if value is not None:
            value = value.strip()
            if len(value) > 255:
                raise ValueError("No puede superar los 255 caracteres")
        return value

    @field_validator("fecha_nacimiento")
    @classmethod
    def fecha_no_futura(cls, value):
        if value is not None and value > date.today():
            raise ValueError("No puede ser una fecha futura")
        return value


@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_cliente(datos: ClienteCreate):
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
            VALUES (?, ?, ?, ?, ?, 'cliente', 1)
            """,
            (datos.nombre, datos.apellido, datos.email, datos.telefono, password_hash),
        )
        usuario_id = cur.lastrowid

        cur.execute(
            """
            INSERT INTO cliente (usuario_id, direccion, fecha_nacimiento)
            VALUES (?, ?, ?)
            """,
            (usuario_id, datos.direccion, datos.fecha_nacimiento),
        )
        cliente_id = cur.lastrowid

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
            detail="Error interno al crear el cliente",
        ) from None
    finally:
        conn.close()

    return {
        "mensaje": "Cliente creado correctamente",
        "usuario_id": usuario_id,
        "cliente_id": cliente_id,
    }