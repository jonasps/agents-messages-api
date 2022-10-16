import datetime
from typing import List, Optional

from pydantic import constr
from sqlmodel import SQLModel, Field, Relationship

AgentNameType = constr(regex="^[A-Za-z0-9_-]*$")


class AgentBase(SQLModel):
    name: AgentNameType = Field(default="string")


class Agent(AgentBase, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    messages_sent: List["Message"] = Relationship(back_populates="sender")


class AgentCreate(AgentBase):
    pass


class MessageBase(SQLModel):
    text: str


class Message(MessageBase, table=True):
    id: int = Field(default=None, primary_key=True)
    receiver_id: int
    sender_id: Optional[int] = Field(default=None, foreign_key="agent.id")
    sender: Optional[Agent] = Relationship(back_populates="messages_sent")
    created_at: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow, nullable=False
    )
    fetched_at: datetime.datetime = Field(default=None, nullable=True)


class MessageCreate(MessageBase):
    sender_name: str


class MessageDelete(SQLModel):
    sender_name: str
    ids: List[int]
