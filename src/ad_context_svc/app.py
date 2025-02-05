from fastapi import FastAPI
from ad_context_svc.routers import system_create, system_update

app = FastAPI(debug=True)

# Integrate the system_create router with the prefix '/system' so that the create endpoint is accessible at '/system/create'
app.include_router(system_create.router, prefix="/system")

# Integrate the system_update router without an additional prefix to expose the '/system/update' endpoint
app.include_router(system_update.router)
