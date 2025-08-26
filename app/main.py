from fastapi import FastAPI

from .routers.auth import router as auth_router
from .routers.quiz import router as quiz_router
from .routers.history import router as history_router


app = FastAPI()

app.include_router(auth_router)
app.include_router(quiz_router)
app.include_router(history_router)


