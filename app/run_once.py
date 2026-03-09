import asyncio
from app.config import get_settings
from app.services.publisher import publish_smart_post

async def main():
    settings = get_settings()
    await publish_smart_post(settings)

if __name__ == "__main__":
    asyncio.run(main())
