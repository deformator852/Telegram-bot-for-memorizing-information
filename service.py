from pymongo.cursor import Cursor
from datetime import date, datetime
from create_bot import bot
from enums import RepeatStatus  # pyright:ignore
import pymongo


def main() -> None:
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["memorize_bot"]
    users_collection = db["users"]
    check_repeat_time(users_collection)


def check_repeat_time(users_collection):
    users: Cursor = users_collection.find()
    for user in users:
        for data in user["memorize_info"]:
            repeat_time_str = data["repeat_time"]
            repeat_time = datetime.strptime(repeat_time_str, "%Y-%m-%d %H:%M")
            current_time = datetime.now()
            if repeat_time <= current_time:
                match data["repeat_count"]:
                    case RepeatStatus.FIRST.value:
                        print(1)
                        break
                    case RepeatStatus.SECOND.value:
                        print(2)
                        break
                    case RepeatStatus.THIRD.value:
                        print(3)
                        break
                    case RepeatStatus.FOURTH.value:
                        print(4)
                        break
                    case RepeatStatus.FIFTH.value:
                        print(5)
                        break
                    case _:
                        break


if __name__ == "__main__":
    main()
