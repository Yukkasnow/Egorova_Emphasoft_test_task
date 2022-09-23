from typing import Optional

from pydantic import BaseModel


class create_user(BaseModel):
    user_name: str
    first_name: str
    last_name: str
    password: str


class get_id(BaseModel):
    user_id: int


class update_user_pydantic(BaseModel):
    user_name: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    password: Optional[str]
