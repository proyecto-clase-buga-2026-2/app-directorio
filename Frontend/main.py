import flet as ft

from registro_cliente import RegistroCliente
from registro_profesional import RegistroProfesional


@ft.component
def Login():
    page = ft.context.page

    campo_email = ft.TextField(
        label="Correo electrónico",
        prefix_icon=ft.Icons.EMAIL_OUTLINED,
    )
    campo_contrasena = ft.TextField(
        label="Contraseña",
        prefix_icon=ft.Icons.LOCK_OUTLINE,
        password=True,
        can_reveal_password=True,
    )

    def iniciar_sesion(e=None):
        faltantes = [
            campo.label
            for campo in (campo_email, campo_contrasena)
            if not (campo.value or "").strip()
        ]
        if faltantes:
            page.show_dialog(
                ft.SnackBar(ft.Text(f"Complete los campos: {', '.join(faltantes)}"))
            )
            return
        page.show_dialog(
            ft.SnackBar(
                ft.Text(
                    "Inicio de sesión en desarrollo: aún no hay conexión con el backend"
                )
            )
        )

    return ft.View(
        route="/",
        can_pop=False,
        bgcolor=ft.Colors.INDIGO_50,
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Container(
                width=420,
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
                            ft.Icons.PHONE_IN_TALK,
                            size=52,
                            color=ft.Colors.INDIGO,
                        ),
                        ft.Text(
                            "DirectorioApp",
                            size=28,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.INDIGO,
                        ),
                        ft.Text(
                            "Inicia sesión para continuar",
                            size=14,
                            color=ft.Colors.GREY_600,
                        ),
                        campo_email,
                        campo_contrasena,
                        ft.Row(
                            controls=[
                                ft.Button(
                                    content="Iniciar sesión",
                                    icon=ft.Icons.LOGIN,
                                    bgcolor=ft.Colors.INDIGO,
                                    color=ft.Colors.WHITE,
                                    height=44,
                                    expand=True,
                                    on_click=iniciar_sesion,
                                )
                            ]
                        ),
                        ft.Divider(height=1, color=ft.Colors.INDIGO_100),
                        ft.Text(
                            "¿No tienes una cuenta? Créala como:",
                            size=13,
                            color=ft.Colors.GREY_600,
                        ),
                        ft.Row(
                            controls=[
                                ft.OutlinedButton(
                                    content="Crear cuenta como cliente",
                                    icon=ft.Icons.PERSON_OUTLINE,
                                    expand=True,
                                    on_click=lambda: page.navigate("/registro_cliente"),
                                )
                            ]
                        ),
                        ft.Row(
                            controls=[
                                ft.OutlinedButton(
                                    content="Crear cuenta como profesional",
                                    icon=ft.Icons.HANDYMAN_OUTLINED,
                                    expand=True,
                                    on_click=lambda: page.navigate(
                                        "/registro_profesional"
                                    ),
                                )
                            ]
                        ),
                    ],
                ),
            )
        ],
    )


@ft.component
def App():
    return ft.Router(
        [
            ft.Route(
                component=Login,
                children=[
                    ft.Route(path="registro_cliente", component=RegistroCliente),
                    ft.Route(path="registro_profesional", component=RegistroProfesional),
                ],
            )
        ],
        manage_views=True,
    )


def iniciar(page: ft.Page):
    page.title = "DirectorioApp"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.INDIGO)
    page.render_views(App)


if __name__ == "__main__":
    ft.run(iniciar)
