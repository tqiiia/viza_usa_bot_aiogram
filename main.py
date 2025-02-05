# import os
import re
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import CallbackQuery
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from custom_calendar import SimpleCalendar, calendar_callback
from auth_data import TOKEN_API
from messages import START_MESSAGE, PAY_METHOD
from keyboards import kb, kb_countries, ikb_reg_accept
from parser import third_cabinet_parser
from data_base import db_start, create_profile, edit_profile

bot = Bot(TOKEN_API)
dp = Dispatcher(bot, storage=MemoryStorage())


class reg(StatesGroup):
    country = State()
    second_name = State()
    first_name = State()
    passport_num = State()
    boardcode_num = State()
    phone = State()
    email = State()
    first_date = State()
    second_date = State()


async def on_startup(_):
    await db_start()


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer(START_MESSAGE, reply_markup=kb)
    await create_profile(user_id=message.from_user.id)
    await message.delete()


@dp.message_handler(Text(equals='Записаться в посольтво США'))
async def cmd_reg(message: types.Message):
    await message.answer('Выберите страну/город для записи:',
                         reply_markup=kb_countries)
    await reg.country.set()


@dp.message_handler(state=reg.country)
async def get_country(message: types.Message, state: FSMContext):
    await state.update_data(country=message.text)
    await message.answer('Введите вашу фамилию <b>латинскими буквами</b>',
                         parse_mode='HTML')
    await reg.second_name.set()


@dp.message_handler(state=reg.second_name)
async def get_second_name(message: types.Message, state: FSMContext):
    await state.update_data(second_name=message.text)
    data = await state.get_data()
    if re.search(r'[^А-Яа-я0-9]', str(data.get('second_name'))):
        await message.answer('Введите вашe имя <b>латинскими буквами</b>',
                             parse_mode='HTML')
        await reg.first_name.set()
    else:
        await message.answer('Введите вашу фамилию <b>латинскими буквами</b>',
                             parse_mode='HTML')
        await reg.second_name.set()


@dp.message_handler(state=reg.first_name)
async def get_first_name(message: types.Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    data = await state.get_data()
    if not re.search(r'[А-Яа-я0-9]', str(data.get('first_name'))):
        await message.answer('Введите ваш номер паспорта')
        await reg.passport_num.set()
    else:
        await message.answer('Введите ваше имя <b>латинскими буквами</b>',
                             parse_mode='HTML')
        await reg.first_name.set()


@dp.message_handler(state=reg.passport_num)
async def get_passport_num(message: types.Message, state: FSMContext):
    await state.update_data(passport_num=message.text)
    await message.answer('Введите ваш confirmation id')
    await reg.boardcode_num.set()


@dp.message_handler(state=reg.boardcode_num)
async def get_boardcode_num(message: types.Message, state: FSMContext):
    await state.update_data(boardcode_num=message.text)
    await message.answer('Введите ваш номер телефона <b>без + и ( )</b>',
                         parse_mode='HTML')
    await reg.phone.set()


@dp.message_handler(state=reg.phone)
async def get_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    data = await state.get_data()
    if not re.search(r'[+()a-zA-Zа-яА-ЯёЁ]', str(data.get('phone'))):
        await message.answer('Введите вашу электронную почту')
        await reg.email.set()
    else:
        await message.answer('Введите ваш номер телефона <b>без + и ( )</b>',
                             parse_mode='HTML')
        await reg.phone.set()


@dp.message_handler(state=reg.email)
async def get_email(message: types.Message, state: FSMContext):
    await state.update_data(email=message.text)
    data = await state.get_data()
    if re.search(r'@', str(data.get('email'))):
        await message.answer('Выберите дату начала записи',
                             reply_markup=await SimpleCalendar().start_calendar())
        await reg.first_date.set()
    else:
        await message.answer('Введите вашу <u>корректную</u> электронную почту',
                             parse_mode='HTML')
        await reg.email.set()


# noinspection PyTypeChecker,PyArgumentList
@dp.callback_query_handler(calendar_callback.filter(), state=reg.first_date)
async def process_simple_calendar(callback_query: CallbackQuery, callback_data: dict,
                                  state=FSMContext):
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    if selected:
        await callback_query.message.delete()
        await callback_query.message.answer(
            f'Вы выбрали дату начала записи: {date.strftime("%d.%m.%Y")}'
        )
        await state.update_data(first_date=date.strftime("%d.%m.%Y"))
        await callback_query.message.answer('Выберите дату конца записи',
                                            reply_markup=await SimpleCalendar().start_calendar())
        await reg.second_date.set()


# noinspection PyArgumentList,PyTypeChecker
@dp.callback_query_handler(calendar_callback.filter(), state=reg.second_date)
async def process_simple_calendar(callback_query: CallbackQuery, callback_data: dict,
                                  state=FSMContext):
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    if selected:
        await state.update_data(second_date=date.strftime("%d.%m.%Y"))
        data = await state.get_data()
        if ((int(str(data.get('first_date')).split('.')[0]) > int(str(data.get('second_date')).split('.')[0])) and
                (int(str(data.get('first_date')).split('.')[1]) >= int(str(data.get('second_date')).split('.')[1])) and
                (int(str(data.get('first_date')).split('.')[2]) >= int(str(data.get('second_date')).split('.')[2]))):
            await callback_query.message.delete()
            await callback_query.message.answer('Вы выбрали некорректную дату конца записи.\n'
                                                '<b>Дата конца записи должна быть <u>позже/в день</u>'
                                                ' с датой начала записи</b>',
                                                parse_mode='HTML',
                                                reply_markup=await SimpleCalendar().start_calendar())
            await reg.second_date.set()
        else:
            await callback_query.message.delete()
            await callback_query.message.answer(f'Вы выбрали дату конца записи: {date.strftime("%d.%m.%Y")}')
            await state.update_data(second_date=date.strftime("%d.%m.%Y"))
            data = await state.get_data()
            await callback_query.message.answer('Проверьте введёные данные:')
            await callback_query.message.answer(f"1. Страна: {str(data.get('country')).split(',')[0]}\n"
                                                f"2. Город: {str(data.get('country')).split(', ', maxsplit=1)[1]}\n"
                                                f"3. Имя: {data.get('first_name')}\n"
                                                f"4. Фамилия: {data.get('second_name')}\n"
                                                f"5. Номер пасспорта: {data.get('passport_num')}\n"
                                                f"6. Номер boardcode: {data.get('boardcode_num')}\n"
                                                f"7. Номер телефона: {data.get('phone')}\n"
                                                f"8. Эл. почта: {data.get('email')}\n"
                                                f"9. Интервал поиска дат: {data.get('first_date')} "
                                                f"- {data.get('second_date')}\n",
                                                reply_markup=ikb_reg_accept)
            await state.reset_state(with_data=False)


# noinspection PyArgumentList
@dp.callback_query_handler(lambda c: c.data == 'accept')
async def accept(callback_query: CallbackQuery, state=FSMContext):
    await edit_profile(state, user_id=callback_query.from_user.id)
    await bot.edit_message_reply_markup(chat_id=callback_query.from_user.id,
                                        message_id=callback_query.message.message_id,
                                        reply_markup=None)
    await bot.answer_callback_query(callback_query.id)
    data = await state.get_data()
    await state.finish()
    print("1")
    await bot.send_message(callback_query.from_user.id, text=f"{await third_cabinet_parser(data.get('country'), data.get('first_name'), data.get('second_name'), data.get('passport_num'), data.get('boardcode_num'), data.get('phone'), data.get('email'), data.get('first_date'), data.get('second_date'))}",
                           reply_markup=kb)
    # with open('End.png', 'rb') as photo:
    #     await bot.send_photo(callback_query.from_user.id, photo=photo)
    #     os.remove('End.png')


@dp.callback_query_handler(lambda c: c.data == 'remove')
async def remove(callback_query: CallbackQuery):
    await bot.edit_message_reply_markup(chat_id=callback_query.from_user.id,
                                        message_id=callback_query.message.message_id,
                                        reply_markup=None)
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Введите данные заново',
                           reply_markup=kb)


@dp.message_handler(Text(equals='Способы оплаты'))
async def pay_method(message: types.Message):
    await message.answer(PAY_METHOD)


@dp.message_handler()  # Обработчик неверных команд
async def parser(message: types.Message):
    await message.answer('Нет такой команды')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True,
                           on_startup=on_startup)
