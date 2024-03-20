from os import stat
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, FSInputFile, Message
from keyboards.keyboards import Keyboards  # pyright:ignore
from aiogram.fsm.context import FSMContext
from states import AddNewInformation  # pyright:ignore

router = Router(name=__name__)
keyboards = Keyboards()


@router.callback_query(F.data == "start memorize")
async def start_memorize_callback(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer(
        "Write information: ", reply_markup=await keyboards.cancel_kb()
    )
    await state.set_state(AddNewInformation.information)


@router.message(AddNewInformation.information)
async def get_new_informaton(message: Message, state: FSMContext):
    await state.update_data(information=message.text)
    await message.answer(
        "Send image(if you have no image just write some number): ",
        reply_markup=await keyboards.cancel_kb(),
    )
    await state.set_state(AddNewInformation.image)


@router.message(AddNewInformation.image)
async def get_new_image(message: Message, state: FSMContext):
    data = await state.get_data()  # pyright:ignore
    information = data["information"]
    if message.content_type == "PHOTO":
        pass
    elif message.text == "1":
        pass
    await state.clear()


@router.message(Command("start"))
async def command_start(message: Message):
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
