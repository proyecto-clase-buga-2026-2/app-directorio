from fastapi import FastAPI

from routers import cliente, home, profesional

app = FastAPI(title="DirectorioApp API")

app.include_router(home.router)
app.include_router(cliente.router)
app.include_router(profesional.router)