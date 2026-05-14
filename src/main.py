# src/main.py

"""
Aplicação exemplo com Instrumentação Completa
- Prometheus metrics
- Jaeger tracing
- Structured logging
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, Gauge
import time
import json
import logging
from datetime import datetime
import random

from opentelemetry import trace, metrics
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor

# Initialize FastAPI
app = FastAPI(
    title="AIOps Example Application",
    description="Application with full observability instrumentation",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ Logging Setup ============

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Structured logging
class StructuredLogger:
    @staticmethod
    def log(level: str, message: str, **kwargs):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message,
            **kwargs
        }
        print(json.dumps(log_entry))

# ============ Prometheus Metrics ============

# Counters
requests_total = Counter(
    'app_requests_total',
    'Total requests',
    ['method', 'endpoint', 'status']
)

errors_total = Counter(
    'app_errors_total',
    'Total errors',
    ['error_type', 'endpoint']
)

# Histograms
request_duration_seconds = Histogram(
    'app_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

db_query_duration_seconds = Histogram(
    'app_db_query_duration_seconds',
    'Database query duration in seconds',
    ['operation', 'table']
)

# Gauges
active_connections = Gauge(
    'app_active_connections',
    'Number of active connections'
)

queue_length = Gauge(
    'app_queue_length',
    'Length of processing queue'
)

# ============ Jaeger Tracing Setup ============

jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger-agent",
    agent_port=6831,
)

trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

tracer = trace.get_tracer(__name__)

# Instrument FastAPI
FastAPIInstrumentor.instrument_app(app)
RequestsInstrumentor().instrument()

# ============ Middleware para Observabilidade ============

@app.middleware("http")
async def observability_middleware(request: Request, call_next):
    start_time = time.time()
    
    # Log incoming request
    StructuredLogger.log(
        "INFO",
        "Incoming request",
        method=request.method,
        path=request.url.path,
        query_params=dict(request.query_params),
        client=request.client.host if request.client else "unknown"
    )
    
    try:
        # Process request
        response = await call_next(request)
        
        # Record metrics
        process_time = time.time() - start_time
        
        requests_total.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        
        request_duration_seconds.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(process_time)
        
        # Log response
        StructuredLogger.log(
            "INFO",
            "Outgoing response",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration_seconds=process_time
        )
        
        return response
        
    except Exception as e:
        errors_total.labels(
            error_type=type(e).__name__,
            endpoint=request.url.path
        ).inc()
        
        StructuredLogger.log(
            "ERROR",
            "Request failed",
            method=request.method,
            path=request.url.path,
            error=str(e),
            duration_seconds=time.time() - start_time
        )
        
        raise

# ============ Health Checks ============

@app.get("/health/live")
async def liveness():
    """Kubernetes liveness probe"""
    return {"status": "alive"}

@app.get("/health/ready")
async def readiness():
    """Kubernetes readiness probe"""
    # Check dependencies
    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat()
    }

# ============ Metrics Endpoint ============

from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()

# ============ API Endpoints com Tracing ============

@app.get("/api/users/{user_id}")
async def get_user(user_id: int):
    """Get user by ID with full tracing"""
    
    with tracer.start_as_current_span("get_user") as span:
        span.set_attribute("user_id", user_id)
        
        try:
            # Simulate database query
            with tracer.start_as_current_span("db_query"):
                query_start = time.time()
                
                # Simulate DB operation
                time.sleep(random.uniform(0.01, 0.1))
                user = {
                    "id": user_id,
                    "name": f"User {user_id}",
                    "email": f"user{user_id}@example.com",
                    "created_at": datetime.utcnow().isoformat()
                }
                
                db_query_duration_seconds.labels(
                    operation="SELECT",
                    table="users"
                ).observe(time.time() - query_start)
            
            StructuredLogger.log(
                "INFO",
                "User retrieved",
                user_id=user_id,
                user_name=user["name"]
            )
            
            return user
            
        except Exception as e:
            span.record_exception(e)
            span.set_attribute("error", True)
            raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/users")
async def create_user(data: dict):
    """Create new user with tracing"""
    
    with tracer.start_as_current_span("create_user") as span:
        span.set_attribute("user_email", data.get("email"))
        
        try:
            # Simulate database insert
            with tracer.start_as_current_span("db_insert"):
                query_start = time.time()
                
                time.sleep(random.uniform(0.01, 0.2))
                user = {
                    "id": random.randint(1000, 9999),
                    **data,
                    "created_at": datetime.utcnow().isoformat()
                }
                
                db_query_duration_seconds.labels(
                    operation="INSERT",
                    table="users"
                ).observe(time.time() - query_start)
            
            StructuredLogger.log(
                "INFO",
                "User created",
                user_id=user["id"],
                email=data.get("email")
            )
            
            return user
            
        except Exception as e:
            span.record_exception(e)
            raise HTTPException(status_code=500, detail=str(e))

# ============ Startup & Shutdown ============

@app.on_event("startup")
async def startup():
    StructuredLogger.log("INFO", "Application starting up")

@app.on_event("shutdown")
async def shutdown():
    StructuredLogger.log("INFO", "Application shutting down")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_config=None
    )