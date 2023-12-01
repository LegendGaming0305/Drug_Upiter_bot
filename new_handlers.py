from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import json
import pandas as pd

from main import dp, bot
from keyboards import keyboard, return_menu, country_menu, back_to_menu
from sql import get_info_from_db_substance, get_info_from_db_name
from cache_container import cache
from inline_menu_for_analogs import list_of_categories

# Создаем глобальный объект pandas dataframe, который будет использоваться для формирования таблицы лекарств
# Найденных по запросу пользователя  при поиске аналогов
USER_SEARCH_DATA = pd.DataFrame(columns=['Trade_name', 'Producer', 'Dosage_form', 'Dose', 'MNN', 'ID'])

# Создаем класс для state-ов памяти. Куда буду сохраняться сообщения пользователя для дальнейшего поиска в бд
class User_data(StatesGroup):
    chosen_country = State()
    name  = State()
    drug_name = State()
    active_substance = State()
    analog_info = State()

# Обрабатываем комманду /start после захода в бота и переходим в состояние получения имени от пользователя для взаимодействия
@dp.message_handler(commands=['start'])
async def registration_menu(message: types.Message):
    await message.answer('Как можно к Вам обращаться?')
    await User_data.name.set()

# Происходит только обработка состояния User_data.name. Где дальше предлагает выбор действия
# 1 - Поиск аналогов препарата
# 2 - Поиск препаратов по активному веществу
# Переходим в состояние выбора страны для поиска.
@dp.message_handler(state=User_data.name)
async def first_menu(message: types.Message, state: FSMContext):
    await state.update_data(username=message.text)
    data  = await state.get_data() # Достаем информацию из текущего состояния
    await state.finish()
    await message.answer(f'Привет, {data["username"]}!\n'
                         'Выберите страну в которой хотите найти лекарственное средство', reply_markup=country_menu)
    await User_data.chosen_country.set()

# Обрабатываем страну
@dp.message_handler(state=User_data.chosen_country)
async def menu_after_country(message: types.Message, state: FSMContext):
        await state.update_data(chosencountry=message.text) # Добавляем в память название страны
        await message.answer('Выберите кнопку "Поиск аналогов препарата" для того, '
                          'чтобы искать аналоги лекарственного препарата, которое Вы укажите. \n \n'
                          'Выберите кнопку "Поиск препаратов по активному веществу" для того, '
                          'чтобы получить перечень лекарственных препаратов, '
                          'содержащих в себе указанное Вами активное вещество. ', reply_markup=keyboard)
        await state.reset_state(with_data=False) # Закрываем состояние с сохранением информации

# Общее меню для возврата
@dp.message_handler(text='Меню', state='*')
async def first_menu_after_welcome_message(message: types.Message, state: FSMContext):
    await state.reset_state(with_data=False)
    await message.answer('Вы в главном меню! Выберите следующее действие.', reply_markup=keyboard)

# Возврат в состоянии поиска активного вещества, чтобы вводить новое активное вещество без повторения
# Многократных действий "Меню - Поиск по активному веществу"
@dp.message_handler(text='Назад', state=User_data.active_substance)
async def back_menu(message: types.Message, state: FSMContext):
    await message.answer('Введите другое активное вещество или попробуйте это же, но проверив на наличие ошибок в написании')    

# Возврат в меню выбора страны
@dp.message_handler(text='Выбор страны', state='*')
async def choose_country_menu(message: types.Message, state: FSMContext):
    await state.reset_state(with_data=True)
    await message.answer('Выберите страну', reply_markup=country_menu)
    await User_data.chosen_country.set()

# Обработка выбора "Поиск препаратов по активному веществу" и переход в состояние User_data.active_substance
@dp.message_handler(lambda message: message.text == 'Поиск препаратов по активному веществу', state='*')
async def active_substance_input(message: types.Message):
    await User_data.active_substance.set()
    await message.answer('Введите название активного вещества с заглавной буквы', reply_markup=return_menu)

# Сама обработка состояние User_data.active_substance и получение названия активного вещества
# Далее вызов функции для получения данных из БД
# Вывод по активному веществу
@dp.message_handler(state=User_data.active_substance)
async def active_substance_output(message: types.Message, state: FSMContext):
    # Обновляем данные состояния с новым введенным значением
    await state.update_data(drug_substance=message.text)
    # Получаем данные состояния
    drug_data = await state.get_data()
    drug_substance = drug_data['drug_substance']
    # await state.reset_state(with_data=True)
    await state.set_state('chosen_country')
    country_data = await state.get_data()
    country = country_data['chosencountry']
    chat_id = message.chat.id
    # Получаем информацию о лекарствах из базы данных
    records = await get_info_from_db_substance(drug_substance, country, chat_id)
    # Проверяем, что были найдены соответствующие записи
    if not records:
        await message.answer('Лекарства с таким активным веществом не было найдено.\n\n'
                             'Попробуйте внести другое активное вещество, нажав на кпопку "Назад"\n'
                             'Или нажмите кнопку "Меню", чтобы выбрать поиск по названию препарата или активному веществу', reply_markup=return_menu)
        await User_data.active_substance.set()
        return
    buttons = await create_inline_buttons_for_drug(records) # Создание кнопок
    await bot.send_message(chat_id, 'Выберите лекарство', reply_markup=buttons)
    await state.reset_state(with_data=False)
    await bot.send_message(chat_id, 'Для просмотра еще одного лекарства нажмите меню и повторите те же действия', reply_markup=back_to_menu)

# Обработка кнопки для поиска по названию препарата
@dp.message_handler(lambda message: message.text == 'Поиск по названию препарата', state=None)
async def drug_name_input(message: types.Message):
    await User_data.drug_name.set()
    await message.answer('Введите название лекарства для которого вы хотите найти аналог')

# Аналогично функции с активным веществом
# Вывод по названию препарата
@dp.message_handler(state=User_data.drug_name)
async def drug_name_output(message: types.Message, state: FSMContext):
    await state.update_data(drugname=message.text)
    data = await state.get_data()
    drug_name = data['drugname']
    await state.set_state('chosen_country')
    country_data = await state.get_data()
    country = country_data['chosencountry']
    chat_id = message.chat.id
    records = await get_info_from_db_name(drug_name, country, chat_id)
    if not records:
        await message.answer('Лекарства с таким активным веществом не было найдено.\n\n'
                             'Попробуйте внести другое активное вещество, нажав на кпопку "Назад"\n'
                             'Или нажмите кнопку "Меню", чтобы выбрать поиск по названию препарата или активному веществу', reply_markup=return_menu)
        await User_data.drug_name.set()
        return
    buttons = await create_inline_buttons_for_drug(records)
    chat_id = message.chat.id
    await bot.send_message(chat_id, 'Выберите лекарство', reply_markup=buttons)
    await state.reset_state(with_data=False)
    await bot.send_message(chat_id, 'Для просмотра еще одного лекарства нажмите меню и повторите те же действия', reply_markup=back_to_menu)

# Создание inline кнопок
async def create_inline_buttons_for_drug(medicines):
    markup = InlineKeyboardMarkup(row_width=3)
    buttons = []
    for medicine in medicines:
        title_drug = medicine[0]
        registrator_tran = medicine[1]
        registrator_country = medicine[2]
        producer_tran = medicine[3]
        producer_country = medicine[4]
        dosage_full_form = medicine[5]
        dose = medicine[6]
        sc_name = medicine[7]
        recipe_status = medicine[8]
        as_name_rus = medicine[9]
        id_drug = medicine[10]
        # Словарь с параметрами лекарства для сохранения в памяти
        drug_data = {
            'Название': title_drug,
            'Фирма-производитель': producer_tran,
            'Страна производителя': producer_country,
            'Лекарственная форма': dosage_full_form,
            'Дозировка': dose,
            'Условия хранения': sc_name,
            'Рецептура': recipe_status,
            'Действующие вещества': as_name_rus
        }

        data_id = str(id_drug)

        # Переводим данные в json формат
        serialized_data = json.dumps(drug_data)

        # Сохраняем в кэш память
        await cache.set(data_id, serialized_data)
        button = InlineKeyboardButton(text=title_drug, callback_data=f'medicine_info:{data_id}') # type: ignore
        
        buttons.append(button)
    # Разбиваем на столбцы
    button_lists = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]

    # Добавляем в клавиатуру
    for button_list in button_lists:
        markup.add(*button_list)

    return markup

# Обработчик кнопок для поиска по активному веществу
@dp.callback_query_handler(text_startswith='medicine_info:', state='*')
async def medicine_info_callback(call: types.CallbackQuery):
    callback_data = call.data.split(':')[1]
    data = await cache.get(callback_data) # Извлекаем именно это лекарство из кэша
    if data:
        drug_data = json.loads(data) # Получаем информацию о препарате
        result = ''
        for key, value in drug_data.items(): # Проходимся по этим элементам и достаем их
            result += f'{key}: {value}\n'

        await call.message.answer(f'Параметры лекарства:\n{result.strip()}')
    else:
        await call.message.answer('Данные не найдены')

# Обработка кнопки поиска аналогов
@dp.message_handler(text='Поиск аналогов препарата', state='*')
async def analog_button_used(message: types.Message, state: FSMContext):
    await message.answer('Введите название препарата, для которого Вы хотите найти аналог')
    await User_data.analog_info.set()


@dp.message_handler(state=User_data.analog_info)
async def analog_search(message: types.Message, state: FSMContext):
    await state.update_data(analogname=message.text)
    data = await state.get_data()
    drug_name = data['analogname']
    await User_data.chosen_country.set()
    country_data = await state.get_data()
    country = country_data['chosencountry']
    await User_data.analog_info.set()
    chat_id = message.chat.id
    records = await get_info_from_db_name(drug_name, country, chat_id)
    info_for_dataframe = dict()
    global USER_SEARCH_DATA
    index = 0
    for drug in records: # type: ignore
        info_for_dataframe['Trade_name'] = drug[0]
        info_for_dataframe['Producer'] = drug[3]
        info_for_dataframe['Dosage_form'] = drug[5]
        info_for_dataframe['Dose'] = drug[6]
        info_for_dataframe['MNN'] = drug[9]
        info_for_dataframe['ID'] = drug[10]
        data = pd.DataFrame(info_for_dataframe, index=[index])
        index += 1
        USER_SEARCH_DATA = pd.concat([USER_SEARCH_DATA, data])
    await list_of_categories(message)
