from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from models.user import User
from database import session_maker


async def get_history(email: str) -> list[dict]:
    """Get chat history for a user."""
    return []


async def clear_history(email: str) -> None:
    """Clear chat history for a user."""
    pass


async def add_message(email: str, message: str) -> None:
    """Add a message to user's chat history."""
    pass


async def get_all_dialog_user() -> list[str]:
    """Get all users who have active dialogs."""
    async with session_maker() as session:
        result = await session.execute(select(User.email))
        return result.scalars().all()
