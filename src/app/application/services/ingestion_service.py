from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable

import pandas as pd
from sqlalchemy.orm import Session

from app.infrastructure.db import models


@dataclass
class IngestionResult:
    products_loaded: int
    units_loaded: int
    waiters_loaded: int
    sales_loaded: int


class IngestionService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def load_from_excel(self, file_path: Path, truncate_before_load: bool = True) -> IngestionResult:
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        xls = pd.ExcelFile(file_path)
        products_df = pd.read_excel(xls, "Produtos")
        units_df = pd.read_excel(xls, "Unidades")
        sales_df = pd.read_excel(xls, "Vendas")

        if truncate_before_load:
            self._clear_tables()

        products = self._upsert_products(products_df)
        units = self._upsert_units(units_df)
        waiters = self._upsert_waiters(sales_df["Garcom"].dropna().unique())
        sales_loaded = self._insert_sales(sales_df, products, units, waiters)

        self.session.commit()

        return IngestionResult(
            products_loaded=len(products),
            units_loaded=len(units),
            waiters_loaded=len(waiters),
            sales_loaded=sales_loaded,
        )

    def _clear_tables(self) -> None:
        self.session.query(models.Sale).delete()
        self.session.query(models.Product).delete()
        self.session.query(models.Unit).delete()
        self.session.query(models.Waiter).delete()
        self.session.flush()

    def _upsert_products(self, df: pd.DataFrame) -> dict[str, models.Product]:
        products: dict[str, models.Product] = {}
        for _, row in df.iterrows():
            code = str(row["Produto_ID"]).strip()
            product = models.Product(
                product_code=code,
                name=str(row["Produto"]).strip(),
                category=str(row.get("Categoria", "")).strip() or None,
                cost_unit=float(row["Custo_Unitario"]),
                price=float(row["Preco_Venda"]),
                supplier=str(row.get("Fornecedor", "")).strip() or None,
            )
            self.session.add(product)
            products[code] = product
        self.session.flush()
        return products

    def _upsert_units(self, df: pd.DataFrame) -> dict[str, models.Unit]:
        units: dict[str, models.Unit] = {}
        for _, row in df.iterrows():
            code = str(row["Unidade_ID"]).strip()
            unit = models.Unit(
                unit_code=code,
                name=str(row["Nome_Unidade"]).strip(),
                city=str(row.get("Cidade", "")).strip() or None,
                state=str(row.get("Estado", "")).strip() or None,
                capacity_tables=int(row["Capacidade_Mesas"]) if not pd.isna(row["Capacidade_Mesas"]) else None,
                manager=str(row.get("Gerente", "")).strip() or None,
            )
            self.session.add(unit)
            units[code] = unit
        self.session.flush()
        return units

    def _upsert_waiters(self, names: Iterable[str]) -> dict[str, models.Waiter]:
        waiters: dict[str, models.Waiter] = {}
        for name in names:
            clean_name = str(name).strip()
            waiter = models.Waiter(name=clean_name)
            self.session.add(waiter)
            waiters[clean_name] = waiter
        self.session.flush()
        return waiters

    def _insert_sales(
        self,
        df: pd.DataFrame,
        products: dict[str, models.Product],
        units: dict[str, models.Unit],
        waiters: dict[str, models.Waiter],
    ) -> int:
        count = 0
        for _, row in df.iterrows():
            product_code = str(row["Produto_ID"]).strip()
            unit_code = str(row["Unidade_ID"]).strip()
            waiter_name = str(row["Garcom"]).strip()
            product = products[product_code]
            unit = units[unit_code]
            waiter = waiters[waiter_name]

            order_date = self._parse_date(row["Data_Pedido"])
            quantity = int(row["Quantidade"])
            unit_price = float(row["Valor_Unitario"])
            total_value = float(row["Valor_Total"])
            margin_value = (float(product.price) - float(product.cost_unit)) * quantity
            margin_pct = margin_value / total_value if total_value else 0
            month_year = date(order_date.year, order_date.month, 1)

            sale = models.Sale(
                order_code=str(row["ID_Pedido"]),
                order_date=order_date,
                month_year=month_year,
                unit=unit,
                waiter=waiter,
                product=product,
                quantity=quantity,
                unit_price=unit_price,
                total_value=total_value,
                margin_value=margin_value,
                margin_pct=margin_pct,
            )
            self.session.add(sale)
            count += 1
        return count

    @staticmethod
    def _parse_date(value) -> date:
        if isinstance(value, pd.Timestamp):
            return value.date()
        if isinstance(value, date):
            return value
        return pd.to_datetime(value).date()
