"""Create and configure the FastAPI app."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from . import settings
from .routers import patient
from . import database
from . import crud
from .models import types


@asynccontextmanager
async def lifespan_events(_app: FastAPI):
    """Run tasks at start and end of app lifespan."""
    await database.Database.init_db()
    yield


app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    contact={
        "name": "e-mit.github.io",
        "url": "https://e-mit.github.io/"
    },
    license_info={
        "name": "AGPL-3.0 license",
        "url": "https://www.gnu.org/licenses/agpl-3.0.html#license-text",
    },
    lifespan=lifespan_events
)


app.include_router(
    patient.router,
    prefix=f"/{settings.PATIENT_URL_PREFIX}"
)


@app.exception_handler(crud.ResourceNotFoundError)
async def not_found_handler(_request, exc: crud.ResourceNotFoundError):
    """Raise HTTP error for entity resource not found."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": exc.message},
    )


@app.exception_handler(crud.PatientIDMismatchError)
async def id_mismatch_handler(_request, exc: crud.PatientIDMismatchError):
    """Raise HTTP error for inconsistent patient id."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.message},
    )


@app.exception_handler(types.ModelInvalidError)
async def failed_validator_handler(_request, exc: types.ModelInvalidError):
    """Raise HTTP error for failing model validator."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.message},
    )
