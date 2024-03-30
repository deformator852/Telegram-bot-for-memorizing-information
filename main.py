from aiogram.utils.keyboard import InlineKeyboardBuilder
from create_bot import dp, bot  # pyright:ignore
from routers import bot_routers  # pyright:ignore
from pymongo.cursor import Cursor
from datetime import datetime, time, timedelta
from enums import RepeatStatus  # pyright:ignore
import pymongo
import asyncio
import logging
import sys
import multiprocessing


async def main():
    dp.include_router(bot_routers.router)
    await dp.start_polling(bot)


async def check_repeat_time():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["memorize_bot"]
    users_collection = db["users"]
    while True:
        users: Cursor = users_collection.find()
        for user in users:
            for index, data in enumerate(user["memorize_info"]):
                repeat_time_str = data["repeat_time"]
                repeat_time = datetime.strptime(repeat_time_str, "%Y-%m-%d %H:%M")
                current_time = datetime.now()
                if repeat_time <= current_time and data["send_repeating"] == False:
                    repeat_count = data["repeat_count"]
                    if repeat_count == RepeatStatus.FIRST.value:
                        await update_repeat_time(
                            data["info"],
                            index,
                            user["_id"],
                            {"minutes": 35},
                            1,
                            users_collection,
                        )
                    elif repeat_count == RepeatStatus.SECOND.value:
                        await update_repeat_time(
                            data["info"],
                            index,
                            user["_id"],
                            {"hours": 8},
                            2,
                            users_collection,
                        )
                    elif repeat_count == RepeatStatus.THIRD.value:
                        await update_repeat_time(
                            data["info"],
                            index,
                            user["_id"],
                            {"hours": 24},
                            3,
                            users_collection,
                        )
                    elif repeat_count == RepeatStatus.FOURTH.value:
                        await update_repeat_time(
                            data["info"],
                            index,
                            user["_id"],
                            {"days": 3},
                            4,
                            users_collection,
                        )
                    elif repeat_count == RepeatStatus.FIFTH.value:
                        await update_repeat_time(
                            data["info"],
                            index,
                            user["_id"],
                            {"days": 7},
                            5,
                            users_collection,
                        )


async def update_repeat_time(
    info: str, index: int, user_id: str, times: dict, repeat_status: int, users
) -> None:
    repeat_kb = InlineKeyboardBuilder()

    callback_data = ""
    if "minutes" in times:
        callback_data = f'repeat_{{"minutes": {times["minutes"]}, "index": {index},"repeat_status":{repeat_status}}}'
    elif "hours" in times:
        callback_data = f'repeat_{{"hours": {times["hours"]}, "index": {index},"repeat_status":{repeat_status}}}'
    else:
        callback_data = f'repeat_{{"days": {times["days"]}, "index": {index},"repeat_status":{repeat_status}}}'

    repeat_kb.button(text="I repeated", callback_data=callback_data)
    await bot.send_message(
        chat_id=user_id,
        text=f"Hi! Please repeat information: {info}",
        reply_markup=repeat_kb.as_markup(),
    )
    users.update_one(
        {"_id": user_id}, {"$set": {f"memorize_info.{index}.send_repeating": True}}
    )


def run_check():
    asyncio.run(check_repeat_time())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    multiprocessing.Process(target=run_check, daemon=True).start()
    asyncio.run(main())
