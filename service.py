from pymongo.cursor import Cursor
from datetime import date, datetime, time, timedelta
from create_bot import bot
from enums import RepeatStatus  # pyright:ignore
import pymongo
import asyncio


async def check_repeat_time():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["memorize_bot"]
    users_collection = db["users"]
    try:
        users: Cursor = users_collection.find()
        for user in users:
            for index, data in enumerate(user["memorize_info"]):
                repeat_time_str = data["repeat_time"]
                repeat_time = datetime.strptime(repeat_time_str, "%Y-%m-%d %H:%M")
                current_time = datetime.now()
                if repeat_time <= current_time:
                    match data["repeat_count"]:
                        case RepeatStatus.FIRST.value:
                            update_repeat_time(
                                timedelta(minutes=35), index, user["_id"]
                            )
                            await bot.send_message(
                                chat_id=user["_id"],
                                text=f"Hi! Please repeat information: {data['info']}",
                            )
                            break
                        case RepeatStatus.SECOND.value:
                            update_repeat_time(timedelta(hours=9), index, user["_id"])
                            break
                        case RepeatStatus.THIRD.value:
                            update_repeat_time(timedelta(hours=24), index, user["_id"])
                            break
                        case RepeatStatus.FOURTH.value:
                            update_repeat_time(timedelta(days=3), index, user["_id"])
                            break
                        case RepeatStatus.FIFTH.value:
                            update_repeat_time(timedelta(days=7), index, user["_id"])
                            break
                        case _:
                            break
    finally:
        client.close()


def update_repeat_time(new_time: timedelta, index: int, user_id: str) -> None:
    pass
    # repeat_time = datetime.now()
    # update_time = (repeat_time + new_time).strftime("%Y-%m-%d %H:%M")
    # users_collection.update_one(
    #     {"_id": user_id}, {"$inc": {f"memorize_info.{index}.repeat_count": 1}}
    # )
    # check = users_collection.update_one(
    #     {"_id": user_id}, {"$set": {f"memorize_info.{index}.repeat_time": update_time}}
    # )


if __name__ == "__main__":
    asyncio.run(check_repeat_time())
