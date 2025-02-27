from contextlib import contextmanager
from sqlalchemy import text
from .main import Base, engine, SessionLocal
from sqlalchemy.exc import SQLAlchemyError

def test_db_connection(engine) -> bool:
    """Test database connection by executing a simple query."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            return True
    except Exception as e:
    
        return False


def init_db():
    try:
        from .models import (
            Product,
            ProductSage
        )  # noqa

        # Create database tables
        Base.metadata.create_all(bind=engine)

        # Test database connection
        if not test_db_connection(engine):
            raise SQLAlchemyError("Database connection test failed")
        print("Database initialized successfully")

        return True

    except Exception as ex:

        raise


@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()