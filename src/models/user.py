from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import uuid


class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    name: str
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


class User(UserBase, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    password_hash: str
    # Set updated_at to current time on update
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow, nullable=False)


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: str