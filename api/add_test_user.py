import asyncio
from database import session_maker
from utils import hash_password
from models.user import User
from sqlmodel import select


async def add_test_user():
    async with session_maker() as session:
        # Check if user exists
        result = await session.execute(select(User).filter(User.email == "test@example.com"))
        user = result.scalar_one_or_none()
        
        if not user:
            user = User(
                email="test@example.com",
                role="common_user",
                password=hash_password("password123"),
                last_visit=None
            )
            session.add(user)
            await session.commit()
            print("User added successfully!")
        else:
            print("User already exists!")


if __name__ == "__main__":
    asyncio.run(add_test_user())
