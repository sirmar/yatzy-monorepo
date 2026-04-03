from fastapi import FastAPI
from app.action import router

app = FastAPI()
app.include_router(router)
