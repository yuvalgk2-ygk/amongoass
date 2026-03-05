import uuid
from typing import Literal, get_args

from sqlalchemy import String, Enum, DateTime, create_engine, func
from sqlalchemy.orm import declarative_base, Mapped, mapped_column

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
LOGGER = logging.getLogger(__name__)

Status = Literal['created', 'deleted']

Base = declarative_base()

class Deployments(Base):
    __tablename__ = 'deployments'
    id: Mapped[uuid.UUID] = mapped_column(server_default=func.gen_random_uuid(), primary_key=True)
    db_name: Mapped[str] = mapped_column(String(30))
    status: Mapped[Status] = mapped_column(Enum(
        *get_args(Status),
        name="database_status",
        create_constraint=True,
        validate_strings=True,
    ))
    username: Mapped[str] = mapped_column(String(30))
    creation_time: Mapped[DateTime] = mapped_column(DateTime)


def get_db_engine():
    engine = create_engine('postgresql+psycopg2://{}:{}@{}/{}'.format('postgres', 'postgres', 'localhost:5432', 'a_mongo_ass_db'))
    Base.metadata.create_all(engine)
    return engine

while True:
    try:
        db_engine = get_db_engine().connect()
        if db_engine:
            break
    except Exception as e:
        LOGGER.warning(f"++++ Retrying connection to the db bc of the issue {str(e)}++++")