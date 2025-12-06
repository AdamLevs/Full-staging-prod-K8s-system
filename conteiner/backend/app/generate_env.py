import os
import secrets

POSTGRES_USER = "Admin"
POSTGRES_PASSWORD = "Password"
POSTGRES_DB = "statuspage"
POSTGRES_PORT = "5432"
POSTGRES_HOST = "db"
REDIS_HOST = "redis"
REDIS_PORT = "6379"
REDIS_DB = "0"
SECRET_KEY = secrets.token_urlsafe(32)

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")

if not os.path.exists(env_path):
    with open(env_path, "w") as f:
        f.write(f"# POSTGRES SYSTEM USER\n")
        f.write(f"POSTGRES_USER={POSTGRES_USER}\n")
        f.write(f"POSTGRES_PASSWORD={POSTGRES_PASSWORD}\n")
        f.write(f"POSTGRES_DB={POSTGRES_DB}\n")
        f.write(f"POSTGRES_HOST={POSTGRES_HOST}\n")
        f.write(f"POSTGRES_PORT={POSTGRES_PORT}\n")
        f.write(f"DATABASE_URL={DATABASE_URL}\n")
        f.write("\n")
        f.write("# REDIS\n")
        f.write(f"REDIS_URL={REDIS_URL}\n")
        f.write(f"REDIS_PORT={REDIS_PORT}\n")
        f.write("\n")
        f.write("# SECRET KEY\n")
        f.write(f"SECRET_KEY={SECRET_KEY}\n")
        f.write(f"RUNNING_IN_DOCKER=true\n")

    print("✅ .env file generated successfully.")
else:
    print("✅ .env file already exists, skipping generation.")