import logging
from config import TOKEN, channels
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import ParseMode
import logging
from config import TOKEN, channels
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import ParseMode
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils.callback_data import CallbackData
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pymongo import MongoClient

cluster = MongoClient('')

db = cluster['router']
posts = db['router']

logging.basicConfig(level=logging.INFO)
API_TOKEN = TOKEN
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

factory = CallbackData('vote', 'action', 'likes', 'hearts', 'oks', 'dislikes', 'poops', 'url')


def shorten(url):
    r = requests.get(f'https://clck.ru/--?url={url}')
    return r.text.split('/')[-1]


def create_kb(url, likes, hearts, oks, dislikes, poops):
    if '/' in url:
        new_url = shorten(url)
    else:
        new_url = url
    watch_button = InlineKeyboardButton('🎬 Смотреть 🎬', url=f'https://clck.ru/{new_url}')
    like = InlineKeyboardButton(f'👍{likes}',
                                callback_data=factory.new('like', likes, hearts, oks, dislikes, poops, new_url))
    heart = InlineKeyboardButton(f'❤ {hearts}',
                                 callback_data=factory.new('heart', likes, hearts, oks, dislikes, poops, new_url))
    ok = InlineKeyboardButton(f'✋{oks}', callback_data=factory.new('ok', likes, hearts, oks, dislikes, poops, new_url))
    poop = InlineKeyboardButton(f'💩 {dislikes}',
                                callback_data=factory.new('poop', likes, hearts, oks, dislikes, poops, new_url))
    dislike = InlineKeyboardButton(f'👎 {poops}',
                                   callback_data=factory.new('dislike', likes, hearts, oks, dislikes, poops, new_url))
    w_kb = InlineKeyboardMarkup(row_width=5)
    w_kb.insert(like).insert(heart).insert(ok).insert(poop).insert(dislike).add(watch_button)
    return w_kb


@dp.channel_post_handler(chat_id=channels['main'])
async def test(post: types.Message):
    if '#action' in post.text:
        mes = await bot.send_message(channels['action'], f"""{post.text[:-37]}\n<a href='{post.entities[0]['url']}'> </a>""",
                                     parse_mode=ParseMode.HTML,
                                     reply_markup=create_kb(post.entities[-1]['url'], '0', '0', '0', '0', '0'))
        posts.insert_one({'mes_id': mes.message_id, 'chan': mes.chat.id, 'voted': []})
    elif '#comedy' in post.text:
        mes = await bot.send_message(channels['comedy'], f"""{post.text[:-37]}\n<a href='{post.entities[0]['url']}'> </a>""",
                                     parse_mode=ParseMode.HTML,
                                     reply_markup=create_kb(post.entities[-1]['url'], '0', '0', '0', '0', '0'))
        posts.insert_one({'mes_id': mes.message_id, 'chan': mes.chat.id, 'voted': []})
    elif '#drama' in post.text:
        mes = await bot.send_message(channels['drama'], f"""{post.text[:-37]}\n<a href='{post.entities[0]['url']}'> </a>""",
                                     parse_mode=ParseMode.HTML,
                                     reply_markup=create_kb(post.entities[-1]['url'], '0', '0', '0', '0', '0'))
        posts.insert_one({'mes_id': mes.message_id, 'chan': mes.chat.id, 'voted': []})



@dp.callback_query_handler(factory.filter(action='like'))
async def like(call: CallbackQuery, callback_data: dict):
    if call.from_user.id not in posts.find_one({'mes_id': call.message.message_id, 'chan': call.message.chat.id})['voted']:
        mes = await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=create_kb(
            callback_data.get('url'),
            f'{int(callback_data.get("likes")) + 1}',
            callback_data.get('hearts'),
            callback_data.get('oks'),
            callback_data.get('dislikes'),
            callback_data.get('poops')
        ))
        await call.answer('Супер 👍')
        posts.update_one({'mes_id': call.message.message_id, 'chan': call.message.chat.id}, {'$push': {'voted': call.from_user.id}})
    else:
        await call.answer('Вы уже голосовали.')


@dp.callback_query_handler(factory.filter(action='heart'))
async def heart(call: CallbackQuery, callback_data: dict):
    if call.from_user.id not in posts.find_one({'mes_id': call.message.message_id, 'chan': call.message.chat.id})['voted']:
        mes = await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=create_kb(
            callback_data.get('url'),
            callback_data.get('likes'),
            f'{int(callback_data.get("hearts")) + 1}',
            callback_data.get('oks'),
            callback_data.get('dislikes'),
            callback_data.get('poops')
        ))
        await call.answer('Любимый ❤')
        posts.update_one({'mes_id': call.message.message_id, 'chan': call.message.chat.id},
                         {'$push': {'voted': call.from_user.id}})
    else:
        await call.answer('Вы уже голосовали.')


@dp.callback_query_handler(factory.filter(action='ok'))
async def ok(call: CallbackQuery, callback_data: dict):
    if call.from_user.id not in posts.find_one({'mes_id': call.message.message_id, 'chan': call.message.chat.id})['voted']:
        mes = await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=create_kb(
            callback_data.get('url'),
            callback_data.get('likes'),
            callback_data.get('hearts'),
            f'{int(callback_data.get("oks")) + 1}',
            callback_data.get('dislikes'),
            callback_data.get('poops')
        ))
        await call.answer('Нормально ✋')
        posts.update_one({'mes_id': call.message.message_id, 'chan': call.message.chat.id},
                     {'$push': {'voted': call.from_user.id}})
    else:
        await call.answer('Вы уже голосовали.')


@dp.callback_query_handler(factory.filter(action='poop'))
async def poop(call: CallbackQuery, callback_data: dict):
    if call.from_user.id not in posts.find_one({'mes_id': call.message.message_id, 'chan': call.message.chat.id})['voted']:
        mes = await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=create_kb(
            callback_data.get('url'),
            callback_data.get('likes'),
            callback_data.get('hearts'),
            callback_data.get('oks'),
            f'{int(callback_data.get("dislikes")) + 1}',
            callback_data.get('poops')
        ))
        await call.answer('Ужасно 💩')
        posts.update_one({'mes_id': call.message.message_id, 'chan': call.message.chat.id},
                         {'$push': {'voted': call.from_user.id}})
    else:
        await call.answer('Вы уже голосовали.')


@dp.callback_query_handler(factory.filter(action='dislike'))
async def dislike(call: CallbackQuery, callback_data: dict):
    if call.from_user.id not in posts.find_one({'mes_id': call.message.message_id, 'chan': call.message.chat.id})['voted']:
        mes = await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=create_kb(
            callback_data.get('url'),
            callback_data.get('likes'),
            callback_data.get('hearts'),
            callback_data.get('oks'),
            callback_data.get('dislikes'),
            f'{int(callback_data.get("poops")) + 1}',
        ))
        await call.answer('Не особо 👎')
        posts.update_one({'mes_id': call.message.message_id, 'chan': call.message.chat.id},
                     {'$push': {'voted': call.from_user.id}})
    else:
        await call.answer('Вы уже голосовали.')


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
