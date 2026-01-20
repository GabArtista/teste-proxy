from sqlalchemy import text

from app.infrastructure.db.base import Base
from app.infrastructure.db.models import Product, Sale, Unit, Waiter  # noqa: F401
from app.infrastructure.db.session import engine


def run_migrations():
    with engine.begin() as conn:
        conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'))
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS citext;"))
        Base.metadata.create_all(conn)


if __name__ == "__main__":
    run_migrations()
    print("migrations completed")
