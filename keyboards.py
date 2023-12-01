from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import emoji


# ----- Menu for drug find -----
name_drug_button = KeyboardButton('Поиск по названию препарата')
substance_button = KeyboardButton('Поиск препаратов по активному веществу')
analog_button = KeyboardButton('Поиск аналогов препарата')
keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2).add(name_drug_button, substance_button, analog_button)

# ----- Return menu -----
return_button = KeyboardButton('Меню')
back_button = KeyboardButton('Назад')
country_selection = KeyboardButton('Выбор страны')
# drug_selection = KeyboardButton('Выбрать лекарство')
return_menu = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2).add(back_button, return_button,country_selection)
# Для отображения только одной кнопки при выводе результата, а то не очень красиво получается
back_to_menu = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2).add(return_button, country_selection)


# ----- Country menu -----
russia_button = KeyboardButton(emoji.emojize(':Russia: Россия'))
armenia_button = KeyboardButton(emoji.emojize(':Armenia: Армения'))
kyrgystan_button = KeyboardButton(emoji.emojize(':Kyrgyzstan: Кыргызстан'))
kazakhstan_button = KeyboardButton(emoji.emojize(':Kazakhstan: Казахстан'))
country_menu = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3).add(russia_button, armenia_button, 
                                                                          kyrgystan_button, kazakhstan_button)