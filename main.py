import os
from dependencies.limiter import limiter
from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from database import Base, engine
from routers.v1 import auth, user
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from fastapi.security import HTTPBearer

app = FastAPI(title="My API", version="1.0.0")
bearer_scheme = HTTPBearer()

Base.metadata.create_all(bind=engine)
app.include_router(auth.router, prefix="/api/v1")
app.include_router(user.router, prefix="/api/v1")

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
print("Run is :", ENVIRONMENT)

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request:Request, exc:StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code,
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request:Request, exc:RequestValidationError):
    errors = []

    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })

    return JSONResponse(
        status_code=422,
        content={
            "errors": True,
            "message": "Validation Error",
            "details": errors
        }
    )

@app.exception_handler(RateLimitExceeded)
async def rate_limit_exception_handler(request:Request, exc:RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "error": True,
            "message": "Rate Limit Exceeded",
            "detail": f"Too many request. Try again in {exc.retry_after} seconds",
            "retry_after": exc.retry_after
        }
    )

@app.exception_handler(500)
async def internal_server_exception_handler(request:Request, exc:StarletteHTTPException):
    error_detail = str(exc) if ENVIRONMENT == "development" else "Internal Server Error"
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Internal Server Error",
        }
    )
def setup_cors():
    if ENVIRONMENT == "production":
        return {
            "allow_origins": [
                "https://myapp.com",
                "https://www.myapp.com",
            ],
            "allow_credentials": True,
            "allow_methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": [
                "Authorization",
                "Content-Type",
                "X-Requested-With"
            ],
            "expose_headers": [
                "X-API-Key",
                "X-Total-Count",
            ],
            "max_age": 86400,
        }
    else:
        return {
            "allow_origins": [
                "http://localhost:3000",
                "http://127.0.0.1:3000",
                "http://localhost:5173",
                "http://localhost:8080",
                "http://localhost:4200",
                "http://localhost:3001",
            ],
            "allow_credentials": True,
            "allow_methods": ["*"],
            "allow_headers": ["*"],
            "expose_headers": ["*"]
        }

app.add_middleware(CORSMiddleware, **setup_cors())
app.add_middleware(GZipMiddleware)

@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY" 
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)