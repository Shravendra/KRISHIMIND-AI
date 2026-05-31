from apps.db.session import engine, Base

from apps.db.models.user import User
from apps.db.models.conversation import Conversation
from apps.db.models.message import Message
from apps.db.models.image_analysis import ImageAnalysis


async def init_db():

    print("Creating database tables...")

    async with engine.begin() as conn:

        await conn.run_sync(
            Base.metadata.create_all
        )

    print("Database tables created")