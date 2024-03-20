from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


class Keyboards:
    @staticmethod
    async def start_kb():
        builder = ReplyKeyboardBuilder()
        builder.button(text="/profile")
        builder.button(text="/info")
        builder.button(text="/support")
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    async def profile_kb():
        builder = InlineKeyboardBuilder()
        builder.button(text="start memorize", callback_data="start memorize")
        builder.button(text="repeat", callback_data="repeat")
        builder.button(
            text="memorized information", callback_data="memorized information"
        )
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    async def cancel_kb():
        builder = InlineKeyboardBuilder()
        builder.button(text="cancel", callback_data="cancel")
        return builder.as_markup()
