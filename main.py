import logging
import asyncio
import sys
from create_bot import dp,bot #pyright:ignore 
from routers import bot_routers #pyright:ignore

async def main():
    dp.include_router(bot_routers.router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
