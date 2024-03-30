from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from keyboards.keyboards import Keyboards
from aiogram.fsm.context import FSMContext
from states import *
from pymongo.results import UpdateResult
from enums import RepeatStatus
from create_bot import bot, ADMINS_ID
import random
import pymongo
import json

router = Router(name=__name__)
keyboards = Keyboards()
client = client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["memorize_bot"]
users = db["users"]


@router.callback_query(F.data.startswith("accept-remove-info_"))
async def accept_remove_info(callback_query: CallbackQuery):
    info = callback_query.data[19:]
    remove_info = users.update_one(
        {"_id": callback_query.message.chat.id},
        {"$pull": {"memorize_info": {"info": info}}},
    )
    if remove_info.modified_count > 0:
        await callback_query.message.answer("Successfully removed!")


@router.callback_query(F.data.startswith("remove-info_"))
async def press_remove_info_button_callback(callback_query: CallbackQuery):
    info = callback_query.data[12:]
    builder = InlineKeyboardBuilder()
    builder.button(text="✅", callback_data=f"accept-remove-info_{info}")
    await callback_query.message.answer(
        f"Are you sure that wanna remove this information - {info}?",
        reply_markup=builder.as_markup(),
    )


@router.callback_query(F.data == "remove info")
async def remove_info_callback(callback_query: CallbackQuery):
    user_memorize_info = users.find_one(
        {"_id": callback_query.message.chat.id}, {"memorize_info": 1, "_id": 0}
    )
    if user_memorize_info:
        for data in user_memorize_info["memorize_info"]:
            builder = InlineKeyboardBuilder()
            builder.button(text="remove", callback_data=f"remove-info_{data['info']}")
            await callback_query.message.answer(
                f"INFO - {data['info']}", reply_markup=builder.as_markup()
            )


@router.callback_query(F.data == "list info")
async def list_info_callback(callback_query: CallbackQuery):
    user_memorize_info = users.find_one(
        {"_id": callback_query.message.chat.id}, {"memorize_info": 1, "_id": 0}
    )
    if user_memorize_info:
        for data in user_memorize_info["memorize_info"]:
            await callback_query.message.answer(f"INFO - {data['info']}")


@router.callback_query(F.data == "start memorize")
async def start_memorize_callback(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer(
        "Write information: ", reply_markup=await keyboards.cancel_kb()
    )
    await state.set_state(AddNewInformation.INFORMATION)


@router.message(AddNewInformation.INFORMATION)
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
                    "send_repeating": False,
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
    if user_id in ADMINS_ID:
        await message.answer(
            "Hello admin!In case you receive a message from a user through support you will receive a link to the user's account for further communication.",
            reply_markup=await keyboards.admin_kb(),
        )
    elif user is None:
        users.insert_one({"_id": user_id, "memorize_info": []})
        await message.answer("Welcome!", reply_markup=await keyboards.start_kb())


@router.message(Command("profile"))
async def command_start_memorize(message: Message):
    await message.answer("profile:", reply_markup=await keyboards.profile_kb())


@router.message(Command("support"))
async def command_support(message: Message, state: FSMContext):
    await message.answer(
        "Send your message(In order for an admin to message you you must enable message forwarding in the privacy settings.): "
    )
    await state.set_state(SendMessageToSupport.MESSAGE)


@router.message(SendMessageToSupport.MESSAGE)
async def get_support_message(message: Message, state: FSMContext):
    support_message = message.text
    admin = random.choice(ADMINS_ID)
    await bot.send_message(
        admin,
        f"Message from <a href='tg://user?id={message.from_user.id}'>{message.from_user.full_name}</a>.Text - {support_message}  ",
    )
    await message.answer("Wait for a reply, the admin will contact you!")
    await state.clear()


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


@router.callback_query(F.data.startswith("repeat_"))
async def repeat_data(callback_query: CallbackQuery):
    data_str = callback_query.data[7:]
    data_dict = json.loads(data_str)
    index = data_dict["index"]
    user_id = callback_query.from_user.id
    repeat_time = datetime.now()
    update_time = ""
    chat_id = callback_query.message.chat.id
    message_id = callback_query.message.message_id
    await bot.delete_message(chat_id, message_id)
    if "minutes" in data_dict:
        update_time = repeat_time + timedelta(minutes=data_dict["minutes"])
    elif "hours" in data_dict:
        update_time = repeat_time + timedelta(minutes=data_dict["hours"])
    else:
        update_time = repeat_time + timedelta(minutes=data_dict["days"])

    update_time = update_time.strftime("%Y-%m-%d %H:%M")

    repeat_time_update = users.update_one(
        {"_id": user_id},
        {"$set": {f"memorize_info.{index}.repeat_time": update_time}},
    )
    users.update_one(
        {"_id": user_id}, {"$inc": {f"memorize_info.{index}.repeat_count": 1}}
    )
    users.update_one(
        {"_id": user_id}, {"$set": {f"memorize_info.{index}.send_repeating": False}}
    )
    if repeat_time_update.modified_count > 0:
        match data_dict["repeat_status"]:
            case RepeatStatus.FIRST.value:
                await callback_query.message.answer(
                    f"You have successfully repeated the information! The next repeat in: 35 minutes! "
                )
            case RepeatStatus.SECOND.value:
                await callback_query.message.answer(
                    f"You have successfully repeated the information! The next repeat in: 8 hours! "
                )
            case RepeatStatus.THIRD.value:
                await callback_query.message.answer(
                    f"You have successfully repeated the information! The next repeat in: 24 hours! "
                )
            case RepeatStatus.FOURTH.value:
                await callback_query.message.answer(
                    f"You have successfully repeated the information! The next repeat in: 3 days! "
                )
            case RepeatStatus.FIFTH.value:
                await callback_query.message.answer(
                    f"You have successfully repeated the information! The next repeat in: 7 days! "
                )


@router.callback_query(F.data == "cancel")
async def cancel_state_callback(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Successfully canceled")
    await state.clear()
