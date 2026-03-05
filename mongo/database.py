from typing import List, Dict, Any

from pydantic import BaseModel, Field, model_validator


class Database(BaseModel):
    db_name: str
    username: str = Field(min_length=3)
    collection_name: str
    data: List[Dict[str, Any]]

    @model_validator(mode='after')
    def validate_db_name(self) :
        if not self.db_name.startswith(self.username):
            raise ValueError('Invalid database name - name must start with username: ' + self.username)
        return self
