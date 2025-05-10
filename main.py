from fastapi import FastAPI
from src.api.routes import routers

app = FastAPI()
for router in routers:
    app.include_router(router)


@app.get("/", tags=["service"])
async def healthcheck():
    return {"status": "OK"}
