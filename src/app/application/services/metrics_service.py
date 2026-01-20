from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.infrastructure.db.models import Product, Sale, Unit, Waiter


def _to_float(value: Any) -> float:
    return float(value) if value is not None else 0.0


@dataclass
class SummaryMetrics:
    revenue_total: float
    margin_total: float
    margin_pct: float
    ticket_medio: float
    pedidos: int

    def to_dict(self):
        return asdict(self)


class MetricsService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def summary(self) -> SummaryMetrics:
        query = self.session.execute(
            select(
                func.sum(Sale.total_value),
                func.sum(Sale.margin_value),
                func.count(Sale.id),
            )
        ).one()
        revenue_total, margin_total, pedidos = query
        margin_pct = (margin_total / revenue_total) if revenue_total else 0
        ticket_medio = (revenue_total / pedidos) if pedidos else 0
        return SummaryMetrics(
            revenue_total=_to_float(revenue_total),
            margin_total=_to_float(margin_total),
            margin_pct=_to_float(margin_pct),
            ticket_medio=_to_float(ticket_medio),
            pedidos=int(pedidos or 0),
        )

    def by_unit(self):
        stmt = (
            select(
                Unit.unit_code,
                Unit.name,
                func.sum(Sale.total_value).label("revenue"),
                func.sum(Sale.margin_value).label("margin"),
                (func.sum(Sale.margin_value) / func.sum(Sale.total_value)).label("margin_pct"),
                func.count(Sale.id).label("orders"),
            )
            .join(Sale.unit)
            .group_by(Unit.unit_code, Unit.name)
            .order_by(func.sum(Sale.total_value).desc())
        )
        rows = self.session.execute(stmt).all()
        return [
            {
                "unit_code": unit_code,
                "unit_name": unit_name,
                "revenue": _to_float(revenue),
                "margin": _to_float(margin),
                "margin_pct": _to_float(margin_pct),
                "orders": int(orders),
            }
            for unit_code, unit_name, revenue, margin, margin_pct, orders in rows
        ]

    def by_category(self):
        stmt = (
            select(
                Product.category,
                func.sum(Sale.total_value).label("revenue"),
                func.sum(Sale.margin_value).label("margin"),
                (func.sum(Sale.margin_value) / func.sum(Sale.total_value)).label("margin_pct"),
                func.count(Sale.id).label("orders"),
            )
            .join(Sale.product)
            .group_by(Product.category)
            .order_by(func.sum(Sale.total_value).desc())
        )
        rows = self.session.execute(stmt).all()
        return [
            {
                "category": category or "Sem categoria",
                "revenue": _to_float(revenue),
                "margin": _to_float(margin),
                "margin_pct": _to_float(margin_pct),
                "orders": int(orders),
            }
            for category, revenue, margin, margin_pct, orders in rows
        ]

    def monthly(self):
        stmt = (
            select(
                Sale.month_year,
                func.sum(Sale.total_value).label("revenue"),
                func.sum(Sale.margin_value).label("margin"),
                (func.sum(Sale.margin_value) / func.sum(Sale.total_value)).label("margin_pct"),
                func.count(Sale.id).label("orders"),
            )
            .group_by(Sale.month_year)
            .order_by(Sale.month_year)
        )
        rows = self.session.execute(stmt).all()
        return [
            {
                "month": month_year.isoformat(),
                "revenue": _to_float(revenue),
                "margin": _to_float(margin),
                "margin_pct": _to_float(margin_pct),
                "orders": int(orders),
            }
            for month_year, revenue, margin, margin_pct, orders in rows
        ]

    def by_waiter(self):
        stmt = (
            select(
                Waiter.name,
                func.sum(Sale.total_value).label("revenue"),
                func.sum(Sale.margin_value).label("margin"),
                (func.sum(Sale.margin_value) / func.sum(Sale.total_value)).label("margin_pct"),
                func.count(Sale.id).label("orders"),
            )
            .join(Sale.waiter)
            .group_by(Waiter.name)
            .order_by(func.sum(Sale.total_value).desc())
        )
        rows = self.session.execute(stmt).all()
        return [
            {
                "waiter": waiter,
                "revenue": _to_float(revenue),
                "margin": _to_float(margin),
                "margin_pct": _to_float(margin_pct),
                "orders": int(orders),
            }
            for waiter, revenue, margin, margin_pct, orders in rows
        ]

    def by_geography(self):
        stmt = (
            select(
                Unit.state,
                Unit.city,
                func.sum(Sale.total_value).label("revenue"),
                func.count(Sale.id).label("orders"),
            )
            .join(Sale.unit)
            .group_by(Unit.state, Unit.city)
            .order_by(func.sum(Sale.total_value).desc())
        )
        rows = self.session.execute(stmt).all()
        return [
            {
                "state": state or "ND",
                "city": city or "ND",
                "revenue": _to_float(revenue),
                "orders": int(orders),
            }
            for state, city, revenue, orders in rows
        ]
