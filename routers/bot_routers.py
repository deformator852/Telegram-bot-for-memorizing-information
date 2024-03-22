from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, FSInputFile, Message
from keyboards.keyboards import Keyboards  # pyright:ignore
from aiogram.fsm.context import FSMContext
from states import AddNewInformation  # pyright:ignore
from pymongo.results import UpdateResult
from enums import RepeatStatus  # pyright:ignore
import pymongo

router = Router(name=__name__)
keyboards = Keyboards()
client = client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["memorize_bot"]
users = db["users"]


@router.callback_query(F.data == "start memorize")
async def start_memorize_callback(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer(
        "Write information: ", reply_markup=await keyboards.cancel_kb()
    )
    await state.set_state(AddNewInformation.information)


@router.message(AddNewInformation.information)
async def get_new_informaton(message: Message, state: FSMContext):
    repeat_time = datetime.now()
    repeat_time += timedelta(minutes=20)
    formated_time = repeat_time.strftime("%Y-%m-%d %H:%M")
    user_result: UpdateResult = users.update_one(
        {"_id": message.from_user.id},
        {
            "$push": {
                "memorize_info": {
                    "info": message.text,
                    "repeat_time": formated_time,
                    "repeat_count": RepeatStatus.FIRST.value,
                },
            }
        },
    )
    if user_result.modified_count > 0:
        await message.answer("Success! Next repetition in 20 minutes!")
    await state.clear()


@router.message(Command("start"))
async def command_start(message: Message):
    user_id = message.from_user.id
    user: dict | None = users.find_one({"_id": user_id})
    if user is None:
        users.insert_one({"_id": user_id, "memorize_info": []})

    await message.answer("Welcome!", reply_markup=await keyboards.start_kb())


@router.message(Command("profile"))
async def command_start_memorize(message: Message):
    await message.answer("profile:", reply_markup=await keyboards.profile_kb())


@router.message(Command("support"))
async def command_support(message: Message):
    pass


@router.message(Command("info"))
async def command_info(message: Message):
    await message.answer(
        """The Ebbinghaus Forgetting Curve highlights how memory fades over time without reinforcement. To combat this, practice spaced repetition by reviewing material shortly after learning, then gradually increase intervals:

1.)Review shortly after learning.

2.)Review again after one day.

3.)Review once more after one week.

4.)Repeat monthly to strengthen long-term memory retention.

"""
    )


@router.callback_query(F.data == "cancel")
async def cancel_state_callback(callback_query: CallbackQuery, state: FSMContext):
    await state.clear()
