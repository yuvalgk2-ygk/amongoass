from pydantic import BaseModel


class DatabaseName(BaseModel):
    db_name: str
