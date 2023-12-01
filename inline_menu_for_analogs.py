from typing import Union
from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

from getting_information import get_categories, get_subcategories, get_sub_subcategories
from main import dp

menu_cd = CallbackData("menu", "level", "category", "subcategory", "sub_subcategory")

GLOBAL_LIST_OF_MENU = {}

def make_callback_data(level, category='0', subcategory='0', sub_subcategory='0'):
    return menu_cd.new(level=level, category=category, subcategory=subcategory, sub_subcategory=sub_subcategory)


async def list_of_categories(message: Union[types.Message, types.CallbackQuery], **kwargs):
    markup = await categories_keyboard()

    if isinstance(message, types.Message):
        await message.answer(
                    'Выберите категорию',
                    reply_markup=markup
                )
    elif isinstance(message, types.CallbackQuery):
        call = message
        await call.message.edit_reply_markup(reply_markup=markup)

async def list_of_subcategories(callback: types.CallbackQuery, category, **kwargs):
    markup = await subcategories_keyboard(category=category)
    await callback.message.edit_reply_markup(reply_markup=markup)
    
async def list_of_sub_subcategories(callback: types.CallbackQuery, category, subcategory, **kwargs):
    markup = await categories_in_subcategories(category=category, subcategory=subcategory)
    await callback.message.edit_reply_markup(reply_markup=markup)


async def categories_keyboard():
    categories = await get_categories() # dict
    CURRENT_LEVEL = 0
    markup = InlineKeyboardMarkup(row_width=3)
    global GLOBAL_LIST_OF_MENU

    for key, value in categories.items():
        button_text = value
        callback_data = make_callback_data(CURRENT_LEVEL + 1, category=f'category-{key}')
        markup.add(InlineKeyboardButton(text=button_text, callback_data=callback_data)) # type: ignore
        GLOBAL_LIST_OF_MENU[f'category-{key}'] = button_text
    return markup

async def subcategories_keyboard(category, **kwargs):
    CURRENT_LEVEL = 1
    markup = InlineKeyboardMarkup(row_width=3)
    global GLOBAL_LIST_OF_MENU
    subcategories = await get_subcategories(category) # dict

    for key, value in subcategories.items():
        button_text = value
        callback_data = make_callback_data(CURRENT_LEVEL + 1, category=category, subcategory=f'subcategory-{key}')
        markup.add(InlineKeyboardButton(text=button_text, callback_data=callback_data)) # type: ignore
        GLOBAL_LIST_OF_MENU[f'subcategory-{key}'] = button_text

    markup.row(
        InlineKeyboardButton(text='Назад',
                             callback_data=make_callback_data(CURRENT_LEVEL - 1)) # type: ignore
    )
    return markup

async def categories_in_subcategories(category, subcategory, **kwargs):
    CURRENT_LEVEL = 2
    markup = InlineKeyboardMarkup(row_width=3)
    global GLOBAL_LIST_OF_MENU
    sub_subcategories = await get_sub_subcategories(category=category, subcategory=subcategory)

    for key, value in sub_subcategories.items():
        button_text = value
        callback_data = make_callback_data(CURRENT_LEVEL, category=category, subcategory=subcategory,
                                           sub_subcategory=f'sub_subcategory-{key}')
        markup.add(InlineKeyboardButton(text=button_text, callback_data=callback_data)) # type: ignore
        GLOBAL_LIST_OF_MENU[f'sub_subcategory-{key}'] = button_text

    markup.row(
        InlineKeyboardButton(text='Назад',
                             callback_data=make_callback_data(CURRENT_LEVEL - 1, category=category,
                                                              subcategory=subcategory)) # type: ignore
    )

    return markup

@dp.callback_query_handler(menu_cd.filter(), state='*')
async def navigate(call: types.CallbackQuery, callback_data: dict):
    current_level = callback_data.get('level')
    category = callback_data.get('category')
    subcategory = callback_data.get('subcategory')

    levels = {
        '0': list_of_categories,
        '1': list_of_subcategories,
        '2': list_of_sub_subcategories
    }

    current_level_function = levels[current_level] # type: ignore
    await current_level_function(call, category=category, subcategory=subcategory)
