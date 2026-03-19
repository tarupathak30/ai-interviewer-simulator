from fastapi import FastAPI
from api.routes import router

app = FastAPI(title="Interview Simulator")
app.include_router(router, prefix="/api")