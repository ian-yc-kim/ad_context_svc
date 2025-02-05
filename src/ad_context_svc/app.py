from fastapi import FastAPI
from ad_context_svc.routers import system_create, system_update, system_delete, system_get

app = FastAPI(debug=True)

# Integrate the system_create router with the prefix '/system' so that the create endpoint is accessible at '/system/create'
app.include_router(system_create.router, prefix="/system")

# Integrate the system_update router without an additional prefix to expose the '/system/update' endpoint
app.include_router(system_update.router)

# Integrate the system_delete router with the prefix '/system' so that the delete endpoint is accessible at '/system/delete'
app.include_router(system_delete.router, prefix="/system")

# Integrate the system_get router with the prefix '/system' so that the GET endpoint is accessible at '/system/get'
app.include_router(system_get.router, prefix="/system")
