from fastapi import FastAPI
from ad_context_svc.routers import system_create

app = FastAPI(debug=True)

# Integrate the system_create router with the prefix '/system' so that the create endpoint is accessible at '/system/create'
app.include_router(system_create.router, prefix="/system")
