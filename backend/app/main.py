"""FastAPI Application Factory"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.config import settings
from app.api.v1 import auth, journals, admin, author, editor, reviewer, articles, roles, webhooks
from app.core.rate_limit import limiter, get_rate_limit_key
from app.core.subdomain import SubdomainMiddleware
from app.scheduler.tasks import start_scheduler, shutdown_scheduler

logger = logging.getLogger(__name__)
scheduler = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage app startup and shutdown events"""
    global scheduler
    # Startup: Start the scheduler
    logger.info("Starting application with scheduler...")
    try:
        scheduler = start_scheduler()
    except Exception as e:
        logger.error(f"Failed to initialize scheduler: {str(e)}")
    
    yield
    
    # Shutdown: Stop the scheduler
    logger.info("Shutting down application...")
    shutdown_scheduler(scheduler)


# Create FastAPI application with lifespan
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Add rate limiting middleware
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# Custom rate limit exception handler
@app.exception_handler(RateLimitExceeded)
async def rate_limit_exception_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Rate limit exceeded. Please try again later.",
            "error": "rate_limit_exceeded"
        }
    )

# Add subdomain detection middleware (must be before CORS)
app.add_middleware(SubdomainMiddleware)

# Add CORS middleware with regex pattern for subdomains
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=settings.CORS_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.aacsjournals.com"]
)


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring.
    
    Returns:
        Status of the API
    """
    return {
        "status": "healthy",
        "service": "AACS Backend API",
        "version": settings.API_VERSION
    }


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint providing API information.
    
    Returns:
        API information and available endpoints
    """
    return {
        "name": settings.API_TITLE,
        "description": settings.API_DESCRIPTION,
        "version": settings.API_VERSION,
        "documentation": "/docs",
        "endpoints": {
            "health": "/health",
            "auth": "/api/v1/auth/login",
            "documentation": "/docs"
        }
    }


# Include routers
app.include_router(auth.router)
app.include_router(journals.router)
app.include_router(articles.router)
app.include_router(admin.router)
app.include_router(author.router)
app.include_router(editor.router)
app.include_router(reviewer.router)
app.include_router(roles.router)
app.include_router(webhooks.router)


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": str(type(exc).__name__)}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development"
    )
