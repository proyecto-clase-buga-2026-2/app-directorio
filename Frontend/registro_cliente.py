import datetime

import flet as ft
import httpx

API_BASE = "http://127.0.0.1:8000"


def campos_vacios(valores):
    return [etiqueta for etiqueta, valor in valores if not (valor or "").strip()]


@ft.component
def RegistroCliente():
    page = ft.context.page

    nombre, set_nombre = ft.use_state("")
    apellido, set_apellido = ft.use_state("")
    email, set_email = ft.use_state("")
    telefono, set_telefono = ft.use_state("")
    contrasena, set_contrasena = ft.use_state("")
    confirmar, set_confirmar = ft.use_state("")
    direccion, set_direccion = ft.use_state("")
    fecha_nacimiento, set_fecha_nacimiento = ft.use_state("")

    def establecer_fecha(fecha):
        set_fecha_nacimiento(fecha.strftime("%d/%m/%Y"))

    selector_fecha = ft.DatePicker(
        last_date=datetime.datetime.now(),
        on_change=lambda e: establecer_fecha(e.control.value),
    )

    def registrarse(e=None):
        faltantes = campos_vacios(
            [
                ("Nombre", nombre),
                ("Apellido", apellido),
                ("Correo electrónico", email),
                ("Teléfono", telefono),
                ("Contraseña", contrasena),
                ("Confirmar contraseña", confirmar),
                ("Dirección", direccion),
            ]
        )
        if faltantes:
            page.show_dialog(
                ft.SnackBar(ft.Text(f"Campos obligatorios: {', '.join(faltantes)}"))
            )
            return
        if "@" not in email or "." not in email:
            page.show_dialog(
                ft.SnackBar(ft.Text("Ingrese un correo electrónico válido"))
            )
            return
        if len(contrasena) < 8:
            page.show_dialog(
                ft.SnackBar(ft.Text("La contraseña debe tener al menos 8 caracteres"))
            )
            return
        if contrasena != confirmar:
            page.show_dialog(ft.SnackBar(ft.Text("Las contraseñas no coinciden")))
            return

        # -- Construir payload para el backend --
        payload = {
            "nombre": nombre.strip(),
            "apellido": apellido.strip(),
            "email": email.strip(),
            "telefono": telefono.strip() if telefono.strip() else None,
            "password": contrasena,
            "direccion": direccion.strip(),
            "fecha_nacimiento": None,
        }
        if fecha_nacimiento:
            try:
                partes = fecha_nacimiento.split("/")
                payload["fecha_nacimiento"] = f"{partes[2]}-{partes[1]}-{partes[0]}"
            except (IndexError, ValueError):
                pass

        try:
            resp = httpx.post(f"{API_BASE}/clientes/", json=payload, timeout=10)
            if resp.status_code == 201:
                page.show_dialog(
                    ft.AlertDialog(
                        title=ft.Text("¡Registro exitoso!"),
                        content=ft.Text(
                            "La cuenta de cliente se creó correctamente."
                        ),
                        actions_alignment=ft.MainAxisAlignment.END,
                        actions=[
                            ft.TextButton(
                                "Aceptar",
                                on_click=lambda e: (
                                    page.pop_dialog(),
                                    page.navigate("/"),
                                ),
                            )
                        ],
                    )
                )
            elif resp.status_code == 409:
                detalle = resp.json().get("detail", "El email ya está registrado")
                page.show_dialog(ft.SnackBar(ft.Text(detalle)))
            elif resp.status_code == 422:
                errores = resp.json().get("detail", [])
                if isinstance(errores, list):
                    msgs = [e.get("msg", "") for e in errores]
                else:
                    msgs = [str(errores)]
                page.show_dialog(
                    ft.SnackBar(ft.Text("Datos inválidos: " + "; ".join(msgs)))
                )
            else:
                page.show_dialog(
                    ft.SnackBar(ft.Text(f"Error inesperado ({resp.status_code})"))
                )
        except httpx.ConnectError:
            page.show_dialog(
                ft.SnackBar(ft.Text("No se pudo conectar con el servidor"))
            )
        except httpx.TimeoutException:
            page.show_dialog(
                ft.SnackBar(ft.Text("El servidor tardó demasiado en responder"))
            )

    return ft.View(
        route="/registro_cliente",
        bgcolor=ft.Colors.INDIGO_50,
        scroll=ft.ScrollMode.AUTO,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        padding=ft.Padding.symmetric(horizontal=20, vertical=24),
        appbar=ft.AppBar(
            leading=ft.IconButton(
                ft.Icons.ARROW_BACK,
                tooltip="Volver",
                on_click=lambda: page.navigate("/"),
            ),
            title=ft.Text("Crear cuenta como cliente"),
            center_title=True,
            bgcolor=ft.Colors.INDIGO,
            color=ft.Colors.WHITE,
        ),
        controls=[
            ft.Container(
                width=440,
                bgcolor=ft.Colors.WHITE,
                border=ft.Border.all(1, ft.Colors.INDIGO_100),
                border_radius=ft.BorderRadius.all(14),
                padding=ft.Padding.all(32),
                content=ft.Column(
                    tight=True,
                    spacing=14,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(
                            ft.Icons.PERSON_ADD_ALT_1,
                            size=48,
                            color=ft.Colors.INDIGO,
                        ),
                        ft.Text(
                            "Registro de cliente",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.INDIGO,
                        ),
                        ft.Text(
                            "Crea tu cuenta para solicitar servicios",
                            size=13,
                            color=ft.Colors.GREY_600,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.TextField(
                            label="Nombre",
                            prefix_icon=ft.Icons.PERSON_OUTLINE,
                            value=nombre,
                            on_change=lambda e: set_nombre(e.control.value),
                        ),
                        ft.TextField(
                            label="Apellido",
                            prefix_icon=ft.Icons.PERSON_OUTLINE,
                            value=apellido,
                            on_change=lambda e: set_apellido(e.control.value),
                        ),
                        ft.TextField(
                            label="Correo electrónico",
                            prefix_icon=ft.Icons.EMAIL_OUTLINED,
                            value=email,
                            on_change=lambda e: set_email(e.control.value),
                        ),
                        ft.TextField(
                            label="Teléfono",
                            prefix_icon=ft.Icons.PHONE_OUTLINED,
                            value=telefono,
                            on_change=lambda e: set_telefono(e.control.value),
                        ),
                        ft.TextField(
                            label="Contraseña",
                            prefix_icon=ft.Icons.LOCK_OUTLINE,
                            password=True,
                            can_reveal_password=True,
                            value=contrasena,
                            on_change=lambda e: set_contrasena(e.control.value),
                        ),
                        ft.TextField(
                            label="Confirmar contraseña",
                            prefix_icon=ft.Icons.LOCK_OUTLINE,
                            password=True,
                            can_reveal_password=True,
                            value=confirmar,
                            on_change=lambda e: set_confirmar(e.control.value),
                        ),
                        ft.TextField(
                            label="Dirección",
                            prefix_icon=ft.Icons.LOCATION_ON_OUTLINED,
                            value=direccion,
                            on_change=lambda e: set_direccion(e.control.value),
                        ),
                        ft.TextField(
                            label="Fecha de nacimiento",
                            prefix_icon=ft.Icons.CAKE_OUTLINED,
                            helper="Opcional",
                            read_only=True,
                            value=fecha_nacimiento,
                            suffix=ft.IconButton(
                                ft.Icons.CALENDAR_MONTH,
                                tooltip="Seleccionar fecha",
                                on_click=lambda: page.show_dialog(selector_fecha),
                            ),
                        ),
                        ft.Row(
                            controls=[
                                ft.Button(
                                    content="Registrarme",
                                    icon=ft.Icons.PERSON_ADD_ALT_1,
                                    bgcolor=ft.Colors.INDIGO,
                                    color=ft.Colors.WHITE,
                                    height=44,
                                    expand=True,
                                    on_click=registrarse,
                                )
                            ]
                        ),
                        ft.TextButton(
                            "Volver al inicio de sesión",
                            on_click=lambda: page.navigate("/"),
                        ),
                    ],
                ),
            )
        ],
    )
