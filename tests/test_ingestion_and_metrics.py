from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.application.services.ingestion_service import IngestionService
from app.application.services.metrics_service import MetricsService
from app.infrastructure.db.base import Base


@pytest.fixture(scope="session")
def data_path() -> Path:
    return Path(__file__).resolve().parent.parent / "data" / "sabores.xlsx"


@pytest.fixture()
def session():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, autoflush=False, future=True)
    with SessionLocal() as session:
        yield session
    engine.dispose()


@pytest.fixture()
def loaded_session(session, data_path: Path):
    service = IngestionService(session)
    service.load_from_excel(data_path, truncate_before_load=True)
    return session


def test_ingestion_counts(loaded_session):
    # Data comes from the provided Excel; ensure full load into dimensions + fact.
    product_count = loaded_session.execute("select count(*) from product").scalar_one()
    unit_count = loaded_session.execute("select count(*) from unit").scalar_one()
    waiter_count = loaded_session.execute("select count(*) from waiter").scalar_one()
    sale_count = loaded_session.execute("select count(*) from sale").scalar_one()

    assert product_count == 10
    assert unit_count == 5
    assert waiter_count == 4
    assert sale_count == 10


def test_summary_metrics(loaded_session):
    metrics = MetricsService(loaded_session).summary()
    assert metrics.revenue_total == pytest.approx(526)
    assert metrics.margin_total == pytest.approx(328)
    assert metrics.margin_pct == pytest.approx(0.623574, rel=1e-4)
    assert metrics.ticket_medio == pytest.approx(52.6)
    assert metrics.pedidos == 10


def test_metrics_by_unit(loaded_session):
    units = MetricsService(loaded_session).by_unit()
    assert [u["unit_code"] for u in units] == ["U01", "U03", "U02"]
    top = units[0]
    assert top["revenue"] == pytest.approx(230)
    assert top["margin_pct"] == pytest.approx(0.608696, rel=1e-4)


def test_metrics_by_category(loaded_session):
    categories = MetricsService(loaded_session).by_category()
    assert [c["category"] for c in categories] == ["Pratos", "Bebidas", "Porções"]
    assert categories[1]["margin_pct"] == pytest.approx(0.74, rel=1e-3)


def test_metrics_monthly(loaded_session):
    monthly = MetricsService(loaded_session).monthly()
    assert [m["month"] for m in monthly] == ["2025-01-01", "2025-02-01"]
    assert monthly[0]["revenue"] == pytest.approx(303)
    assert monthly[1]["revenue"] == pytest.approx(223)


def test_metrics_by_waiter(loaded_session):
    waiters = MetricsService(loaded_session).by_waiter()
    assert [w["waiter"] for w in waiters][:2] == ["Marcos Lima", "João Silva"]
    assert waiters[0]["revenue"] == pytest.approx(186)
    assert waiters[-1]["revenue"] == pytest.approx(46)


def test_metrics_geography(loaded_session):
    geo = MetricsService(loaded_session).by_geography()
    assert geo[0]["city"] == "São Paulo"
    assert geo[0]["revenue"] == pytest.approx(230)
    assert {g["state"] for g in geo} == {"SP", "RS"}
