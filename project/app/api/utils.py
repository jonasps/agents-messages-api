from typing import Union, List
import datetime

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import Agent, Message


async def get_agent_id_by_name(session: AsyncSession, name: str) -> Union[Agent, Exception]:
    """Returns ´Agent´ matching name or None"""
    agent_by_name_q = select(Agent).where(Agent.name == name)
    result = await session.execute(agent_by_name_q)
    try:
        agent_id: int = result.first()[0].id
        return agent_id
    except:
        raise HTTPException(
            status_code=400,
            detail=f"Error, agent_name {name} not found",
        )


async def update_fetched_messages_if_needed(
    messages: List[Message],
    session: AsyncSession,
    fetched_at: datetime
) -> None:
    for message in messages:
        if not message.fetched_at:
            message.fetched_at = fetched_at
            session.add(message)
    await session.commit()