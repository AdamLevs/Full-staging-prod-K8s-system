"""
Simple FastAPI application with PostgreSQL and Redis integration.
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime
import redis
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://appuser:apppass@postgres-service:5432/appdb")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis setup
REDIS_HOST = os.getenv("REDIS_HOST", "redis-service")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")

try:
    if REDIS_PASSWORD:
        redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, decode_responses=True)
    else:
        redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    redis_client.ping()
    logger.info("Connected to Redis")
except Exception as e:
    logger.warning(f"Redis connection failed: {e}")
    redis_client = None

# Database Models
class Item(Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# Pydantic Models
class ItemCreate(BaseModel):
    name: str

class ItemResponse(BaseModel):
    id: int
    name: str
    created_at: datetime
    
    model_config = {"from_attributes": True}

# Create tables
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI(title="Demo API", version="1.0.0")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_redis():
    return redis_client

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db_status = "ok"
    redis_status = "ok"
    
    # Check database
    try:
        db = SessionLocal()
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        db.close()
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "error"
    
    # Check Redis
    if redis_client:
        try:
            redis_client.ping()
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            redis_status = "error"
    else:
        redis_status = "unavailable"
    
    return {
        "status": "healthy" if db_status == "ok" else "unhealthy",
        "database": db_status,
        "redis": redis_status
    }

@app.post("/items", response_model=ItemResponse)
async def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    """Create a new item"""
    db_item = Item(name=item.name)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    # Invalidate cache
    if redis_client:
        try:
            redis_client.delete("items:list")
        except:
            pass
    
    return db_item

@app.get("/items")
async def get_items(db: Session = Depends(get_db), redis: redis.Redis = Depends(get_redis)):
    """Get all items, with Redis caching"""
    cache_key = "items:list"
    
    # Try to get from cache first
    if redis:
        try:
            cached = redis.get(cache_key)
            if cached:
                logger.info("Returning items from cache")
                import json
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Cache read failed: {e}")
    
    # Get from database
    items = db.query(Item).all()
    result = [ItemResponse.model_validate(item).model_dump() for item in items]
    
    # Store in cache
    if redis:
        try:
            import json
            redis.setex(cache_key, 60, json.dumps(result, default=str))  # Cache for 60 seconds
            logger.info("Stored items in cache")
        except Exception as e:
            logger.warning(f"Cache write failed: {e}")
    
    return result

@app.get("/stats")
async def get_stats(redis: redis.Redis = Depends(get_redis)):
    """Get API call statistics from Redis"""
    if not redis:
        return {"error": "Redis not available"}
    
    try:
        count = redis.incr("api:calls")
        return {"total_api_calls": count}
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

