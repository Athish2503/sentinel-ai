from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.utils.logger import logger

class KavalarException(Exception):
    """
    Base exception class for all custom Kavalar errors.
    """
    def __init__(self, message: str, status_code: int = 500, details: dict = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)

class EntityNotFoundException(KavalarException):
    """
    Exception raised when a requested entity does not exist in the database.
    """
    def __init__(self, entity_name: str, entity_id: str):
        super().__init__(
            message=f"{entity_name} with identity '{entity_id}' not found.",
            status_code=404
        )

class DatabaseException(KavalarException):
    """
    Exception raised when a database operation fails.
    """
    def __init__(self, message: str, details: dict = None):
        super().__init__(
            message=message,
            status_code=500,
            details=details
        )

def register_exception_handlers(app: FastAPI):
    """
    Registers custom exception handlers on the FastAPI application instance.
    """
    @app.exception_handler(KavalarException)
    async def kavalar_exception_handler(request: Request, exc: KavalarException):
        logger.error(f"KavalarException: {exc.message} [Code: {exc.status_code}] - Details: {exc.details}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.__class__.__name__,
                    "message": exc.message,
                    "details": exc.details
                }
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.error(f"ValidationError: {exc.errors()}")
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "ValidationError",
                    "message": "Input request validation failed.",
                    "details": exc.errors()
                }
            }
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        logger.error(f"HTTPException: {exc.detail} [Code: {exc.status_code}]")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": "HTTPException",
                    "message": exc.detail,
                    "details": None
                }
            }
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled Exception: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "InternalServerError",
                    "message": "An unexpected error occurred. Please contact system administration.",
                    "details": str(exc)
                }
            }
        )
