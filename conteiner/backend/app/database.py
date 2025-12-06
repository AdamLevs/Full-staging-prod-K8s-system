import time
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import app.config as config

# Retry logic for database connection
for i in range(10):
    try:
        engine = create_engine(config.DATABASE_URL)
        connection = engine.connect()
        connection.close()
        break
    except Exception as e:
        print(f"Database not ready yet ({i+1}/10): {e}")
        time.sleep(5)
else:
    raise Exception("Database connection failed after multiple attempts.")

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()