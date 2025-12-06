import time
import requests
import socket
import dns.resolver
from urllib.parse import urlparse
from celery import Celery
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime
from app.models import Service, HealthCheck, ServerStats
from app.SSH import get_server_stats
import app.config as config
import ping3

celery = Celery('worker', broker=config.REDIS_URL)
engine = create_engine(config.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def perform_check(service):
    start = time.time()
    try:
        check_type = service.check_type.upper()
        if check_type == "HTTP":
            return check_http(service.check_target, start)
        elif check_type == "PING":
            return check_ping(service.check_target, start)
        elif check_type == "TCP":
            return check_tcp(service.check_target, start)
        elif check_type == "DNS":
            return check_dns(service.check_target, start)
        elif check_type == "SSH":
            return check_ssh_stats(service.check_target, start)
        else:
            return "DOWN", None, f"Unsupported check type: {check_type}"
    except Exception as e:
        return "DOWN", None, f"Unhandled error: {str(e)}"

def check_http(target, start):
    try:
        resp = requests.get(target, timeout=10, allow_redirects=True)
        response_time = time.time() - start

        print(f"[HTTP DEBUG] Target: {target} | Status: {resp.status_code} | URL after redirects: {resp.url}")

        if 200 <= resp.status_code < 400:
            return "UP", response_time, None
        else:
            return "DOWN", response_time, f"HTTP Status: {resp.status_code}"
    except requests.exceptions.RequestException as e:
        return "DOWN", None, f"HTTP error: {str(e)}"

def check_ping(target, start):
    try:
        ping3.EXCEPTIONS = True
        parsed = urlparse(target)
        host = parsed.hostname if parsed.hostname else target

        try:
            socket.gethostbyname(host)
        except socket.gaierror as dns_error:
            return "DOWN", None, f"DNS resolution failed: {dns_error}"

        latency = ping3.ping(host, timeout=3)
        response_time = time.time() - start

        if latency and latency > 0:
            return "UP", response_time, None
        else:
            return "DOWN", response_time, f"Ping latency invalid: {latency}"
    except Exception as e:
        return "DOWN", None, f"Ping error: {str(e)}"

def check_tcp(target, start):
    try:
        host, port = target.split(":")
        port = int(port)
        with socket.create_connection((host, port), timeout=5):
            response_time = time.time() - start
            return "UP", response_time, None
    except Exception as e:
        return "DOWN", None, f"TCP error: {str(e)}"

def check_dns(target, start):
    try:
        dns.resolver.resolve(target, lifetime=5)
        response_time = time.time() - start
        return "UP", response_time, None
    except Exception as e:
        return "DOWN", None, f"DNS error: {str(e)}"

def check_ssh_stats(target, start, service_id, db):
    try:
        stats = get_server_stats(target)
        response_time = time.time() - start

        if "error" not in stats:
            db.add(ServerStats(
                service_id=service_id,
                cpu_usage=stats.get("cpu_usage"),
                memory_usage=stats.get("memory_usage"),
                disk_usage=stats.get("disk_usage"),
            ))

        return "UP", response_time, None if "error" not in stats else stats["error"]
    except Exception as e:
        return "DOWN", None, f"SSH error: {str(e)}"

@celery.task
def check_services():
    db = SessionLocal()
    try:
        services = db.query(Service).filter(Service.is_active == True).all()
        now = datetime.utcnow()
        for service in services:
            if service.check_type.upper() == "SSH":
                status, response_time, error = check_ssh_stats(service.check_target, time.time(), service.id, db)
            else:
                status, response_time, error = perform_check(service)

            print(f"[{service.name}] Status: {status} | Time: {response_time} | Error: {error}")

            check = HealthCheck(
                service_id=service.id,
                status=status,
                response_time=response_time,
                error_message=error,
                checked_at=now
            )
            db.add(check)
            service.last_checked_at = now

        db.commit()
    except Exception as e:
        print(f"[Worker Error] {str(e)}")
        db.rollback()
    finally:
        db.close()

celery.conf.beat_schedule = {
    "check-every-5-seconds": {
        "task": "app.worker.check_services",
        "schedule": 5,
    }
}
