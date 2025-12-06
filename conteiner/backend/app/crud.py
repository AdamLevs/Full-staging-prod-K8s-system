from sqlalchemy.orm import Session
from app import models, schemas, auth, config
from typing import Optional
from app.models import Service, HealthCheck, ServerStats

# Health Checks
def get_health_checks(db: Session, service_id: int):
    return db.query(HealthCheck).filter(HealthCheck.service_id == service_id).order_by(HealthCheck.checked_at.desc()).limit(10).all()

# Users
def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = auth.hash_password(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()

def get_user(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()

# Services
def create_service(db: Session, service: schemas.ServiceCreate):
    db_service = models.Service(**service.dict())
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service

def get_services(db: Session):
    return db.query(models.Service).all()

def get_service(db: Session, service_id: int):
    return db.query(models.Service).filter(models.Service.id == service_id).first()

def get_latest_stats(db: Session, service_id: int) -> Optional[ServerStats]:
    return db.query(ServerStats)\
             .filter(ServerStats.service_id == service_id)\
             .order_by(ServerStats.created_at.desc())\
             .first()

def delete_service(db: Session, service_id: int) -> bool:
    service = db.query(models.Service).filter(models.Service.id == service_id).first()
    if not service:
        return False
    db.delete(service)
    db.commit()
    return True