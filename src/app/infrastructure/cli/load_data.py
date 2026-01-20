import argparse
from pathlib import Path

from app.application.services.ingestion_service import IngestionService
from app.infrastructure.db.session import SessionLocal


def main():
    parser = argparse.ArgumentParser(description="Load Excel/XML data into Postgres.")
    parser.add_argument(
        "--file",
        required=True,
        help="Path to Excel file (expecting sheets: Vendas, Produtos, Unidades).",
    )
    args = parser.parse_args()

    file_path = Path(args.file)
    session = SessionLocal()
    try:
        service = IngestionService(session)
        result = service.load_from_excel(file_path=file_path, truncate_before_load=True)
        print(
            f"Loaded products={result.products_loaded}, "
            f"units={result.units_loaded}, waiters={result.waiters_loaded}, "
            f"sales={result.sales_loaded}"
        )
    finally:
        session.close()


if __name__ == "__main__":
    main()
