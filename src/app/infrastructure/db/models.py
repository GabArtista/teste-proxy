from datetime import date, datetime
from uuid import uuid4

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Product(Base, TimestampMixin):
    __tablename__ = "product"

    id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    product_code: Mapped[str] = mapped_column(String(10), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    category: Mapped[str] = mapped_column(String(60), nullable=True)
    cost_unit: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    supplier: Mapped[str | None] = mapped_column(String(120), nullable=True)

    sales: Mapped[list["Sale"]] = relationship(back_populates="product")


class Unit(Base, TimestampMixin):
    __tablename__ = "unit"

    id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    unit_code: Mapped[str] = mapped_column(String(10), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    city: Mapped[str] = mapped_column(String(80), nullable=True)
    state: Mapped[str] = mapped_column(String(4), nullable=True)
    capacity_tables: Mapped[int | None] = mapped_column(Integer, nullable=True)
    manager: Mapped[str | None] = mapped_column(String(120), nullable=True)

    sales: Mapped[list["Sale"]] = relationship(back_populates="unit")


class Waiter(Base, TimestampMixin):
    __tablename__ = "waiter"

    id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)

    sales: Mapped[list["Sale"]] = relationship(back_populates="waiter")


class Sale(Base, TimestampMixin):
    __tablename__ = "sale"
    __table_args__ = (UniqueConstraint("order_code", name="uq_sale_order_code"),)

    id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    order_code: Mapped[str] = mapped_column(String(20), nullable=False)
    order_date: Mapped[date] = mapped_column(Date, nullable=False)
    month_year: Mapped[date] = mapped_column(Date, nullable=False)

    unit_id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), ForeignKey("unit.id"), nullable=False)
    waiter_id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), ForeignKey("waiter.id"), nullable=False)
    product_id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), ForeignKey("product.id"), nullable=False)

    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    total_value: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    margin_value: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    margin_pct: Mapped[float] = mapped_column(Float, nullable=False)

    product: Mapped[Product] = relationship(back_populates="sales")
    unit: Mapped[Unit] = relationship(back_populates="sales")
    waiter: Mapped[Waiter] = relationship(back_populates="sales")
