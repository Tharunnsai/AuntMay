from fastapi import FastAPI

from .routers.quiz import router as quiz_router

app = FastAPI(
    title="Quiz Generation Microservice",
    description="A microservice for generating and evaluating quizzes using AI",
    version="1.0.0"
)

app.include_router(quiz_router)


