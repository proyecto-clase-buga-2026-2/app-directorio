import os
import sqlite3
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "DirectorioApp.db")


def crear_esquema(conn):
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS usuario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre VARCHAR(100) NOT NULL,
            apellido VARCHAR(100) NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE,
            telefono VARCHAR(20),
            password_hash VARCHAR(255) NOT NULL,
            tipo_usuario VARCHAR(20) NOT NULL CHECK (tipo_usuario IN ('cliente', 'profesional')),
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            activo BOOLEAN DEFAULT 1
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS cliente (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL UNIQUE,
            direccion VARCHAR(255),
            fecha_nacimiento DATE,
            FOREIGN KEY (usuario_id) REFERENCES usuario(id)
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS profesional (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL UNIQUE,
            descripcion TEXT,
            experiencia_anios INTEGER,
            disponible BOOLEAN DEFAULT 1,
            promedio_calificacion DECIMAL(3,2) DEFAULT 0,
            FOREIGN KEY (usuario_id) REFERENCES usuario(id)
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS categoria_servicio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre VARCHAR(100) NOT NULL,
            descripcion TEXT
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS servicio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profesional_id INTEGER NOT NULL,
            categoria_id INTEGER NOT NULL,
            nombre VARCHAR(100) NOT NULL,
            descripcion TEXT,
            precio DECIMAL(10,2) NOT NULL CHECK (precio >= 0),
            duracion_estimada_min INTEGER,
            activo BOOLEAN DEFAULT 1,
            FOREIGN KEY (profesional_id) REFERENCES profesional(id),
            FOREIGN KEY (categoria_id) REFERENCES categoria_servicio(id)
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS solicitud_servicio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            profesional_id INTEGER NOT NULL,
            servicio_id INTEGER NOT NULL,
            fecha_solicitud TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_respuesta TIMESTAMP,
            estado VARCHAR(20) NOT NULL DEFAULT 'pendiente'
                CHECK (estado IN ('pendiente', 'aceptado', 'rechazado', 'en_proceso', 'completado', 'cancelado')),
            comentario_cliente TEXT,
            motivo_rechazo TEXT,
            FOREIGN KEY (cliente_id) REFERENCES cliente(id),
            FOREIGN KEY (profesional_id) REFERENCES profesional(id),
            FOREIGN KEY (servicio_id) REFERENCES servicio(id)
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS transaccion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            solicitud_id INTEGER NOT NULL UNIQUE,
            fecha_transaccion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            monto_total DECIMAL(10,2) NOT NULL,
            estado VARCHAR(20) NOT NULL DEFAULT 'pendiente'
                CHECK (estado IN ('pendiente', 'pagado', 'anulado')),
            FOREIGN KEY (solicitud_id) REFERENCES solicitud_servicio(id)
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS pago (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaccion_id INTEGER NOT NULL,
            fecha_pago TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            monto DECIMAL(10,2) NOT NULL,
            metodo_pago VARCHAR(30) NOT NULL
                CHECK (metodo_pago IN ('tarjeta', 'efectivo', 'transferencia', 'billetera_digital')),
            estado VARCHAR(20) NOT NULL DEFAULT 'pendiente'
                CHECK (estado IN ('pendiente', 'completado', 'fallido', 'reembolsado')),
            referencia_externa VARCHAR(100),
            FOREIGN KEY (transaccion_id) REFERENCES transaccion(id)
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS calificacion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            solicitud_id INTEGER NOT NULL UNIQUE,
            cliente_id INTEGER NOT NULL,
            profesional_id INTEGER NOT NULL,
            puntuacion INTEGER NOT NULL CHECK (puntuacion BETWEEN 1 AND 5),
            comentario TEXT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (solicitud_id) REFERENCES solicitud_servicio(id),
            FOREIGN KEY (cliente_id) REFERENCES cliente(id),
            FOREIGN KEY (profesional_id) REFERENCES profesional(id)
        )
        """
    )

    conn.commit()


def insertar_datos_ejemplo(conn):
    cur = conn.cursor()

    categorias = [
        ("Plomería", "Servicios de instalación y reparación de tuberías, llaves y sanitarios."),
        ("Tutorías", "Clases particulares de distintas materias y niveles."),
        ("Diseño", "Diseño gráfico, web y de interiores."),
        ("Electricidad", "Instalaciones y reparaciones eléctricas residenciales."),
        ("Jardinería", "Cuidado de jardines, poda y paisajismo."),
    ]
    for nombre, descripcion in categorias:
        cur.execute(
            "INSERT INTO categoria_servicio (nombre, descripcion) VALUES (?, ?)",
            (nombre, descripcion),
        )

    password_hash = "hash_ejemplo_cliente"
    cur.execute(
        """
        INSERT INTO usuario (nombre, apellido, email, telefono, password_hash, tipo_usuario, activo)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        ("Ana", "García", "ana.garcia@example.com", "555-0101", password_hash, "cliente", 1),
    )
    cliente_usuario_id = cur.lastrowid
    cur.execute(
        "INSERT INTO cliente (usuario_id, direccion, fecha_nacimiento) VALUES (?, ?, ?)",
        (cliente_usuario_id, "Av. Principal 123, Ciudad", "1990-05-15"),
    )

    password_hash = "hash_ejemplo_profesional"
    cur.execute(
        """
        INSERT INTO usuario (nombre, apellido, email, telefono, password_hash, tipo_usuario, activo)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        ("Luis", "Pérez", "luis.perez@example.com", "555-0202", password_hash, "profesional", 1),
    )
    profesional_usuario_id = cur.lastrowid
    cur.execute(
        """
        INSERT INTO profesional (usuario_id, descripcion, experiencia_anios, disponible, promedio_calificacion)
        VALUES (?, ?, ?, ?, ?)
        """,
        (profesional_usuario_id, "Plomero certificado con 10 años de experiencia.", 10, 1, 0),
    )
    profesional_id = cur.lastrowid

    cur.execute(
        """
        INSERT INTO servicio (profesional_id, categoria_id, nombre, descripcion, precio, duracion_estimada_min, activo)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (profesional_id, 1, "Reparación de fugas", "Reparación de fugas de agua en baños y cocinas.", 350.00, 90, 1),
    )

    conn.commit()


def main():
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        crear_esquema(conn)

        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM categoria_servicio")
        if cur.fetchone()[0] == 0:
            insertar_datos_ejemplo(conn)
            print("Datos de ejemplo insertados correctamente.")
        else:
            print("La base de datos ya contiene datos; no se insertaron datos de ejemplo.")

        tablas = [
            r[0]
            for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            ).fetchall()
        ]
        print("Base de datos creada correctamente en:", DB_PATH)
        print("Tablas creadas:", ", ".join(tablas))
    finally:
        conn.close()


if __name__ == "__main__":
    main()