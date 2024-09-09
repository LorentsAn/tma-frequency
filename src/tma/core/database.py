from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from tma.core.settings import settings

engine = create_engine(settings.pg_dsn)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def create_database() -> None:
    with engine.begin() as session:
        Base.metadata.create_all(session)


def drop_database() -> None:
    with engine.begin() as session:
        Base.metadata.drop_all(session)
