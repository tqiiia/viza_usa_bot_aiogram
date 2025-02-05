from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

kb = ReplyKeyboardMarkup(resize_keyboard=True)
kb.add(KeyboardButton('Записаться в посольтво США'),
       KeyboardButton('Способы оплаты'))

kb_countries = ReplyKeyboardMarkup(resize_keyboard=True,
                                   one_time_keyboard=True)
btn_list = [
    'KYRGYZSTAN, BISHKEK',
    'LUXEMBOURG, LUXEMBOURG',
    'MALTA, VALLETTA, MALTA',
    'MAURITIUS, PORT LOUIS',
    'MONTENEGRO, PODGORICA',
    'MOZAMBIQUE, MAPUTO',
    'TAJIKISTAN, DUSHANBE',
    'TURKMENISTAN, ASHGABAT',
    'UZBEKISTAN, TASHKENT'
]

for btn in btn_list:
    kb_countries.add(btn)

ikb_reg_accept = InlineKeyboardMarkup(row_width=7,
                                      resize_keyboard=True,
                                      one_time_keyboard=True)
ikb_reg_accept.add(InlineKeyboardButton('Подтвердить ✅', callback_data='accept'),
                   InlineKeyboardButton('Заново ввести данные 🔄', callback_data='remove'))
