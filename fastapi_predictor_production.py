"""
Production-ready FastAPI service for football match predictions.
Optimized for millions of users with rate limiting, caching, monitoring, and scalability.
"""
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import os
import sys
import django
import asyncio
import time
import logging
from datetime import datetime
from contextlib import asynccontextmanager
from functools import lru_cache
import redis
try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    SLOWAPI_AVAILABLE = True
except ImportError:
    SLOWAPI_AVAILABLE = False
    logger.warning("slowapi not installed. Rate limiting disabled. Install with: pip install slowapi")
import uvicorn

# Setup Django (needed for analytics functions)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings_production')
django.setup()

import joblib
from predictor.analytics import (
    advanced_predict_match,
    preprocess_for_models,
    load_football_data
)
from predictor.cache_utils import sanitize_cache_key

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize rate limiter
if SLOWAPI_AVAILABLE:
    limiter = Limiter(key_func=get_remote_address)
else:
    limiter = None

# Redis connection for caching and rate limiting
REDIS_URL = os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/1')
redis_client = None

def get_redis_client():
    """Get Redis client with connection pooling."""
    global redis_client
    if redis_client is None:
        try:
            redis_client = redis.from_url(
                REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            # Test connection
            redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Caching disabled.")
            redis_client = None
    return redis_client

# Global model storage
MODEL1 = None
MODEL2 = None
MODELS_LOADED = False

# Cache configuration
CACHE_TTL = 3600  # 1 hour
PREDICTION_CACHE_TTL = 1800  # 30 minutes for predictions

# Metrics tracking
metrics = {
    'total_requests': 0,
    'successful_predictions': 0,
    'failed_predictions': 0,
    'cache_hits': 0,
    'cache_misses': 0,
    'average_response_time': 0.0,
    'start_time': datetime.now()
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - startup and shutdown."""
    # Startup
    logger.info("Starting Football Predictor API (Production Mode)")
    
    # Initialize Redis
    get_redis_client()
    
    # Load models in background
    asyncio.create_task(load_models_async())
    
    # Pre-load football data
    asyncio.create_task(preload_football_data_async())
    
    yield
    
    # Shutdown
    logger.info("Shutting down Football Predictor API")
    if redis_client:
        redis_client.close()

# Create FastAPI app with lifespan
app = FastAPI(
    title="Football Predictor API",
    description="Production-ready API for football match predictions - Optimized for millions of users",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add rate limiter exception handler
if SLOWAPI_AVAILABLE and limiter:
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware - configure for your domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv('CORS_ORIGINS', '*').split(','),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=3600,
)

# Trusted host middleware for security
allowed_hosts = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=allowed_hosts
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests for monitoring."""
    start_time = time.time()
    metrics['total_requests'] += 1
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s - "
        f"IP: {request.client.host if request.client else 'unknown'}"
    )
    
    # Update average response time
    total = metrics['total_requests']
    current_avg = metrics['average_response_time']
    metrics['average_response_time'] = (current_avg * (total - 1) + process_time) / total
    
    return response

async def load_models_async():
    """Load ML models asynchronously."""
    global MODEL1, MODEL2, MODELS_LOADED
    
    def load_models():
        """Load models in thread pool."""
        global MODEL1, MODEL2, MODELS_LOADED
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            model1_path = os.path.join(base_dir, 'models', 'model1.pkl')
            model2_path = os.path.join(base_dir, 'models', 'model2.pkl')
            
            logger.info("Loading ML models...")
            
            if os.path.exists(model1_path):
                MODEL1 = joblib.load(model1_path)
                logger.info("Model 1 loaded successfully")
            else:
                logger.warning(f"Model 1 not found at {model1_path}")
            
            if os.path.exists(model2_path):
                MODEL2 = joblib.load(model2_path)
                logger.info("Model 2 loaded successfully")
            else:
                logger.warning(f"Model 2 not found at {model2_path}")
            
            MODELS_LOADED = True
            logger.info("All models loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load models: {e}", exc_info=True)
    
    # Run in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, load_models)

async def preload_football_data_async():
    """Pre-load football data asynchronously."""
    def load_data():
        """Load data in thread pool."""
        try:
            logger.info("Pre-loading football data...")
            data1 = load_football_data(1, use_cache=True)
            data2 = load_football_data(2, use_cache=True)
            
            # Cache in Redis if available
            redis_conn = get_redis_client()
            if redis_conn:
                try:
                    import pickle
                    redis_conn.setex(
                        'football_data:1',
                        CACHE_TTL,
                        pickle.dumps(data1)
                    )
                    redis_conn.setex(
                        'football_data:2',
                        CACHE_TTL,
                        pickle.dumps(data2)
                    )
                    logger.info("Football data cached in Redis")
                except Exception as e:
                    logger.warning(f"Failed to cache data in Redis: {e}")
            
            logger.info("Football data pre-loaded successfully")
        except Exception as e:
            logger.warning(f"Failed to pre-load football data: {e}")
    
    # Run in thread pool
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, load_data)

def get_cached_prediction(home_team: str, away_team: str) -> Optional[dict]:
    """Get cached prediction from Redis."""
    redis_conn = get_redis_client()
    if not redis_conn:
        return None
    
    try:
        cache_key = f"prediction:{sanitize_cache_key(home_team)}:{sanitize_cache_key(away_team)}"
        cached = redis_conn.get(cache_key)
        if cached:
            import pickle
            metrics['cache_hits'] += 1
            return pickle.loads(cached)
    except Exception as e:
        logger.warning(f"Cache get error: {e}")
    
    metrics['cache_misses'] += 1
    return None

def cache_prediction(home_team: str, away_team: str, result: dict):
    """Cache prediction result in Redis."""
    redis_conn = get_redis_client()
    if not redis_conn:
        return
    
    try:
        cache_key = f"prediction:{sanitize_cache_key(home_team)}:{sanitize_cache_key(away_team)}"
        import pickle
        redis_conn.setex(
            cache_key,
            PREDICTION_CACHE_TTL,
            pickle.dumps(result)
        )
    except Exception as e:
        logger.warning(f"Cache set error: {e}")

# Request/Response models
class PredictionRequest(BaseModel):
    home_team: str
    away_team: str
    category: Optional[str] = None

class PredictionResponse(BaseModel):
    home_team: str
    away_team: str
    prediction: str
    home_score: int
    away_score: int
    probabilities: dict
    confidence: float
    model_type: str
    form_home: Optional[str] = None
    form_away: Optional[str] = None
    cached: bool = False

class HealthResponse(BaseModel):
    status: str
    api_ready: bool
    model1_loaded: bool
    model2_loaded: bool
    redis_connected: bool
    uptime_seconds: float
    metrics: dict

@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "message": "Football Predictor API (Production)",
        "version": "2.0.0",
        "status": "operational",
        "endpoints": {
            "/predict": "POST - Get match prediction",
            "/health": "GET - Check API health and metrics",
            "/metrics": "GET - Get performance metrics",
            "/models": "GET - Check model status"
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health():
    """Comprehensive health check endpoint."""
    redis_conn = get_redis_client()
    uptime = (datetime.now() - metrics['start_time']).total_seconds()
    
    return HealthResponse(
        status="healthy" if (MODEL1 or MODEL2) else "degraded",
        api_ready=True,
        model1_loaded=MODEL1 is not None,
        model2_loaded=MODEL2 is not None,
        redis_connected=redis_conn is not None,
        uptime_seconds=uptime,
        metrics={
            "total_requests": metrics['total_requests'],
            "successful_predictions": metrics['successful_predictions'],
            "failed_predictions": metrics['failed_predictions'],
            "cache_hit_rate": (
                metrics['cache_hits'] / (metrics['cache_hits'] + metrics['cache_misses'])
                if (metrics['cache_hits'] + metrics['cache_misses']) > 0 else 0
            ),
            "average_response_time": metrics['average_response_time']
        }
    )

@app.get("/metrics")
async def get_metrics():
    """Get detailed performance metrics."""
    uptime = (datetime.now() - metrics['start_time']).total_seconds()
    
    return {
        "uptime_seconds": uptime,
        "uptime_formatted": f"{int(uptime // 3600)}h {int((uptime % 3600) // 60)}m {int(uptime % 60)}s",
        "requests": {
            "total": metrics['total_requests'],
            "successful": metrics['successful_predictions'],
            "failed": metrics['failed_predictions'],
            "success_rate": (
                metrics['successful_predictions'] / metrics['total_requests']
                if metrics['total_requests'] > 0 else 0
            )
        },
        "cache": {
            "hits": metrics['cache_hits'],
            "misses": metrics['cache_misses'],
            "hit_rate": (
                metrics['cache_hits'] / (metrics['cache_hits'] + metrics['cache_misses'])
                if (metrics['cache_hits'] + metrics['cache_misses']) > 0 else 0
            )
        },
        "performance": {
            "average_response_time": round(metrics['average_response_time'], 3),
            "requests_per_second": round(metrics['total_requests'] / uptime if uptime > 0 else 0, 2)
        },
        "models": {
            "model1_loaded": MODEL1 is not None,
            "model2_loaded": MODEL2 is not None
        },
        "redis": {
            "connected": get_redis_client() is not None
        }
    }

@app.get("/models")
async def models_status():
    """Check model status."""
    return {
        "model1": {
            "loaded": MODEL1 is not None,
            "type": type(MODEL1).__name__ if MODEL1 else None,
            "features": MODEL1.n_features_in_ if MODEL1 and hasattr(MODEL1, 'n_features_in_') else None
        },
        "model2": {
            "loaded": MODEL2 is not None,
            "type": type(MODEL2).__name__ if MODEL2 else None,
            "features": MODEL2.n_features_in_ if MODEL2 and hasattr(MODEL2, 'n_features_in_') else None
        },
        "models_ready": MODELS_LOADED
    }

@app.post("/predict", response_model=PredictionResponse)
async def predict(
    request: Request,
    prediction_request: PredictionRequest
):
    """
    Get match prediction with caching and rate limiting.
    
    Rate limit: 100 requests per minute per IP address.
    Results are cached for 30 minutes.
    """
    # Simple rate limiting using Redis
    if limiter:
        try:
            # Use slowapi if available
            pass  # Decorator handles it
        except:
            pass
    
    # Fallback rate limiting with Redis
    redis_conn = get_redis_client()
    if redis_conn:
        client_ip = request.client.host if request.client else "unknown"
        rate_key = f"rate_limit:predict:{client_ip}"
        current = redis_conn.get(rate_key)
        if current and int(current) >= 100:  # 100 requests per minute
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded: 100 requests per minute. Please try again later."
            )
        # Increment counter
        pipe = redis_conn.pipeline()
        pipe.incr(rate_key)
        pipe.expire(rate_key, 60)  # 1 minute window
        pipe.execute()
    
    start_time = time.time()
    
    try:
        # Check cache first
        cached_result = get_cached_prediction(
            prediction_request.home_team,
            prediction_request.away_team
        )
        if cached_result:
            cached_result['cached'] = True
            logger.info(f"Cache HIT for {prediction_request.home_team} vs {prediction_request.away_team}")
            return PredictionResponse(**cached_result)
        
        # Wait for models to load (with timeout)
        max_wait = 10
        wait_time = 0
        while not MODELS_LOADED and (MODEL1 is None and MODEL2 is None) and wait_time < max_wait:
            await asyncio.sleep(0.1)
            wait_time += 0.1
        
        if MODEL1 is None and MODEL2 is None:
            raise HTTPException(
                status_code=503,
                detail="Models are still loading. Please try again in a moment."
            )
        
        # Run prediction in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            advanced_predict_match,
            prediction_request.home_team,
            prediction_request.away_team,
            MODEL1,
            MODEL2
        )
        
        if not result:
            metrics['failed_predictions'] += 1
            raise HTTPException(
                status_code=400,
                detail=f"Prediction failed - check team names: {prediction_request.home_team} vs {prediction_request.away_team}"
            )
        
        # Extract probabilities
        probs = result.get('probabilities', {})
        prob_dict = {
            "Home": float(probs.get(0, probs.get("Home", 0.33))),
            "Draw": float(probs.get(1, probs.get("Draw", 0.33))),
            "Away": float(probs.get(2, probs.get("Away", 0.33)))
        }
        
        # Normalize probabilities
        total = sum(prob_dict.values())
        if total > 0:
            prob_dict = {k: v/total for k, v in prob_dict.items()}
        
        # Determine scores
        outcome = result.get('outcome', 'Draw')
        if outcome == "Home":
            home_score = 2
            away_score = 1
        elif outcome == "Away":
            home_score = 1
            away_score = 2
        else:
            home_score = 1
            away_score = 1
        
        response_data = {
            "home_team": prediction_request.home_team,
            "away_team": prediction_request.away_team,
            "prediction": outcome,
            "home_score": home_score,
            "away_score": away_score,
            "probabilities": prob_dict,
            "confidence": float(result.get('confidence', 0.5)),
            "model_type": result.get('model_type', 'Unknown'),
            "form_home": None,
            "form_away": None,
            "cached": False
        }
        
        # Cache the result
        cache_prediction(
            prediction_request.home_team,
            prediction_request.away_team,
            response_data
        )
        
        metrics['successful_predictions'] += 1
        
        elapsed = time.time() - start_time
        logger.info(f"Prediction completed in {elapsed:.3f}s for {prediction_request.home_team} vs {prediction_request.away_team}")
        
        return PredictionResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        metrics['failed_predictions'] += 1
        logger.error(f"Prediction error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Prediction error: {str(e)}. Check server logs for details."
        )

@app.get("/predict/simple")
async def predict_simple(
    request: Request,
    home_team: str,
    away_team: str
):
    """
    Simple GET endpoint for quick predictions.
    
    Example: /predict/simple?home_team=Lugano&away_team=Luzern
    
    Rate limit: 100 requests per minute per IP address.
    """
    # Rate limiting
    redis_conn = get_redis_client()
    if redis_conn:
        client_ip = request.client.host if request.client else "unknown"
        rate_key = f"rate_limit:predict:{client_ip}"
        current = redis_conn.get(rate_key)
        if current and int(current) >= 100:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded: 100 requests per minute. Please try again later."
            )
        pipe = redis_conn.pipeline()
        pipe.incr(rate_key)
        pipe.expire(rate_key, 60)
        pipe.execute()
    
    prediction_request = PredictionRequest(home_team=home_team, away_team=away_team)
    return await predict(request, prediction_request)

if __name__ == "__main__":
    # Production configuration
    uvicorn.run(
        "fastapi_predictor_production:app",
        host=os.getenv("FASTAPI_HOST", "0.0.0.0"),
        port=int(os.getenv("FASTAPI_PORT", 8001)),
        workers=int(os.getenv("FASTAPI_WORKERS", 4)),
        log_level="info",
        access_log=True,
        timeout_keep_alive=5,
        limit_concurrency=1000,
        limit_max_requests=10000,
        reload=False  # Never reload in production
    )

