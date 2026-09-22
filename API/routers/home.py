from fastapi import APIRouter

router = APIRouter(prefix="", tags=["home"])


@router.get("/")
def hola_mundo():
    return {"message": "Hola Mundo"}