import uuid
import enum

from sqlalchemy import String, Enum, DateTime, create_engine
from sqlalchemy.orm import declarative_base, Mapped, mapped_column

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
LOGGER = logging.getLogger(__name__)

class Status(enum.Enum):
    CREATED = 'created',
    DELETED = 'deleted'


Base = declarative_base()

class Deployments(Base):
    __tablename__ = 'deployments'
    id: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4(), primary_key=True)
    db_name: Mapped[str] = mapped_column(String(30))
    status: Mapped[Enum] = mapped_column(Enum(Status))
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