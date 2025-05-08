from email import errors
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.routers import admin, employee,auth
from app.db.database import engine
import app.models
from app.scheduler import start_scheduler 
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

def startup_event(app: FastAPI):
    # Start your scheduler here
    start_scheduler()
    yield
app = FastAPI(title="Attendence Management System",lifespan=startup_event)# this is alternative new method of on_event 
# Routers
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(employee.router, prefix="/employee", tags=["Employee"])
app.include_router(auth.router, prefix="/auth")
app.include_router(admin.router, prefix="/admin")
app.include_router(employee.router, prefix="/employee")
app.include_router(admin.admin_router)

@app.get("/")
def root():
    return {"message": "Attendence Management API is running"}
@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
       errors = exc.errors()
       custom_errors = []

       for err in errors:
        field = ".".join([str(loc) for loc in err['loc'] if loc != 'body'])
        msg = err['msg']
        custom_errors.append(f"{field}: {msg}")

        return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": custom_errors}
    )