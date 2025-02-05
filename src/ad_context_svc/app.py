from fastapi import FastAPI
from ad_context_svc.routers import system_create

app = FastAPI(debug=True)

app.include_router(system_create.router)
