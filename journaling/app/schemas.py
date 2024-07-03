from pydantic import BaseModel
from typing import List, Optional
import datetime

class JournalBase(BaseModel):
    title: str
    content: str
    category: str
    date: datetime.datetime

class JournalCreate(JournalBase):
    pass

class Journal(JournalBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    journals: List[Journal] = []

    class Config:
        orm_mode = True
