from typing import Union, List
import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import Agent, Message


async def get_agent_id_by_name(session: AsyncSession, name: str) -> Union[Agent, None]:
    """Returns ´Agent´ matching name or None"""
    agent_by_name_q = select(Agent).where(Agent.name == name)
    result = await session.execute(agent_by_name_q)
    agent_id: int = result.first()[0].id
    return agent_id


async def update_fetched_messages_if_needed(
    messages: List[Message], session: AsyncSession
) -> None:
    for message in messages:
        if not message.fetched_at:
            message.fetched_at = datetime.datetime.utcnow()
            session.add(message)
    await session.commit()