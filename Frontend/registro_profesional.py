import flet as ft
import httpx

API_BASE = "http://127.0.0.1:8000"


def campos_vacios(campos):
    return [campo.label for campo in campos if not (campo.value or "").strip()]


@ft.component
def RegistroProfesional():
    page = ft.context.page

    campo_nombre = ft.TextField(
        label="Nombre",
        prefix_icon=ft.Icons.PERSON_OUTLINE,
    )
    campo_apellido = ft.TextField(
        label="Apellido",
        prefix_icon=ft.Icons.PERSON_OUTLINE,
    )
    campo_email = ft.TextField(
        label="Correo electrónico",
        prefix_icon=ft.Icons.EMAIL_OUTLINED,
    )
    campo_telefono = ft.TextField(
        label="Teléfono",
        prefix_icon=ft.Icons.PHONE_OUTLINED,
    )
    campo_contrasena = ft.TextField(
        label="Contraseña",
        prefix_icon=ft.Icons.LOCK_OUTLINE,
        password=True,
        can_reveal_password=True,
    )
    campo_confirmar = ft.TextField(
        label="Confirmar contraseña",
        prefix_icon=ft.Icons.LOCK_OUTLINE,
        password=True,
        can_reveal_password=True,
    )
    campo_experiencia = ft.TextField(
        label="Años de experiencia",
        prefix_icon=ft.Icons.SCHEDULE,
        helper="Cantidad de años ejerciendo tu oficio",
    )
    campo_descripcion = ft.TextField(
        label="Descripción profesional",
        prefix_icon=ft.Icons.WORK_OUTLINE,
        multiline=True,
        min_lines=3,
        max_lines=5,
        helper="Opcional. Cuéntale a los clientes qué sabes hacer",
    )

    def registrarse(e=None):
        faltantes = campos_vacios(
            [
                campo_nombre,
                campo_apellido,
                campo_email,
                campo_telefono,
                campo_contrasena,
                campo_confirmar,
                campo_experiencia,
            ]
        )
        if faltantes:
            page.show_dialog(
                ft.SnackBar(ft.Text(f"Campos obligatorios: {', '.join(faltantes)}"))
            )
            return
        if "@" not in campo_email.value or "." not in campo_email.value:
            page.show_dialog(
                ft.SnackBar(ft.Text("Ingrese un correo electrónico válido"))
            )
            return
        try:
            anios_experiencia = int((campo_experiencia.value or "").strip())
            if anios_experiencia < 0:
                raise ValueError
        except ValueError:
            page.show_dialog(
                ft.SnackBar(
                    ft.Text("Los años de experiencia deben ser un número entero")
                )
            )
            return
        if len(campo_contrasena.value) < 8:
            page.show_dialog(
                ft.SnackBar(ft.Text("La contraseña debe tener al menos 8 caracteres"))
            )
            return
        if campo_contrasena.value != campo_confirmar.value:
            page.show_dialog(ft.SnackBar(ft.Text("Las contraseñas no coinciden")))
            return

        # -- Construir payload para el backend --
        payload = {
            "nombre": campo_nombre.value.strip(),
            "apellido": campo_apellido.value.strip(),
            "email": campo_email.value.strip(),
            "telefono": campo_telefono.value.strip() if campo_telefono.value.strip() else None,
            "password": campo_contrasena.value,
            "descripcion": (campo_descripcion.value or "").strip() or None,
            "experiencia_anios": anios_experiencia,
        }

        try:
            resp = httpx.post(f"{API_BASE}/profesionales/", json=payload, timeout=10)
            if resp.status_code == 201:
                page.show_dialog(
                    ft.AlertDialog(
                        title=ft.Text("¡Registro exitoso!"),
                        content=ft.Text(
                            "La cuenta de profesional se creó correctamente."
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
        route="/registro_profesional",
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
            title=ft.Text("Crear cuenta como profesional"),
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
                            ft.Icons.ENGINEERING,
                            size=48,
                            color=ft.Colors.INDIGO,
                        ),
                        ft.Text(
                            "Registro de profesional",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.INDIGO,
                        ),
                        ft.Text(
                            "Crea tu cuenta para ofrecer tus servicios",
                            size=13,
                            color=ft.Colors.GREY_600,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        campo_nombre,
                        campo_apellido,
                        campo_email,
                        campo_telefono,
                        campo_experiencia,
                        campo_descripcion,
                        campo_contrasena,
                        campo_confirmar,
                        ft.Row(
                            controls=[
                                ft.Button(
                                    content="Registrarme",
                                    icon=ft.Icons.HANDYMAN,
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

