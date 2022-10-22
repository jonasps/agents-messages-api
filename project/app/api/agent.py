from typing import List, Union, Optional
import datetime
import asyncio

from fastapi import Depends, APIRouter, HTTPException, BackgroundTasks
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import Agent, AgentCreate, Message, MessageCreate, MessageDelete
from app.api.utils import get_agent_id_by_name, update_fetched_messages_if_needed

router = APIRouter()


@router.get("/agents", response_model=List[Agent])
async def get_all_agents(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Agent))
    agents = result.scalars().all()
    return agents


@router.post("/agents", response_model=Agent)
async def add_agent(agent: AgentCreate, session: AsyncSession = Depends(get_session)):
    try:
        agent = Agent(name=agent.name)
        session.add(agent)
        await session.commit()
        await session.refresh(agent)
        return agent
    except:
        raise HTTPException(status_code=400, detail="Bad agent name")


@router.get("/agents/{agent_name}/messages")
async def get_all_messages(
    agent_name: str,
    background_tasks: BackgroundTasks,
    new: Optional[bool] = False,
    start_date: Union[datetime.date, None] = None,
    end_date: Union[datetime.date, None] = None,
    session: AsyncSession = Depends(get_session),
):
    agent_id: int = await get_agent_id_by_name(session, agent_name)
    messages_q = select(Message).where(Message.receiver_id == agent_id)

    if new:
        # Only query for messages not previusly fetched.
        messages_q = messages_q.where(Message.fetched_at == None)

    # Check if query should be filterd by start/end date.
    if start_date:
        messages_q = messages_q.where(Message.created_at > start_date)

    if end_date:
        messages_q = messages_q.where(Message.created_at < end_date)

    messages_q = messages_q.options(selectinload(Message.sender))
    result = await session.execute(messages_q)
    messages = result.scalars().all()

    # Update fetched_at in the background for new messages
    fetched_at = datetime.datetime.utcnow()
    background_tasks.add_task(
        update_fetched_messages_if_needed, messages, session, fetched_at
    )

    # It should be possible to just use ´response_model=Message´ instead of this list comprehension.
    # But for unknown reasons the sender is not included in the response when doing that.
    return [{key: value for (key, value) in message} for message in messages]


@router.post("/agents/{agent_name}/messages")
async def add_message(
    agent_name: str,
    message: MessageCreate,
    session: AsyncSession = Depends(get_session),
):

    sender_id, reciver_id = await asyncio.gather(
        *[
            get_agent_id_by_name(session, message.sender_name),
            get_agent_id_by_name(session, agent_name),
        ]
    )
    message = Message(text=message.text, sender_id=sender_id, receiver_id=reciver_id)

    session.add(message)
    await session.commit()
    await session.refresh(message)
    return message


@router.delete("/agents/{agent_name}/messages")
async def delete_messages(
    agent_name: str,
    message_delete: MessageDelete,
    session: AsyncSession = Depends(get_session),
):
    try:
        agent_id: int = await get_agent_id_by_name(session, agent_name)

        messages_q = (
            select(Message)
            .where(Message.receiver_id == agent_id)
            .where(Message.id.in_(message_delete.ids))
        )
        result = await session.execute(messages_q)
        messages = result.all()

        if len(messages) == 0:
            raise

        deleted_messages = 0
        for message in messages:
            deleted_messages += 1
            await session.delete(message[0])

        await session.commit()
        return {"success": f"{deleted_messages} messages deleted"}
    except:
        raise HTTPException(status_code=400, detail=f"Error, No messages deleted")
