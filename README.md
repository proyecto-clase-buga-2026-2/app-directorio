# app-directorio

Aplicación para el servicio de directorio comercial en la ciudad de Buga, su objetivo es recolectar la información de personas que prestan sus servicios por ejemplo, plomería.

## Stack tecnológico

- **Frontend:** Flutter (Dart) - SDK ^3.13.3
- **Plataformas:** Android, Web
- **Licencia:** GPL-3.0

## Requisitos previos

- Flutter SDK (`flutter --version`)
- Java JDK 17+ (`java -version`)
- Android SDK (para compilar en Android)
- Editor: VS Code / Android Studio / Cursor

## Iniciar el proyecto

```bash
# Verificar que todo esté instalado
flutter doctor -v

# Instalar dependencias del proyecto
cd frontend
flutter pub get

# Ejecutar en web
flutter run -d chrome

# Ejecutar en Android (emulador o dispositivo conectado)
flutter run
```

## Estructura del proyecto

```
app-directorio/
├── LICENSE
├── README.md
├── CONTEXT.txt
└── frontend/
    ├── lib/main.dart          # Código fuente principal
    ├── android/               # Configuración Android
    ├── web/                   # Configuración Web
    ├── test/                  # Tests
    ├── pubspec.yaml           # Dependencias
    └── analysis_options.yaml  # Reglas de linting
```

## Estado del proyecto

| Componente | Estado |
|------------|--------|
| Frontend (Flutter) | Template por defecto - en desarrollo |
| Backend/API | No implementado |
| Base de datos | No implementada |
| Modelos de datos | No implementados |
| Autenticación | No implementada |

## Funcionalidad objetivo

- Directorio de servicios por categoría (plomería, electricidad, etc.)
- Búsqueda de proveedores por ubicación y especialidad
- Registro y perfil de prestadores de servicio
- Calificaciones y reseñas

