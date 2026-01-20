from fastapi import Depends, FastAPI

from app.application.services.metrics_service import MetricsService
from app.infrastructure.db.session import get_session

app = FastAPI(title="Sabores Observability API", version="1.0.0")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/metrics/summary")
def metrics_summary(session=Depends(get_session)):
    service = MetricsService(session)
    return service.summary().to_dict()


@app.get("/metrics/units")
def metrics_by_unit(session=Depends(get_session)):
    service = MetricsService(session)
    return service.by_unit()


@app.get("/metrics/categories")
def metrics_by_category(session=Depends(get_session)):
    service = MetricsService(session)
    return service.by_category()


@app.get("/metrics/monthly")
def metrics_monthly(session=Depends(get_session)):
    service = MetricsService(session)
    return service.monthly()


@app.get("/metrics/waiters")
def metrics_by_waiter(session=Depends(get_session)):
    service = MetricsService(session)
    return service.by_waiter()


@app.get("/metrics/geography")
def metrics_geography(session=Depends(get_session)):
    service = MetricsService(session)
    return service.by_geography()
