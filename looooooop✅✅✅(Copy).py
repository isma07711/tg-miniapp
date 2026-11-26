# -*- coding: utf-8 -*-
# ============================================================
# ISMABOOST BOT ULTRA — bot.py
# Python 3.10+ | aiogram 3.4.1 | aiocryptopay | aiohttp
# ============================================================

import logging
import sqlite3
import asyncio
import io
import csv
import os
from datetime import datetime, timedelta
from collections import defaultdict
import time as _time
import random
import json
import string
import aiohttp
import re  # <--- ДОБАВЬ ЭТО
import math
from aiogram.fsm.state import State, StatesGroup

from aiogram import Bot, Dispatcher, F, BaseMiddleware, types
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton,
    CallbackQuery, Message,
    BufferedInputFile,
    TelegramObject,
    WebAppInfo,
    ReplyKeyboardRemove
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from aiocryptopay import AioCryptoPay, Networks

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.FileHandler("bot.log", encoding="utf-8"), logging.StreamHandler()]
)

# ============ НАСТРОЙКИ ПАНЕЛЕЙ ============
PANELS = {
    "panel_1": {"url": "https://vingboost.com/api/v2", "key": "RysONJYWf4rRIGMPRWERSe6zy5IYF5yO3zrEZEvZnuNdfvAxpZxVQyoqJhxe"},
    "panel_2": {"url": "https://kuzya-boost.ru/api/v2", "key": "1bdc2423200ab02a6a9e0020fe64033e"},
    "panel_3": {"url": "https://twiboost.com/api/v2",   "key": "0fUruTwwxH3JZ0YZfcpdt63V2psQ5WUfZD7fjn22TJrsqM1h9BonrFVyvkjn"},
    "panel_4": {"url": "https://vexboost.ru/api/v2",    "key": "819tLjVvVcTaVXJ8bhYJlRtXFRTW4tVDBtHraf9evli6XQcXWKFIEgs5LugE"},
}
DEFAULT_PANEL = "panel_1"

# ============ ОСНОВНЫЕ НАСТРОЙКИ ============
BOT_TOKEN = "8914847110:AAGRvfI6buuK8YbGwmfiMVHv3VcPc5POJ9U"
WEBAPP_URL = "https://isma0771.github.io/tg-miniapp/?v=14"
ADMIN_ID = 7414904006
SUPPORT_USERNAME = "ismaboy014"
CHANNEL_USERNAME = "ismaBoost"
CHANNEL_URL = "https://t.me/ismaBoost"
TIKTOK_USERNAME = "ismaaaa983"
SBP_PHONE = "89285937212"
# ============ НАСТРОЙКИ ДЛЯ ДИНАМИЧЕСКОГО КАТАЛОГА ============
VEX_PROVIDER_URL = "https://vexboost.ru/api/v2"
VEX_API_KEY = "819tLjVvVcTaVXJ8bhYJlRtXFRTW4tVDBtHraf9evli6XQcXWKFIEgs5LugE"
VEX_MARGIN = 35  # Наценка 35%
VEX_CACHE = []
DB_PATH = "ismaboost.db"

CRYPTO_PAY_TOKEN = "664704:AAzeBrWpvwx0Jau7RMRtM95o0XWwCLTZ3wM"
CRYPTO_PAY_NETWORK = "mainnet"
USDT_TO_RUB = 90

PANEL_CHECK_INTERVAL = 300
REF_BONUS_PERCENT = 5
MAX_ORDERS_PER_HOUR = 25
MAX_ORDERS_PER_DAY = 250
MAX_SUM_PER_HOUR = 30000
BACKUP_INTERVAL = 86400
LOG_CHANNEL_ID = -1004423117782

DISCOUNT_THRESHOLD = 5000
DISCOUNT_PERCENT = 7
LOW_BALANCE_THRESHOLD = 25
TOP_SERVICES_COUNT = 5
REF_STATS_LIMIT = 20
WEEKEND_DISCOUNT = 3
FIRST_ORDER_DISCOUNT = 10

FLOOD_MSG_LIMIT = 5
FLOOD_MSG_WINDOW = 3
FLOOD_CB_LIMIT = 20
FLOOD_CB_WINDOW = 10
FLOOD_BAN_TIME = 15
# ============ НАСТРОЙКИ ПЛАВНОЙ НАКРУТКИ ============
SMOOTH_MIN_DAYS = 1
SMOOTH_MAX_DAYS = 60
SMOOTH_DEFAULT_INTERVAL = 60  # минуты по умолчанию

# Услуги, которые НЕЛЬЗЯ растянуть (звёзды, жалобы, запуски, приват)
SMOOTH_DISABLED_KEYS = {
    "tg_stars", "tg_report_menu",
    "sniper_tg_report", "sniper_tg_neg",
    "tg_bot_start", "mx_bot_start",
    "priv_tg_subs", "priv_tt_views",
}

def can_be_smooth(plat, key):
    if plat in ("privat", "snipers"):
        return False
    if key in SMOOTH_DISABLED_KEYS:
        return False
    return True

# ============ НАСТРОЙКИ ПЛАВНОЙ НАКРУТКИ ============
SMOOTH_MIN_DAYS = 1
SMOOTH_MAX_DAYS = 60

SMOOTH_DISABLED_KEYS = {
    "tg_stars", "tg_report_menu",
    "sniper_tg_report", "sniper_tg_neg",
    "tg_bot_start", "mx_bot_start",
    "priv_tg_subs", "priv_tt_views",
}

def can_be_smooth(plat, key):
    if plat in ("privat", "snipers"):
        return False
    if key in SMOOTH_DISABLED_KEYS:
        return False
    return True

# ============================================================
# ПОЛНЫЙ КАТАЛОГ VEXBOOST (ИЗ API DUMP) — с наценкой 35%
# Telegram ≥ 10₽, Instagram 2411 = 14₽
# ============================================================

def _p(raw: float) -> float:
    """Наценка 35%, округление до 2 знаков"""
    return round(float(raw) * 1.35, 2)

SERVICES = {
    # ============================================================
    # TIKTOK
    #
    "tiktok": {
        "1447": {"name": "TikTok Репосты [Хорошая скорость]", "price": _p(11.4574), "panel": "panel_4", "desc": "TikTok Сохранения / Репосты"},
        "1479": {"name": "TikTok Сохранения видео [365 Дней гарантии]", "price": _p(2.9654), "panel": "panel_4", "desc": "TikTok Сохранения / Репосты"},
        "1896": {"name": "TikTok Подписчики [Живые][Россия+СНГ][Вечная Гарантия♻️]", "price": _p(1007.5), "panel": "panel_4", "desc": "TikTok Подписчики [Живые]"},
        "2144": {"name": "TikTok Баттл поинты [PK Battle Points] [Лучшая цена]", "price": _p(37.9871), "panel": "panel_4", "desc": "TikTok Баттл поинты"},
        "2444": {"name": "TikTok Реальные подписчики [США] [Быстрые] [Гарантия 15]", "price": _p(385.5896), "panel": "panel_4", "desc": "TikTok Подписчики"},
        "2469": {"name": "TikTok Лайки [Гарантия 30 дней♻️][Списания до 20%]", "price": _p(130.7083), "panel": "panel_4", "desc": "TikTok Лайки"},
        "2472": {"name": "TikTok Подписчики [Живой трафик СНГ+МИКС]", "price": _p(1314.4), "panel": "panel_4", "desc": "TikTok Подписчики [Живые]"},
        "2544": {"name": "TikTok Просмотры [Минимум списаний] [Без гарантии]", "price": _p(7.4136), "panel": "panel_4", "desc": "TikTok Просмотры"},
        "2545": {"name": "🔥TikTok Просмотры [Гарантия 30 Дней♻️]", "price": _p(3.5046), "panel": "panel_4", "desc": "TikTok Просмотры"},
        "2710": {"name": "TikTok Зрители [30 Минут][200% Лайков+20% ИИ]", "price": _p(225.4719), "panel": "panel_4", "desc": "TikTok Прямая трансляция"},
        "2711": {"name": "TikTok Зрители [60 Минут][200% Лайков+20% ИИ]", "price": _p(450.9438), "panel": "panel_4", "desc": "TikTok Прямая трансляция"},
        "2712": {"name": "TikTok Зрители [90 Минут][200% Лайков+20% ИИ]", "price": _p(676.4157), "panel": "panel_4", "desc": "TikTok Прямая трансляция"},
        "2713": {"name": "TikTok Зрители [120 Минут][200% Лайков+20% ИИ]", "price": _p(901.8876), "panel": "panel_4", "desc": "TikTok Прямая трансляция"},
        "2714": {"name": "TikTok Зрители [150 Минут][200% Лайков+20% ИИ]", "price": _p(1127.3594), "panel": "panel_4", "desc": "TikTok Прямая трансляция"},
        "2715": {"name": "TikTok Зрители [180 Минут][200% Лайков+20% ИИ]", "price": _p(1352.8313), "panel": "panel_4", "desc": "TikTok Прямая трансляция"},
        "2716": {"name": "TikTok Зрители [210 Минут][200% Лайков+20% ИИ]", "price": _p(1578.3032), "panel": "panel_4", "desc": "TikTok Прямая трансляция"},
        "2717": {"name": "TikTok Зрители [240 Минут][200% Лайков+20% ИИ]", "price": _p(1803.7751), "panel": "panel_4", "desc": "TikTok Прямая трансляция"},
        "2718": {"name": "TikTok Зрители [15 Минут][200% Лайков+20% ИИ]", "price": _p(225.4719), "panel": "panel_4", "desc": "TikTok Прямая трансляция"},
        "2749": {"name": "TikTok Подписчики [Небольшие списания] [Без гарантии]", "price": _p(134.793), "panel": "panel_4", "desc": "TikTok Подписчики"},
        "2891": {"name": "🔥TikTok Реальные подписчики [Минимум списаний] [30 Дней гарантии]", "price": _p(262.8463), "panel": "panel_4", "desc": "TikTok Подписчики"},
        "2904": {"name": "TikTok Лайки [Без гарантии] [Быстрые]", "price": _p(58.8188), "panel": "panel_4", "desc": "TikTok Лайки"},
        "2905": {"name": "🇷🇺 TikTok Лайки [10k/День] [Россия]", "price": _p(60.7549), "panel": "panel_4", "desc": "TikTok Лайки"},
        "2906": {"name": "TikTok Лайки [Бразилия]", "price": _p(72.7882), "panel": "panel_4", "desc": "TikTok Лайки [Таргетинг]"},
        "2907": {"name": "TikTok Лайки [Турция]", "price": _p(330.8555), "panel": "panel_4", "desc": "TikTok Лайки [Таргетинг]"},
        "2908": {"name": "TikTok Лайки [Английские аккаунты] [Средняя скорость]", "price": _p(92.6395), "panel": "panel_4", "desc": "TikTok Лайки [Таргетинг]"},
        "2909": {"name": "TikTok Лайки [Английские аккаунты] [Быстрые]", "price": _p(166.7512), "panel": "panel_4", "desc": "TikTok Лайки [Таргетинг]"},
        "2910": {"name": "TikTok Лайки [Индонезия]", "price": _p(86.0224), "panel": "panel_4", "desc": "TikTok Лайки [Таргетинг]"},
        "2911": {"name": "TikTok Лайки [Арабы]", "price": _p(132.3422), "panel": "panel_4", "desc": "TikTok Лайки [Таргетинг]"},
        "2915": {"name": "TikTok Просмотры [Без списаний]", "price": _p(7.4136), "panel": "panel_4", "desc": "TikTok Просмотры"},
        "2947": {"name": "TikTok Зрители [15 Минут]", "price": _p(265.9098), "panel": "panel_4", "desc": "TikTok Прямая трансляция"},
        "2948": {"name": "TikTok Зрители [30 Минут]", "price": _p(529.2871), "panel": "panel_4", "desc": "TikTok Прямая трансляция"},
        "2949": {"name": "TikTok Зрители [60 Минут]", "price": _p(1215.5876), "panel": "panel_4", "desc": "TikTok Прямая трансляция"},
        "2950": {"name": "TikTok Зрители [90 Минут]", "price": _p(1586.595), "panel": "panel_4", "desc": "TikTok Прямая трансляция"},
        "2951": {"name": "TikTok Зрители [120 Минут]", "price": _p(2114.6159), "panel": "panel_4", "desc": "TikTok Прямая трансляция"},
        "2952": {"name": "TikTok Зрители [180 Минут]", "price": _p(3330.2034), "panel": "panel_4", "desc": "TikTok Прямая трансляция"},
        "2953": {"name": "TikTok Зрители [240 Минут]", "price": _p(4229.2318), "panel": "panel_4", "desc": "TikTok Прямая трансляция"},
        "2954": {"name": "TikTok Зрители [300 Минут]", "price": _p(14993.0653), "panel": "panel_4", "desc": "TikTok Прямая трансляция"},
        "2955": {"name": "TikTok Зрители [360 Минут]", "price": _p(17991.6784), "panel": "panel_4", "desc": "TikTok Прямая трансляция"},
        "2974": {"name": "TikTok Просмотры [Авто-Восстановление 30 Дней♻️]", "price": _p(7.8425), "panel": "panel_4", "desc": "TikTok Просмотры"},
        "2998": {"name": "TikTok Подписчики [Медленные] [30 Дней гарантии♻️]", "price": _p(188.6693), "panel": "panel_4", "desc": "TikTok Подписчики"},
        "3054": {"name": "TikTok Просмотры [Для монетизации] [Без списаний] [Гарантия 30]", "price": _p(12.1314), "panel": "panel_4", "desc": "TikTok Просмотры"},
        "3056": {"name": "TikTok Просмотры [На последние 5 видео]", "price": _p(10.1095), "panel": "panel_4", "desc": "TikTok Просмотры [На последние видео]"},
        "3057": {"name": "TikTok Просмотры [На последние 10 видео]", "price": _p(10.1095), "panel": "panel_4", "desc": "TikTok Просмотры [На последние видео]"},
        "3058": {"name": "TikTok Просмотры [На последние 15 видео]", "price": _p(10.1095), "panel": "panel_4", "desc": "TikTok Просмотры [На последние видео]"},
        "3102": {"name": "TikTok Подписчики [Приоритетные] [30 Дней гарантии♻️]", "price": _p(302.6307), "panel": "panel_4", "desc": "TikTok Подписчики"},
        "3117": {"name": "TikTok Лайки [Гарантия 15 дней♻️][Списания до 50%]", "price": _p(69.8473), "panel": "panel_4", "desc": "TikTok Лайки"},
        "3118": {"name": "TikTok Лайки [Без списаний] [Гарантия 30 дней♻️]", "price": _p(261.4167), "panel": "panel_4", "desc": "TikTok Лайки"},
        "3129": {"name": "🔥TikTok Просмотры [Без гарантии] [Быстрые]", "price": _p(0.947), "panel": "panel_4", "desc": "TikTok Просмотры"},
        "3130": {"name": "TikTok Подписчики [Медленные] [Без гарантии]", "price": _p(118.7404), "panel": "panel_4", "desc": "TikTok Подписчики"},
        "3132": {"name": "TikTok Лайки [Медленные] [Высокое качество + Реальные]", "price": _p(156.85), "panel": "panel_4", "desc": "TikTok Лайки"},
        "3182": {"name": "🇷🇺 TikTok Лайки [Живые] [Россия]", "price": _p(544.05), "panel": "panel_4", "desc": "TikTok Лайки"},
        "3226": {"name": "TikTok Комментарии [Случайные][Россия]", "price": _p(840.0), "panel": "panel_4", "desc": "TikTok Комментарии"},
        "3227": {"name": "TikTok Комментарии [Случайные+Смайлики][Россия]", "price": _p(624.0), "panel": "panel_4", "desc": "TikTok Комментарии"},
        "3228": {"name": "TikTok Комментарии [Случайные][Россия+Микс]", "price": _p(696.0), "panel": "panel_4", "desc": "TikTok Комментарии"},
        "3229": {"name": "TikTok Комментарии [Свои][Россия]", "price": _p(912.0), "panel": "panel_4", "desc": "TikTok Комментарии"},
        "3230": {"name": "TikTok Комментарии [Свои][Микс]", "price": _p(294.0938), "panel": "panel_4", "desc": "TikTok Комментарии"},
        "3231": {"name": "TikTok Лайки на комментарии [Быстрые]", "price": _p(18.2992), "panel": "panel_4", "desc": "TikTok Комментарии / Лайки на комментарии"},
        "3233": {"name": "🔥TikTok Просмотры [Без гарантии] [Медленные]", "price": _p(0.4941), "panel": "panel_4", "desc": "TikTok Просмотры"},
        "3283": {"name": "🔥TikTok Просмотры [Гарантия 30 Дней♻️][Крупные заказы]", "price": _p(7.4136), "panel": "panel_4", "desc": "TikTok Просмотры"},
    },
    # ============================================================
    # TELEGRAM (MIN 10₽/1к)
    # ============================================================
    "telegram": {
        "1235": {"name": "🌟 Telegram Микс позитивных реакций 👍❤️🔥🥰👏😁🎉🤩[Premium]", "price": max(_p(12.4549), 10.0), "panel": "panel_4", "desc": "Telegram Premium Реакции"},
        "1236": {"name": "🌟 Telegram Микс негативных реакций 👎😁😢💩🤮🤔🤯🤬[Premium]", "price": max(_p(12.4549), 10.0), "panel": "panel_4", "desc": "Telegram Premium Реакции"},
        "1238": {"name": "ID1238 🌟🤖Telegram Запуск бота Premium [База 100к]", "price": max(_p(517.8207), 10.0), "panel": "panel_4", "desc": "Telegram Premium Старты бота"},
        "1240": {"name": "🌟Telegram Просмотры историй l Premium l Для поисковой оптимизации", "price": max(_p(27.6775), 10.0), "panel": "panel_4", "desc": "Telegram Premium Просмотры"},
        "1258": {"name": "Telegram Premium RU Подписчики 180 дней [Присоединяются из поиска]", "price": max(_p(3202.3543), 10.0), "panel": "panel_4", "desc": "Telegram Premium Подписчики [Россия]"},
        "1492": {"name": "🔥Telegram Подписчики [60 Дней без списаний♻️] [Сервер: 1]", "price": max(_p(35.5363), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики"},
        "1507": {"name": "Telegram Рефералы для ботов (только запуск)🌟", "price": max(_p(1500.0), 10.0), "panel": "panel_4", "desc": "Telegram Рефералы"},
        "1518": {"name": "Telegram Подписчики [Гарантия 360♻️] [Переполнение]", "price": max(_p(47.055), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики"},
        "1603": {"name": "Telegram Просмотры RU [SEO] 🌟", "price": max(_p(92.5), 10.0), "panel": "panel_4", "desc": "Telegram Просмотры"},
        "1642": {"name": "🇷🇺 Просмотры [для вывода в топ, 1-20 постов]", "price": max(_p(107.8), 10.0), "panel": "panel_4", "desc": "Telegram Просмотры [Россия]"},
        "1643": {"name": "🇷🇺 Просмотры [1-20 постов]", "price": max(_p(61.6), 10.0), "panel": "panel_4", "desc": "Telegram Просмотры [Россия]"},
        "1644": {"name": "🇷🇺 Просмотры [Последних 5 постов]", "price": max(_p(12.5807), 10.0), "panel": "panel_4", "desc": "Telegram Просмотры [Россия]"},
        "1645": {"name": "🇷🇺 Просмотры [Последних 10 постов]", "price": max(_p(25.1614), 10.0), "panel": "panel_4", "desc": "Telegram Просмотры [Россия]"},
        "1646": {"name": "🇷🇺 Просмотры [Последних 20 постов]", "price": max(_p(50.3227), 10.0), "panel": "panel_4", "desc": "Telegram Просмотры [Россия]"},
        "1647": {"name": "🇷🇺 Просмотры [Последних 50 постов]", "price": max(_p(125.8068), 10.0), "panel": "panel_4", "desc": "Telegram Просмотры [Россия]"},
        "1648": {"name": "🇷🇺 Просмотры [Последних 100 постов]", "price": max(_p(251.6136), 10.0), "panel": "panel_4", "desc": "Telegram Просмотры [Россия]"},
        "1649": {"name": "🇷🇺 Просмотры [Последних 200 постов]", "price": max(_p(503.2271), 10.0), "panel": "panel_4", "desc": "Telegram Просмотры [Россия]"},
        "1690": {"name": "Рефералы для Ботов [Список поддерживаемых ботов] #1", "price": max(_p(3750.0), 10.0), "panel": "panel_4", "desc": "Telegram Рефералы"},
        "1753": {"name": "Запуск бота [Принимает реферальный код] [Быстрый старт]", "price": max(_p(13.0), 10.0), "panel": "panel_4", "desc": "Telegram Старты бота"},
        "1760": {"name": "🔥Telegram Подписчики без списаний [Лучшая цена] [Сервер: 1]", "price": max(_p(36.1), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики"},
        "1790": {"name": "Telegram Premium RU Подписчики + Просмотры [Присоединяются из поиска]", "price": max(_p(1568.5001), 10.0), "panel": "panel_4", "desc": "Telegram Premium Подписчики [Россия]"},
        "1791": {"name": "Telegram Premium RU Подписчики + Просмотры [Присоединяются по URL]", "price": max(_p(1176.3751), 10.0), "panel": "panel_4", "desc": "Telegram Premium Подписчики [Россия]"},
        "1815": {"name": "🔥🇷🇺 Запуск бота [Принимает реферальный код][Россия][Сервер: 1]", "price": max(_p(4.5885), 10.0), "panel": "panel_4", "desc": "Telegram Старты бота [Таргетинг]"},
        "1824": {"name": "🇨🇳 Telegram Подписчики Без списаний [Китай] [80к/День]", "price": max(_p(86.8067), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики (Таргетинг)"},
        "1828": {"name": "Telegram Авто - Просмотры [Подписка] [От 10]", "price": max(_p(0.3104), 10.0), "panel": "panel_4", "desc": "Telegram Авто-Просмотры"},
        "1835": {"name": "Telegram Подписчики [Гарантия - 30 дней][Лучшая услуга!]♻️🚀 🇷🇺", "price": max(_p(91.4958), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики [Россия]"},
        "1893": {"name": "Telegram Запуск бота Россия [Premium Аккаунты] [Лучшая услуга]", "price": max(_p(658.4433), 10.0), "panel": "panel_4", "desc": "Telegram Premium Старты бота [Россия]"},
        "1904": {"name": "Telegram Просмотры Историй", "price": max(_p(1.2662), 10.0), "panel": "panel_4", "desc": "Telegram Истории"},
        "1905": {"name": "Telegram Лайки на Истории", "price": max(_p(113.9613), 10.0), "panel": "panel_4", "desc": "Telegram Истории"},
        "1906": {"name": "Telegram Репост Историй", "price": max(_p(633.1185), 10.0), "panel": "panel_4", "desc": "Telegram Истории"},
        "1987": {"name": "Telegram Подписчики [Без гарантии] [Быстрые] [Крупные списания⛔️]", "price": max(_p(3.2), 10.0), "panel": "panel_4", "desc": "Private API"},
        "1989": {"name": "Telegram Буст канала [7 Дней] [Гарантия]⚡️", "price": max(_p(3859.9807), 10.0), "panel": "panel_4", "desc": "Telegram Бусты"},
        "2001": {"name": "Telegram Premium Участники [3 Дня] [0% Дроп]", "price": max(_p(147.7086), 10.0), "panel": "panel_4", "desc": "Telegram Premium Подписчики"},
        "2003": {"name": "Telegram микс позитивных реакций [👍 ❤️ 🔥 🎉]", "price": max(_p(1.2336), 10.0), "panel": "panel_4", "desc": "Telegram Реакции"},
        "2004": {"name": "Telegram микс негативных реакций [👎 😁 😢 💩]", "price": max(_p(1.2336), 10.0), "panel": "panel_4", "desc": "Telegram Реакции"},
        "2061": {"name": "Telegram Голоса в опрос [Лучшая цена на рынке!]", "price": max(_p(6.2495), 10.0), "panel": "panel_4", "desc": "Telegram Голоса в опросе"},
        "2062": {"name": "Telegram Реакция на Историю [❤️]", "price": max(_p(1.2662), 10.0), "panel": "panel_4", "desc": "Telegram Истории"},
        "2066": {"name": "🇺🇿 Telegram Premium Участники [Узбекистан] [Из поиска]", "price": max(_p(1519.4845), 10.0), "panel": "panel_4", "desc": "Telegram Premium Подписчики [Таргетинг]"},
        "2067": {"name": "🇺🇿 Telegram Premium Участники [Узбекистан] [По ссылке]", "price": max(_p(1253.5747), 10.0), "panel": "panel_4", "desc": "Telegram Premium Подписчики [Таргетинг]"},
        "2068": {"name": "🇺🇸 Telegram Premium Участники [США] [Из поиска]", "price": max(_p(1519.4845), 10.0), "panel": "panel_4", "desc": "Telegram Premium Подписчики [Таргетинг]"},
        "2069": {"name": "🇺🇸 Telegram Premium Участники [США] [По ссылке]", "price": max(_p(1139.6133), 10.0), "panel": "panel_4", "desc": "Telegram Premium Подписчики [Таргетинг]"},
        "2072": {"name": "🇹🇷 Telegram Premium Участники [Турция] [Просмотры + из поиска]", "price": max(_p(1519.4845), 10.0), "panel": "panel_4", "desc": "Telegram Premium Подписчики [Таргетинг]"},
        "2073": {"name": "🇹🇷 Telegram Premium Участники [Турция] из поиска", "price": max(_p(759.7422), 10.0), "panel": "panel_4", "desc": "Telegram Premium Подписчики [Таргетинг]"},
        "2074": {"name": "🇹🇷 Telegram Premium Участники [Турция]", "price": max(_p(1519.4845), 10.0), "panel": "panel_4", "desc": "Telegram Premium Подписчики [Таргетинг]"},
        "2075": {"name": "🇮🇹 Telegram Premium Участники [Италия] из поиска", "price": max(_p(759.7422), 10.0), "panel": "panel_4", "desc": "Telegram Premium Подписчики [Таргетинг]"},
        "2076": {"name": "🇮🇹 Telegram Premium Участники [Италия]", "price": max(_p(1519.4845), 10.0), "panel": "panel_4", "desc": "Telegram Premium Подписчики [Таргетинг]"},
        "2077": {"name": "🇨🇳 Telegram Premium Участники [Китай] [Просмотры + из поиска]", "price": max(_p(1519.4845), 10.0), "panel": "panel_4", "desc": "Telegram Premium Подписчики [Таргетинг]"},
        "2078": {"name": "🇨🇳 Telegram Premium Участники [Китай] из поиска", "price": max(_p(759.7422), 10.0), "panel": "panel_4", "desc": "Telegram Premium Подписчики [Таргетинг]"},
        "2079": {"name": "🇨🇳 Telegram Premium Участники [Китай] + Просмотры", "price": max(_p(1139.6133), 10.0), "panel": "panel_4", "desc": "Telegram Premium Подписчики [Таргетинг]"},
        "2082": {"name": "Telegram Буст канала [30 Дней] [Для частных каналов] 🔒", "price": max(_p(17645.626), 10.0), "panel": "panel_4", "desc": "Telegram Бусты"},
        "2083": {"name": "Telegram Буст канала [14 Дней] [Для частных каналов] 🔒", "price": max(_p(8822.813), 10.0), "panel": "panel_4", "desc": "Telegram Бусты"},
        "2084": {"name": "Telegram Буст канала [1 День] [Для частных каналов] 🔒", "price": max(_p(2095.4181), 10.0), "panel": "panel_4", "desc": "Telegram Бусты"},
        "2085": {"name": "Telegram Буст канала [7 Дней] [Для частных каналов] 🔒", "price": max(_p(4411.4065), 10.0), "panel": "panel_4", "desc": "Telegram Бусты"},
        "2087": {"name": "🌟🤖Telegram Запуск бота Premium Аккаунты [30 дней] [/start]", "price": max(_p(366.3918), 10.0), "panel": "panel_4", "desc": "Telegram Premium Старты бота"},
        "2088": {"name": "Telegram Запуск бота Россия [Premium Аккаунты] [Активные]", "price": max(_p(1519.4845), 10.0), "panel": "panel_4", "desc": "Telegram Premium Старты бота [Россия]"},
        "2104": {"name": "Telegram Подписчики [90 Дней без списаний♻️]", "price": max(_p(87.3704), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики"},
        "2107": {"name": "Telegram Звезды на профиль", "price": max(_p(1813.0881), 10.0), "panel": "panel_4", "desc": "Telegram Звезды"},
        "2125": {"name": "Telegram Повторные нажатия /start для Ботов", "price": max(_p(186.0), 10.0), "panel": "panel_4", "desc": "Telegram Рефералы"},
        "2127": {"name": "Telegram Просмотры [Для закрытых каналов]", "price": max(_p(2.5325), 10.0), "panel": "panel_4", "desc": "Telegram Просмотры [Для закрытых каналов]"},
        "2129": {"name": "Telegram Нейросетевые Авто-просмотры на 10 постов", "price": max(_p(533.975), 10.0), "panel": "panel_4", "desc": "Telegram Авто-Просмотры для Tgstat"},
        "2130": {"name": "Telegram Нейросетевые Авто-просмотры на 25 постов", "price": max(_p(1334.9375), 10.0), "panel": "panel_4", "desc": "Telegram Авто-Просмотры для Tgstat"},
        "2131": {"name": "Telegram Нейросетевые Авто-просмотры на 50 постов", "price": max(_p(2464.5), 10.0), "panel": "panel_4", "desc": "Telegram Авто-Просмотры для Tgstat"},
        "2139": {"name": "Telegram Умные Просмотры лесенкой [Сервер 1]", "price": max(_p(13.3), 10.0), "panel": "panel_4", "desc": "Telegram Умные Просмотры"},
        "2140": {"name": "Telegram Умные Просмотры лесенкой [Сервер 2]", "price": max(_p(6.65), 10.0), "panel": "panel_4", "desc": "Telegram Умные Просмотры"},
        "2141": {"name": "Telegram Умные Просмотры лесенкой [Сервер 4]", "price": max(_p(13.3), 10.0), "panel": "panel_4", "desc": "Telegram Умные Просмотры"},
        "2142": {"name": "Telegram Умные Просмотры лесенкой [Сервер 3]", "price": max(_p(13.3), 10.0), "panel": "panel_4", "desc": "Telegram Умные Просмотры"},
        "2147": {"name": "🇺🇿 Telegram Подписчики [Узбекистан] [Любые ссылки]", "price": max(_p(74.708), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики (Таргетинг)"},
        "2151": {"name": "🇺🇸 Telegram Подписчики [США] [Гарантия 30 дней]", "price": max(_p(75.9742), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики (Таргетинг)"},
        "2152": {"name": "🇲🇲 Telegram Подписчики [Мьянма] [Гарантия 30 дней]", "price": max(_p(75.9742), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики (Таргетинг)"},
        "2153": {"name": "Telegram Premium Старты бота [Россия] [6 месяцев]", "price": max(_p(1266.2371), 10.0), "panel": "panel_4", "desc": "Telegram Premium Старты бота [Россия]"},
        "2186": {"name": "🇷🇺 Telegram Комментарии [Случайные][Россия]", "price": max(_p(251.9812), 10.0), "panel": "panel_4", "desc": "Telegram Комментарии"},
        "2187": {"name": "🇨🇳 Telegram Комментарии [Случайные][Китай]", "price": max(_p(251.9812), 10.0), "panel": "panel_4", "desc": "Telegram Комментарии"},
        "2188": {"name": "🇩🇪 Telegram Комментарии [Случайные][Германия]", "price": max(_p(189.9356), 10.0), "panel": "panel_4", "desc": "Telegram Комментарии"},
        "2202": {"name": "Telegram Premium RU Подписчики [30 Дней] [Быстрые]", "price": max(_p(1442.3009), 10.0), "panel": "panel_4", "desc": "Telegram Premium Подписчики [Россия]"},
        "2207": {"name": "🇸🇦 Запуск бота [Принимает реферальный код] [Арабские]", "price": max(_p(24.0585), 10.0), "panel": "panel_4", "desc": "Telegram Старты бота [Таргетинг]"},
        "2208": {"name": "🇮🇳 Запуск бота [Принимает реферальный код] [Индия]", "price": max(_p(25.6107), 10.0), "panel": "panel_4", "desc": "Telegram Старты бота [Таргетинг]"},
        "2209": {"name": "🇺🇸 Запуск бота [Принимает реферальный код] [США]", "price": max(_p(24.0585), 10.0), "panel": "panel_4", "desc": "Telegram Старты бота [Таргетинг]"},
        "2210": {"name": "🇨🇳 Запуск бота [Принимает реферальный код] [Китай]", "price": max(_p(24.0585), 10.0), "panel": "panel_4", "desc": "Telegram Старты бота [Таргетинг]"},
        "2211": {"name": "🇮🇩 Запуск бота [Принимает реферальный код] [Индонезия]", "price": max(_p(24.0585), 10.0), "panel": "panel_4", "desc": "Telegram Старты бота [Таргетинг]"},
        "2212": {"name": "🇮🇱 Запуск бота [Принимает реферальный код] [Израиль]", "price": max(_p(24.0585), 10.0), "panel": "panel_4", "desc": "Telegram Старты бота [Таргетинг]"},
        "2213": {"name": "🇹🇷 Запуск бота [Принимает реферальный код] [Турция]", "price": max(_p(24.0585), 10.0), "panel": "panel_4", "desc": "Telegram Старты бота [Таргетинг]"},
        "2214": {"name": "🇩🇪 Запуск бота [Принимает реферальный код] [Германия]", "price": max(_p(24.0585), 10.0), "panel": "panel_4", "desc": "Telegram Старты бота [Таргетинг]"},
        "2215": {"name": "🇺🇦 Запуск бота [Принимает реферальный код] [Украина]", "price": max(_p(24.0585), 10.0), "panel": "panel_4", "desc": "Telegram Старты бота [Таргетинг]"},
        "2216": {"name": "🇮🇹 Запуск бота [Принимает реферальный код] [Италия]", "price": max(_p(24.0585), 10.0), "panel": "panel_4", "desc": "Telegram Старты бота [Таргетинг]"},
        "2219": {"name": "Telegram живые подписчики с рекламы [Россия]", "price": max(_p(2465.0), 10.0), "panel": "panel_4", "desc": "Telegram Живой трафик с рекламы"},
        "2220": {"name": "Telegram живые подписчики с рекламы [Россия+СНГ]", "price": max(_p(2465.0), 10.0), "panel": "panel_4", "desc": "Telegram Живой трафик с рекламы"},
        "2221": {"name": "Telegram живые подписчики с рекламы [Микс гео]", "price": max(_p(2465.0), 10.0), "panel": "panel_4", "desc": "Telegram Живой трафик с рекламы"},
        "2222": {"name": "Telegram живые подписчики с рекламы [Россия] [Мужчины👦🏻]", "price": max(_p(2465.0), 10.0), "panel": "panel_4", "desc": "Telegram Живой трафик с рекламы"},
        "2223": {"name": "Telegram живые подписчики с рекламы [Россия+СНГ] [Мужчины👦🏻]", "price": max(_p(2465.0), 10.0), "panel": "panel_4", "desc": "Telegram Живой трафик с рекламы"},
        "2224": {"name": "Telegram живые подписчики с рекламы [Микс гео] [Мужчины👦🏻]", "price": max(_p(2465.0), 10.0), "panel": "panel_4", "desc": "Telegram Живой трафик с рекламы"},
        "2225": {"name": "Telegram живые подписчики с рекламы [Россия] [Женщины👩🏻]", "price": max(_p(2465.0), 10.0), "panel": "panel_4", "desc": "Telegram Живой трафик с рекламы"},
        "2226": {"name": "Telegram живые подписчики с рекламы [Россия+СНГ] [Женщины👩🏻]", "price": max(_p(2465.0), 10.0), "panel": "panel_4", "desc": "Telegram Живой трафик с рекламы"},
        "2227": {"name": "Telegram живые подписчики с рекламы [Микс Гео] [Женщины👩🏻]", "price": max(_p(2465.0), 10.0), "panel": "panel_4", "desc": "Telegram Живой трафик с рекламы"},
        "2228": {"name": "Telegram Живые просмотры [Микс] 👥", "price": max(_p(13.775), 10.0), "panel": "panel_4", "desc": "Telegram Живой трафик с рекламы"},
        "2258": {"name": "Telegram Рефералы для @UltimaBulls_com_bot (Ultima Bulls Referrals)", "price": max(_p(4456.2554), 10.0), "panel": "panel_4", "desc": "Telegram Рефералы"},
        "2259": {"name": "Telegram Premium Старты бота [Украина][3 месяца][Реф код]", "price": max(_p(251.9812), 10.0), "panel": "panel_4", "desc": "Telegram Premium Старты бота"},
        "2279": {"name": "Telegram Premium Старты бота [30-60 Дней][Принимают реф] ", "price": max(_p(505.2286), 10.0), "panel": "panel_4", "desc": "Telegram Premium Старты бота [Россия]"},
                "2280": {"name": "Активность для услуги ID2153 [Читать описание]", "price": max(_p(126.6237), 10.0), "panel": "panel_4", "desc": "Telegram Активность ботов"},
        "2281": {"name": "Telegram Звезды на пост", "price": max(_p(1829.9168), 10.0), "panel": "panel_4", "desc": "Telegram Звезды"},
        "2282": {"name": "Telegram Звезды для новых постов (Подписка)", "price": max(_p(1895.2709), 10.0), "panel": "panel_4", "desc": "Telegram Звезды"},
        "2283": {"name": "Telegram Запуск бота [Россия][Принимает реферальный код][Для поиска]", "price": max(_p(126.6237), 10.0), "panel": "panel_4", "desc": "Telegram Активность ботов"},
        "2284": {"name": "Активность для услуги ID2283 [Читать описание]", "price": max(_p(12.6624), 10.0), "panel": "panel_4", "desc": "Telegram Активность ботов"},
        "2289": {"name": "Telegram Микс позитивных реакций + Просмотры [Подписка]", "price": max(_p(1.3071), 10.0), "panel": "panel_4", "desc": "Telegram Авто-Реакции"},
        "2293": {"name": "Telegram Буст канала [1 День][Лучшая цена]⚡️", "price": max(_p(966.4248), 10.0), "panel": "panel_4", "desc": "Telegram Бусты"},
        "2304": {"name": "Telegram Просмотры [Последние 5 постов]", "price": max(_p(1.5828), 10.0), "panel": "panel_4", "desc": "Telegram Просмотры"},
        "2305": {"name": "Telegram Просмотры [Последние 10 постов]", "price": max(_p(3.2677), 10.0), "panel": "panel_4", "desc": "Telegram Просмотры"},
        "2306": {"name": "Telegram Просмотры [Последние 20 постов]", "price": max(_p(6.5354), 10.0), "panel": "panel_4", "desc": "Telegram Просмотры"},
        "2307": {"name": "Telegram Просмотры [Последние 30 постов]", "price": max(_p(9.8031), 10.0), "panel": "panel_4", "desc": "Telegram Просмотры"},
        "2308": {"name": "Telegram Просмотры [Последние 50 постов]", "price": max(_p(16.3385), 10.0), "panel": "panel_4", "desc": "Telegram Просмотры"},
        "2309": {"name": "🇷🇺 Telegram Авто - Просмотры в статистику [Россия]", "price": max(_p(2.6142), 10.0), "panel": "panel_4", "desc": "Telegram Авто-Просмотры"},
        "2312": {"name": "Telegram Поделиться [Репост] [Микс]", "price": max(_p(2.2088), 10.0), "panel": "panel_4", "desc": "Telegram Репосты"},
        "2313": {"name": "🇮🇹 Telegram Поделиться [Репост] [Италия]", "price": max(_p(5.0649), 10.0), "panel": "panel_4", "desc": "Telegram Репосты"},
        "2314": {"name": "🇩🇪 Telegram Поделиться [Репост] [Германия]", "price": max(_p(5.0649), 10.0), "panel": "panel_4", "desc": "Telegram Репосты"},
        "2315": {"name": "🇹🇷 Telegram Поделиться [Репост] [Турция]", "price": max(_p(5.0649), 10.0), "panel": "panel_4", "desc": "Telegram Репосты"},
        "2316": {"name": "🇮🇱 Telegram Поделиться [Репост] [Израиль]", "price": max(_p(5.0649), 10.0), "panel": "panel_4", "desc": "Telegram Репосты"},
        "2317": {"name": "🇺🇸 Telegram Поделиться [Репост] [США]", "price": max(_p(5.0649), 10.0), "panel": "panel_4", "desc": "Telegram Репосты"},
        "2318": {"name": "🇷🇺 Telegram Поделиться [Репост] [Россия]", "price": max(_p(5.0649), 10.0), "panel": "panel_4", "desc": "Telegram Репосты"},
        "2319": {"name": "🇺🇸 Telegram Поделиться [Репост] [США] [50 Будущих постов]", "price": max(_p(379.8711), 10.0), "panel": "panel_4", "desc": "Telegram Репосты"},
        "2320": {"name": "🇷🇺 Telegram Поделиться [Репост] [Россия] [50 Будущих постов]", "price": max(_p(379.8711), 10.0), "panel": "panel_4", "desc": "Telegram Репосты"},
        "2321": {"name": "Telegram Авто - Поделиться [Репост] [Микс]", "price": max(_p(5.0649), 10.0), "panel": "panel_4", "desc": "Telegram Репосты"},
        "2323": {"name": "Telegram Подписчики [Гарантия - 3 дня♻️] [Кнопка восстановления]", "price": max(_p(7.3), 10.0), "panel": "panel_4", "desc": "Private API"},
        "2324": {"name": "Telegram Подписчики [15-30 Дней] [Кнопка восстановления 20]", "price": max(_p(16.0), 10.0), "panel": "panel_4", "desc": "Private API"},
        "2344": {"name": "🌟🤖Telegram Запуск бота Premium Аккаунты [/Start]", "price": max(_p(187.0927), 10.0), "panel": "panel_4", "desc": "Telegram Premium Старты бота"},
        "2352": {"name": "🇷🇺 Telegram Подписчики [Россия] [60к в день]♻️🚀", "price": max(_p(117.6375), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики [Россия]"},
        "2353": {"name": "Telegram Реакции позитивные [👍🤩🎉🔥❤️🥰👏🏻] [Лучшая цена!]", "price": max(_p(0.9476), 10.0), "panel": "panel_4", "desc": "Telegram Реакции"},
        "2354": {"name": "Telegram Реакции негативные [👎😁😢💩🤮🤔🤯🤬] [Лучшая цена!]", "price": max(_p(0.9476), 10.0), "panel": "panel_4", "desc": "Telegram Реакции"},
        "2378": {"name": "Telegram Подписчики [Гарантия - 90 дней] ♻️🚀 🇷🇺", "price": max(_p(141.165), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики [Россия]"},
        "2390": {"name": "Telegram Рефералы для @hitvpnbot (hitvpnbot ✊)", "price": max(_p(14000.0), 10.0), "panel": "panel_4", "desc": "Telegram Рефералы"},
        "2391": {"name": "Telegram Реакции Кастомные [Свои] [Читайте Описание]", "price": max(_p(1.2254), 10.0), "panel": "panel_4", "desc": "Telegram Реакции"},
        "2392": {"name": "🚫 Telegram Жалоба на Канал [Без отчета] [Без причины]", "price": max(_p(4343.1931), 10.0), "panel": "panel_4", "desc": "Telegram Жалобы"},
        "2394": {"name": "🚫 Telegram Жалоба [Без отчета] [Причина: Спам]", "price": max(_p(6204.5616), 10.0), "panel": "panel_4", "desc": "Telegram Жалобы"},
        "2396": {"name": "🚫 Telegram Жалоба [Без отчета] [Причина: Фейк]", "price": max(_p(6204.5616), 10.0), "panel": "panel_4", "desc": "Telegram Жалобы"},
        "2398": {"name": "🚫 Telegram Жалоба [Без отчета] [Причина: Насилие]", "price": max(_p(6204.5616), 10.0), "panel": "panel_4", "desc": "Telegram Жалобы"},
        "2400": {"name": "🚫 Telegram Жалоба [Без отчета] [Причина: Порнография]", "price": max(_p(6204.5616), 10.0), "panel": "panel_4", "desc": "Telegram Жалобы"},
        "2402": {"name": "🚫 Telegram Жалоба [Без отчета] [Причина: Авторское право]", "price": max(_p(6204.5616), 10.0), "panel": "panel_4", "desc": "Telegram Жалобы"},
        "2404": {"name": "🚫 Telegram Жалоба [Без отчета] [Причина: Другое]", "price": max(_p(6204.5616), 10.0), "panel": "panel_4", "desc": "Telegram Жалобы"},
        "2413": {"name": "Telegram Подписчики [Гарантия 120♻️] [Быстрые]", "price": max(_p(113.9613), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики"},
        "2414": {"name": "Telegram Подписчики [Без списаний 30 дней] ♻️🚀 🇷🇺", "price": max(_p(79.7321), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики [Россия]"},
        "2415": {"name": "Telegram Подписчики [Без списаний 60 дней] ♻️🚀 🇷🇺", "price": max(_p(100.6454), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики [Россия]"},
        "2416": {"name": "Telegram Подписчики [Без списаний 90 дней] ♻️🚀 🇷🇺", "price": max(_p(120.2517), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики [Россия]"},
        "2417": {"name": "Telegram Подписчики [Без списаний 180 дней] ♻️🚀 🇷🇺", "price": max(_p(182.9917), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики [Россия]"},
        "2453": {"name": "Telegram Подписчики для реакций [Для закрытых каналов]", "price": max(_p(256.5), 10.0), "panel": "panel_4", "desc": "Telegram Реакции [Для закрытых каналов]"},
        "2454": {"name": "Telegram Реакции [👍 ❤️ 🔥 🎉🤩 😁] [Для закрытого канала]", "price": max(_p(12.92), 10.0), "panel": "panel_4", "desc": "Telegram Реакции [Для закрытых каналов]"},
        "2456": {"name": "Telegram Реакция [👍] [Для закрытого канала]", "price": max(_p(12.92), 10.0), "panel": "panel_4", "desc": "Telegram Реакции [Для закрытых каналов]"},
        "2478": {"name": "Telegram Просмотры [10 в минуту]", "price": max(_p(3.1125), 10.0), "panel": "panel_4", "desc": "Telegram Просмотры с настройкой скорости [Россия]"},
        "2479": {"name": "Telegram Просмотры [1 в минуту]", "price": max(_p(3.1125), 10.0), "panel": "panel_4", "desc": "Telegram Просмотры с настройкой скорости [Россия]"},
        "2480": {"name": "Telegram Просмотры [2 в минуту]", "price": max(_p(3.1125), 10.0), "panel": "panel_4", "desc": "Telegram Просмотры с настройкой скорости [Россия]"},
        "2481": {"name": "Telegram Просмотры [5 в минуту]", "price": max(_p(3.1125), 10.0), "panel": "panel_4", "desc": "Telegram Просмотры с настройкой скорости [Россия]"},
        "2482": {"name": "Telegram Просмотры [50 в минуту]", "price": max(_p(3.1125), 10.0), "panel": "panel_4", "desc": "Telegram Просмотры с настройкой скорости [Россия]"},
        "2483": {"name": "Telegram Просмотры [20 в минуту]", "price": max(_p(3.1125), 10.0), "panel": "panel_4", "desc": "Telegram Просмотры с настройкой скорости [Россия]"},
        "2484": {"name": "Telegram Просмотры [70 в минуту]", "price": max(_p(3.1125), 10.0), "panel": "panel_4", "desc": "Telegram Просмотры с настройкой скорости [Россия]"},
        "2499": {"name": "Telegram Просмотры [Моментальные] [Реальные]", "price": max(_p(2.6959), 10.0), "panel": "panel_4", "desc": "Telegram Просмотры одного поста"},
        "2504": {"name": "🇷🇺 Telegram Подписчики [Россия] [Без списаний]♻️🚀", "price": max(_p(304.0), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики [Россия]"},
        "2514": {"name": "🌟🤖Telegram Запуск бота Premium Аккаунты [30 дней] [С Активностью]", "price": max(_p(443.183), 10.0), "panel": "panel_4", "desc": "Telegram Premium Старты бота"},
        "2517": {"name": "🌟🤖Telegram Запуск бота Premium Аккаунты [90 дней] [С Активностью]", "price": max(_p(683.768), 10.0), "panel": "panel_4", "desc": "Telegram Premium Старты бота"},
        "2533": {"name": "Telegram Онлайн подписчики [Читайте Описание]", "price": max(_p(291.2345), 10.0), "panel": "panel_4", "desc": "Telegram Онлайн Подписчики"},
        "2534": {"name": "Telegram Онлайн подписчики + сообщение [Германия] [Группа]", "price": max(_p(126.6237), 10.0), "panel": "panel_4", "desc": "Telegram Онлайн Подписчики"},
        "2535": {"name": "Telegram Онлайн подписчики + сообщение [Турция] [Группа]", "price": max(_p(126.6237), 10.0), "panel": "panel_4", "desc": "Telegram Онлайн Подписчики"},
        "2536": {"name": "Telegram Онлайн подписчики + сообщение [Америка] [Группа]", "price": max(_p(126.6237), 10.0), "panel": "panel_4", "desc": "Telegram Онлайн Подписчики"},
        "2537": {"name": "Telegram Онлайн подписчики + сообщение [Израиль] [Группа]", "price": max(_p(126.6237), 10.0), "panel": "panel_4", "desc": "Telegram Онлайн Подписчики"},
        "2538": {"name": "Telegram Онлайн подписчики + сообщение [Узбекистан] [Группа]", "price": max(_p(126.6237), 10.0), "panel": "panel_4", "desc": "Telegram Онлайн Подписчики"},
        "2539": {"name": "Telegram Онлайн подписчики + сообщение [Китай] [Группа]", "price": max(_p(126.6237), 10.0), "panel": "panel_4", "desc": "Telegram Онлайн Подписчики"},
        "2540": {"name": "Telegram Онлайн подписчики + сообщения [RU+EN]", "price": max(_p(219.059), 10.0), "panel": "panel_4", "desc": "Telegram Онлайн Подписчики"},
        "2561": {"name": "Telegram Подписчики + Онлайн [Без списаний 30 дней] ♻️🚀 🇷🇺", "price": max(_p(153.9744), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики [Россия]"},
        "2563": {"name": "Telegram Подписчики без списаний [Переполнение] [Крупные]", "price": max(_p(52.9369), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики"},
        "2567": {"name": "🇷🇺 Telegram Подписчики [Россия] [3 Дня] [Лучшая Цена!]♻️🚀", "price": max(_p(26.1417), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики [Россия]"},
        "2568": {"name": "🇷🇺 Telegram Подписчики [Россия] [7 Дней] [Лучшая Цена!]♻️🚀", "price": max(_p(32.6771), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики [Россия]"},
        "2569": {"name": "🇷🇺 Telegram Подписчики [Россия] [30 Дней] [Лучшая Цена!]♻️🚀", "price": max(_p(192.85), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики [Россия]"},
        "2571": {"name": "🇷🇺 Telegram Буст канала [1 День] [Русские Аккаунты]", "price": max(_p(1577.0778), 10.0), "panel": "panel_4", "desc": "Telegram Бусты [Россия]"},
        "2572": {"name": "🇷🇺 Telegram Буст канала [7 Дней] [Русские Аккаунты]", "price": max(_p(6837.6801), 10.0), "panel": "panel_4", "desc": "Telegram Бусты [Россия]"},
        "2573": {"name": "🇷🇺 Telegram Буст канала [14 Дней] [Русские Аккаунты]", "price": max(_p(11579.9421), 10.0), "panel": "panel_4", "desc": "Telegram Бусты [Россия]"},
        "2574": {"name": "🇷🇺 Telegram Буст канала [30 Дней] [Русские Аккаунты]", "price": max(_p(21064.466), 10.0), "panel": "panel_4", "desc": "Telegram Бусты [Россия]"},
        "2575": {"name": "🇷🇺 Telegram Буст канала [60 Дней] [Русские Аккаунты]", "price": max(_p(36724.9591), 10.0), "panel": "panel_4", "desc": "Telegram Бусты [Россия]"},
        "2576": {"name": "🇷🇺 Telegram Буст канала [90 Дней] [Русские Аккаунты]", "price": max(_p(50400.3193), 10.0), "panel": "panel_4", "desc": "Telegram Бусты [Россия]"},
        "2577": {"name": "🇷🇺 Telegram Буст канала [180 Дней] [Русские Аккаунты]", "price": max(_p(80728.739), 10.0), "panel": "panel_4", "desc": "Telegram Бусты [Россия]"},
        "2579": {"name": "Telegram Premium Старты бота [30 Дней + Активность]", "price": max(_p(435.5855), 10.0), "panel": "panel_4", "desc": "Telegram Premium Старты бота [Россия]"},
        "2580": {"name": "Telegram Premium Старты бота [60 Дней + Активность]", "price": max(_p(607.7938), 10.0), "panel": "panel_4", "desc": "Telegram Premium Старты бота [Россия]"},
        "2581": {"name": "Telegram Premium Старты бота [90 Дней + Активность]", "price": max(_p(734.4175), 10.0), "panel": "panel_4", "desc": "Telegram Premium Старты бота [Россия]"},
        "2582": {"name": "Telegram Premium Старты бота [180 Дней + Активность]", "price": max(_p(1012.9896), 10.0), "panel": "panel_4", "desc": "Telegram Premium Старты бота [Россия]"},
        "2583": {"name": "Telegram Подписчики [60 Дней без списаний♻️] [Сервер: 2]", "price": max(_p(84.699), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики"},
        "2623": {"name": "🌟🤖Telegram Запуск бота Premium Аккаунты [Китай]🇨🇳", "price": max(_p(1266.2371), 10.0), "panel": "panel_4", "desc": "Telegram Premium Старты бота"},
        "2624": {"name": "🌟🤖Telegram Запуск бота Premium Аккаунты [Украина]🇺🇦", "price": max(_p(620.4562), 10.0), "panel": "panel_4", "desc": "Telegram Premium Старты бота"},
        "2625": {"name": "🌟🤖Telegram Запуск бота Premium Аккаунты [Узбекистан]🇺🇿", "price": max(_p(1266.2371), 10.0), "panel": "panel_4", "desc": "Telegram Premium Старты бота"},
        "2626": {"name": "🌟🤖Telegram Запуск бота Premium Аккаунты [Индия]🇮🇳", "price": max(_p(1266.2371), 10.0), "panel": "panel_4", "desc": "Telegram Premium Старты бота"},
        "2627": {"name": "🌟🤖Telegram Запуск бота Premium Аккаунты [Турция]🇹🇷", "price": max(_p(1266.2371), 10.0), "panel": "panel_4", "desc": "Telegram Premium Старты бота"},
        "2628": {"name": "🌟🤖Telegram Запуск бота Premium Аккаунты [ОАЭ]🇸🇦", "price": max(_p(1266.2371), 10.0), "panel": "panel_4", "desc": "Telegram Premium Старты бота"},
        "2629": {"name": "🌟🤖Telegram Запуск бота Premium Аккаунты [Израиль]🇮🇱", "price": max(_p(886.3659), 10.0), "panel": "panel_4", "desc": "Telegram Premium Старты бота"},
        "2631": {"name": "Telegram Авто - Просмотры - 10 Будущих постов.", "price": max(_p(4.6344), 10.0), "panel": "panel_4", "desc": "Telegram Авто-Просмотры"},
        "2635": {"name": "Telegram Авто - Просмотры - 50 Будущих постов.", "price": max(_p(23.1721), 10.0), "panel": "panel_4", "desc": "Telegram Авто-Просмотры"},
        "2636": {"name": "Telegram Авто - Просмотры - 100 Будущих постов.", "price": max(_p(46.3569), 10.0), "panel": "panel_4", "desc": "Telegram Авто-Просмотры"},
        "2641": {"name": "Активность для услуги ID2624 [Читать описание]", "price": max(_p(126.6237), 10.0), "panel": "panel_4", "desc": "Telegram Активность ботов"},
        "2644": {"name": "🇵🇱 Telegram Просмотры на пост [Польша]", "price": max(_p(2.124), 10.0), "panel": "panel_4", "desc": "Telegram Просмотры [Таргетинг]"},
        "2645": {"name": "🇩🇪 Telegram Просмотры на пост [Германия]", "price": max(_p(2.124), 10.0), "panel": "panel_4", "desc": "Telegram Просмотры [Таргетинг]"},
        "2646": {"name": "🇬🇧 Telegram Просмотры на пост [Великобритания]", "price": max(_p(2.124), 10.0), "panel": "panel_4", "desc": "Telegram Просмотры [Таргетинг]"},
        "2647": {"name": "Telegram Просмотры на пост [🇷🇺 🇮🇱 🇺🇸 🇰🇷 🇩🇪 🇮🇳 🇨🇳 🇹🇷 🇸🇦]", "price": max(_p(2.124), 10.0), "panel": "panel_4", "desc": "Telegram Просмотры [Таргетинг]"},
                "2648": {"name": "🇺🇦 Telegram Просмотры на пост [Украина]", "price": max(_p(2.124), 10.0), "panel": "panel_4", "desc": "Telegram Просмотры [Таргетинг]"},
        "2649": {"name": "🇰🇿 Telegram Просмотры на пост [Казахстан]", "price": max(_p(2.124), 10.0), "panel": "panel_4", "desc": "Telegram Просмотры [Таргетинг]"},
        "2650": {"name": "🇺🇸 Telegram Просмотры на пост [США]", "price": max(_p(2.124), 10.0), "panel": "panel_4", "desc": "Telegram Просмотры [Таргетинг]"},
        "2651": {"name": "🇷🇺 Telegram Просмотры на пост [Россия]", "price": max(_p(2.124), 10.0), "panel": "panel_4", "desc": "Telegram Просмотры [Таргетинг]"},
        "2652": {"name": "🇮🇳 Telegram Подписчики [Индия] [Гарантия 90 дней]", "price": max(_p(101.9688), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики (Таргетинг)"},
        "2653": {"name": "🇺🇦 Telegram Подписчики [Украина] [Гарантия 3 дня]", "price": max(_p(25.3247), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики (Таргетинг)"},
        "2654": {"name": "🇺🇦 Telegram Подписчики [Украина] [Гарантия 7 дней]", "price": max(_p(31.6559), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики (Таргетинг)"},
        "2655": {"name": "🇺🇦 Telegram Подписчики [Украина] [Гарантия 14 дней]", "price": max(_p(43.0521), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики (Таргетинг)"},
        "2656": {"name": "🇺🇦 Telegram Подписчики [Украина] [Гарантия 30 дней]", "price": max(_p(77.2405), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики (Таргетинг)"},
        "2657": {"name": "🇺🇦 Telegram Подписчики [Украина] [Гарантия 60 дней]", "price": max(_p(101.299), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики (Таргетинг)"},
        "2658": {"name": "Telegram Просмотры [Имитация живой активности]", "price": max(_p(3.7987), 10.0), "panel": "panel_4", "desc": "Telegram Умные Просмотры"},
        "2659": {"name": "Telegram Авто - Просмотры [Имитация живой активности]", "price": max(_p(3.7987), 10.0), "panel": "panel_4", "desc": "Telegram Умные Просмотры"},
        "2661": {"name": "Telegram Просмотры поста [Быстрые]", "price": max(_p(0.2483), 10.0), "panel": "panel_4", "desc": "Telegram Просмотры одного поста"},
        "2667": {"name": "🇷🇺 Telegram Подписчики [Россия] [14 Дней] [Лучшая Цена!]♻️🚀", "price": max(_p(40.2745), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики [Россия]"},
        "2668": {"name": "Telegram Просмотры поста [Моментальные][С реальных аккаунтов]", "price": max(_p(1.45), 10.0), "panel": "panel_4", "desc": "Telegram Просмотры одного поста"},
        "2669": {"name": "Telegram Буст канала [15 Дней] [Гарантия]⚡️", "price": max(_p(11016.2623), 10.0), "panel": "panel_4", "desc": "Telegram Бусты"},
        "2671": {"name": "🌟Telegram Просмотры на пост [Premium Аккаунты]", "price": max(_p(9.9502), 10.0), "panel": "panel_4", "desc": "Telegram Premium Просмотры"},
        "2672": {"name": "🌟Telegram Просмотры на последние 5 постов [Premium]", "price": max(_p(49.7509), 10.0), "panel": "panel_4", "desc": "Telegram Premium Просмотры"},
        "2673": {"name": "🌟Telegram Просмотры на последние 20 постов [Premium]", "price": max(_p(199.0034), 10.0), "panel": "panel_4", "desc": "Telegram Premium Просмотры"},
        "2674": {"name": "🌟Telegram Просмотры на последние 50 постов [Premium]", "price": max(_p(426.436), 10.0), "panel": "panel_4", "desc": "Telegram Premium Просмотры"},
        "2675": {"name": "🌟Telegram Просмотры на последние 100 постов [Premium]", "price": max(_p(739.1557), 10.0), "panel": "panel_4", "desc": "Telegram Premium Просмотры"},
        "2704": {"name": "🔥Telegram Подписчики [90 Дней без списаний♻️] [Лучшая Цена]", "price": max(_p(40.4379), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики"},
        "2705": {"name": "Telegram Просмотры поста [Медленные]", "price": max(_p(0.1144), 10.0), "panel": "panel_4", "desc": "Telegram Просмотры одного поста"},
        "2707": {"name": "🔥Telegram Подписчики [180 Дней без списаний♻️] [Быстрые]", "price": max(_p(124.0912), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики"},
        "2708": {"name": "🔥Telegram Подписчики [280 Дней без списаний♻️] [Быстрые]", "price": max(_p(164.6517), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики"},
        "2720": {"name": "Telegram Подписчики с активностью [На 150 прошлых постов]", "price": max(_p(379.8711), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики с активностью"},
        "2721": {"name": "Telegram Подписчики с активностью [На 300 прошлых постов]", "price": max(_p(759.7422), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики с активностью"},
        "2723": {"name": "🌟Telegram Буст канала [1 День][Долгий старт][Русские]", "price": max(_p(1500.0), 10.0), "panel": "panel_4", "desc": "Telegram Бусты"},
        "2733": {"name": "Telegram Просмотры [Последние 100 постов]", "price": max(_p(32.6771), 10.0), "panel": "panel_4", "desc": "Telegram Просмотры"},
        "2734": {"name": "Telegram Просмотры [Последние 200 постов]", "price": max(_p(65.3542), 10.0), "panel": "panel_4", "desc": "Telegram Просмотры"},
        "2735": {"name": "Telegram Просмотры [Последние 500 постов]", "price": max(_p(163.3854), 10.0), "panel": "panel_4", "desc": "Telegram Просмотры"},
        "2745": {"name": "🌟Telegram Premium Старты бота [5 Дней + Активность]", "price": max(_p(306.3477), 10.0), "panel": "panel_4", "desc": "Telegram Premium Старты бота"},
        "2746": {"name": "🌟Telegram Premium Старты бота [10 Дней + Активность]", "price": max(_p(341.884), 10.0), "panel": "panel_4", "desc": "Telegram Premium Старты бота"},
        "2747": {"name": "🌟Telegram Premium Старты бота [15 Дней + Активность]", "price": max(_p(367.2087), 10.0), "panel": "panel_4", "desc": "Telegram Premium Старты бота"},
        "2748": {"name": "🌟Telegram Premium Старты бота [20 Дней + Активность]", "price": max(_p(391.1856), 10.0), "panel": "panel_4", "desc": "Telegram Premium Старты бота"},
        "2752": {"name": "🌟🤖Telegram Запуск бота Premium Аккаунты [30-90 дней]", "price": max(_p(194.4287), 10.0), "panel": "panel_4", "desc": "Telegram Premium Старты бота"},
        "2753": {"name": "Telegram Буст канала [180 Дней] [Все типы каналов]", "price": max(_p(81326.7296), 10.0), "panel": "panel_4", "desc": "Telegram Бусты"},
        "2754": {"name": "Telegram Буст канала [90 Дней] [Все типы каналов]", "price": max(_p(49653.6479), 10.0), "panel": "panel_4", "desc": "Telegram Бусты"},
        "2757": {"name": "🇨🇳 Telegram Просмотры на пост [Китай]", "price": max(_p(2.1861), 10.0), "panel": "panel_4", "desc": "Telegram Просмотры [Таргетинг]"},
        "2758": {"name": "🇸🇦 Telegram Просмотры на пост [Арабы]", "price": max(_p(2.1861), 10.0), "panel": "panel_4", "desc": "Telegram Просмотры [Таргетинг]"},
        "2759": {"name": "🇷🇺 Telegram Просмотры на пост [Россия] [Лучшая цена!]", "price": max(_p(1.6175), 10.0), "panel": "panel_4", "desc": "Telegram Просмотры [Таргетинг]"},
        "2760": {"name": "(Private)Telegram Подписчики [Без списаний 30 дней♻️]", "price": max(_p(42.2395), 10.0), "panel": "panel_4", "desc": "Private API"},
        "2777": {"name": "🌟🤖Telegram Запуск бота Premium Аккаунты [7 дней][С Активностью]", "price": max(_p(514.6641), 10.0), "panel": "panel_4", "desc": "Telegram Premium Старты бота"},
        "2778": {"name": "🌟🤖Telegram Запуск бота Premium Аккаунты [15 дней][С Активностью]", "price": max(_p(588.1875), 10.0), "panel": "panel_4", "desc": "Telegram Premium Старты бота"},
        "2779": {"name": "🌟🤖Telegram Запуск бота Premium Аккаунты [30 дней][С Активностью]", "price": max(_p(612.6953), 10.0), "panel": "panel_4", "desc": "Telegram Premium Старты бота"},
        "2814": {"name": "Запуск бота [Принимает реферальный код]", "price": max(_p(20.9133), 10.0), "panel": "panel_4", "desc": "Telegram Старты бота"},
        "2828": {"name": "Запуск бота [Случайные 10 стран] [Запуск из поиска]", "price": max(_p(58.8188), 10.0), "panel": "panel_4", "desc": "Telegram Старты бота"},
        "2830": {"name": "Telegram Подписчики [7 Дней без списаний♻️]", "price": max(_p(18.5), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики"},
        "2831": {"name": "Telegram Подписчики [30 Дней без списаний♻️] [Моментальные]", "price": max(_p(30.0), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики"},
        "2832": {"name": "Telegram Подписчики [14 Дней без списаний♻️]", "price": max(_p(22.0), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики"},
        "2833": {"name": "Telegram Подписчики [3 Дня без списаний♻️]", "price": max(_p(14.0), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики"},
        "2864": {"name": "🇰🇿 Запуск бота [Принимает реферальный код] [Казахстан]", "price": max(_p(20.2598), 10.0), "panel": "panel_4", "desc": "Telegram Старты бота [Таргетинг]"},
        "2865": {"name": "🇧🇷 Запуск бота [Принимает реферальный код] [Бразилия]", "price": max(_p(20.2598), 10.0), "panel": "panel_4", "desc": "Telegram Старты бота [Таргетинг]"},
        "2913": {"name": "Запуск бота [Принимает реферальный код][Быстрые][Русские]", "price": max(_p(19.6063), 10.0), "panel": "panel_4", "desc": "Telegram Старты бота"},
        "2918": {"name": "Telegram Просмотры [Для закрытых каналов] [1 в минуту]", "price": max(_p(3.9213), 10.0), "panel": "panel_4", "desc": "Telegram Просмотры [Для закрытых каналов]"},
        "2919": {"name": "Telegram Просмотры [Для закрытых каналов] [2 в минуту]", "price": max(_p(3.9213), 10.0), "panel": "panel_4", "desc": "Telegram Просмотры [Для закрытых каналов]"},
        "2920": {"name": "Telegram Просмотры [Для закрытых каналов] [5 в минуту]", "price": max(_p(3.9213), 10.0), "panel": "panel_4", "desc": "Telegram Просмотры [Для закрытых каналов]"},
        "2921": {"name": "Telegram Просмотры [Для закрытых каналов] [10 в минуту]", "price": max(_p(3.9213), 10.0), "panel": "panel_4", "desc": "Telegram Просмотры [Для закрытых каналов]"},
        "2922": {"name": "Telegram Просмотры [Для закрытых каналов] [20 в минуту]", "price": max(_p(3.9213), 10.0), "panel": "panel_4", "desc": "Telegram Просмотры [Для закрытых каналов]"},
        "2923": {"name": "Telegram Просмотры [Для закрытых каналов] [50 в минуту]", "price": max(_p(3.9213), 10.0), "panel": "panel_4", "desc": "Telegram Просмотры [Для закрытых каналов]"},
        "2924": {"name": "Telegram Просмотры [Для закрытых каналов] [70 в минуту]", "price": max(_p(3.9213), 10.0), "panel": "panel_4", "desc": "Telegram Просмотры [Для закрытых каналов]"},
        "2925": {"name": "🇷🇺 Telegram Просмотры на пост [Россия] [До 10 публикаций]", "price": max(_p(2.1567), 10.0), "panel": "panel_4", "desc": "Telegram Просмотры"},
        "2926": {"name": "Telegram Premium RU Подписчики [3 Дня]", "price": max(_p(185.6058), 10.0), "panel": "panel_4", "desc": "Telegram Premium Подписчики [Россия]"},
        "2927": {"name": "Telegram Premium RU Подписчики [7 Дней]", "price": max(_p(284.9442), 10.0), "panel": "panel_4", "desc": "Telegram Premium Подписчики [Россия]"},
        "2928": {"name": "Telegram Premium RU Подписчики [10 Дней]", "price": max(_p(372.5188), 10.0), "panel": "panel_4", "desc": "Telegram Premium Подписчики [Россия]"},
        "2929": {"name": "Telegram Premium RU Подписчики [15 Дней]", "price": max(_p(433.9517), 10.0), "panel": "panel_4", "desc": "Telegram Premium Подписчики [Россия]"},
        "2930": {"name": "Telegram Premium RU Подписчики [20 Дней]", "price": max(_p(496.6917), 10.0), "panel": "panel_4", "desc": "Telegram Premium Подписчики [Россия]"},
        "2931": {"name": "Telegram Premium RU Подписчики [30 Дней]", "price": max(_p(562.0459), 10.0), "panel": "panel_4", "desc": "Telegram Premium Подписчики [Россия]"},
        "2932": {"name": "Telegram Premium RU Подписчики [25 Дней]", "price": max(_p(607.7938), 10.0), "panel": "panel_4", "desc": "Telegram Premium Подписчики [Россия]"},
        "2933": {"name": "Telegram Premium RU Подписчики [60 Дней]", "price": max(_p(1266.2371), 10.0), "panel": "panel_4", "desc": "Telegram Premium Подписчики [Россия]"},
        "2934": {"name": "Telegram Premium RU Подписчики [90 Дней]", "price": max(_p(1810.719), 10.0), "panel": "panel_4", "desc": "Telegram Premium Подписчики [Россия]"},
        "2935": {"name": "Telegram Premium RU Подписчики [180 Дней]", "price": max(_p(3038.9689), 10.0), "panel": "panel_4", "desc": "Telegram Premium Подписчики [Россия]"},
        "2958": {"name": "🇺🇸 Запуск бота [Старт из поиска] [США]", "price": max(_p(52.2833), 10.0), "panel": "panel_4", "desc": "Telegram Старты бота [Таргетинг]"},
        "2959": {"name": "🇮🇷 Запуск бота [Старт из поиска] [Иран]", "price": max(_p(52.2833), 10.0), "panel": "panel_4", "desc": "Telegram Старты бота [Таргетинг]"},
        "2960": {"name": "🇸🇦 Запуск бота [Старт из поиска] [Арабы]", "price": max(_p(52.2833), 10.0), "panel": "panel_4", "desc": "Telegram Старты бота [Таргетинг]"},
        "2961": {"name": "🇨🇳 Запуск бота [Старт из поиска] [Китай]", "price": max(_p(52.2833), 10.0), "panel": "panel_4", "desc": "Telegram Старты бота [Таргетинг]"},
        "2962": {"name": "🇮🇳 Запуск бота [Старт из поиска] [Индия]", "price": max(_p(52.2833), 10.0), "panel": "panel_4", "desc": "Telegram Старты бота [Таргетинг]"},
        "2963": {"name": "🇷🇺 Запуск бота [Старт из поиска] [Россия]", "price": max(_p(52.2833), 10.0), "panel": "panel_4", "desc": "Telegram Старты бота [Таргетинг]"},
        "2964": {"name": "🇹🇷 Запуск бота [Старт из поиска] [Турция]", "price": max(_p(52.2833), 10.0), "panel": "panel_4", "desc": "Telegram Старты бота [Таргетинг]"},
        "2965": {"name": "🇩🇪 Запуск бота [Старт из поиска] [Германия]", "price": max(_p(52.2833), 10.0), "panel": "panel_4", "desc": "Telegram Старты бота [Таргетинг]"},
        "2966": {"name": "🇫🇷 Запуск бота [Старт из поиска] [Франция]", "price": max(_p(52.2833), 10.0), "panel": "panel_4", "desc": "Telegram Старты бота [Таргетинг]"},
        "2967": {"name": "🇮🇱 Запуск бота [Старт из поиска] [Израиль]", "price": max(_p(52.2833), 10.0), "panel": "panel_4", "desc": "Telegram Старты бота [Таргетинг]"},
        "2968": {"name": "🇮🇩 Запуск бота [Старт из поиска] [Индонезия]", "price": max(_p(52.2833), 10.0), "panel": "panel_4", "desc": "Telegram Старты бота [Таргетинг]"},
        "2969": {"name": "🇮🇹 Запуск бота [Старт из поиска] [Италия]", "price": max(_p(52.2833), 10.0), "panel": "panel_4", "desc": "Telegram Старты бота [Таргетинг]"},
        "2970": {"name": "🇰🇿 Запуск бота [Старт из поиска] [Казахстан]", "price": max(_p(52.2833), 10.0), "panel": "panel_4", "desc": "Telegram Старты бота [Таргетинг]"},
        "2971": {"name": "🇧🇷 Запуск бота [Старт из поиска] [Бразилия]", "price": max(_p(52.2833), 10.0), "panel": "panel_4", "desc": "Telegram Старты бота [Таргетинг]"},
        "2973": {"name": "🌟🤖Telegram Рестарт бота Premium Аккаунты для ID1238", "price": max(_p(288.2119), 10.0), "panel": "panel_4", "desc": "Telegram Premium Старты бота"},
        "2975": {"name": "🇬🇧 Telegram Подписчики + комментарий [США]", "price": max(_p(126.6237), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики (Продвижение групп)"},
        "2976": {"name": "🇩🇪 Telegram Подписчики + комментарий [Германия]", "price": max(_p(126.6237), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики (Продвижение групп)"},
        "2977": {"name": "🇦🇪 Telegram Подписчики + комментарий [Арабы]", "price": max(_p(126.6237), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики (Продвижение групп)"},
        "2978": {"name": "🇹🇷 Telegram Подписчики + комментарий [Турция]", "price": max(_p(126.6237), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики (Продвижение групп)"},
        "2979": {"name": "🇮🇳 Telegram Подписчики + комментарий [Индия]", "price": max(_p(126.6237), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики (Продвижение групп)"},
        "2980": {"name": "🇮🇱 Telegram Подписчики + комментарий [Израиль]", "price": max(_p(126.6237), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики (Продвижение групп)"},
        "2981": {"name": "🇺🇿 Telegram Подписчики + комментарий [Узбекистан]", "price": max(_p(126.6237), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики (Продвижение групп)"},
        "2995": {"name": "🌟🤖Telegram Запуск бота Premium Аккаунты [Топ база]", "price": max(_p(456.1721), 10.0), "panel": "panel_4", "desc": "Telegram Premium Старты бота"},
        "2996": {"name": "🇷🇺 Запуск бота [Принимает реферальный код][Россия][Сервер: 2]", "price": max(_p(17.1555), 10.0), "panel": "panel_4", "desc": "Telegram Старты бота [Таргетинг]"},
        "3005": {"name": "🇨🇳 Telegram Подписчики [30 Дней без списаний♻️] [Китай]", "price": max(_p(78.425), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики (Таргетинг)"},
                "3006": {"name": "🇦🇪 Telegram Подписчики [30 Дней без списаний♻️] [Арабы]", "price": max(_p(45.7479), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики (Таргетинг)"},
        "3007": {"name": "🇪🇺 Telegram Подписчики [Без списаний] [Европа]", "price": max(_p(62.74), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики (Таргетинг)"},
        "3009": {"name": "🔥Telegram Подписчики [90 Дней без списаний♻️] [Лучшая Цена]", "price": max(_p(26.9586), 10.0), "panel": "panel_4", "desc": "Private API"},
        "3017": {"name": "Telegram Комментарии по теме поста [Искусственный Интеллект]", "price": max(_p(355.3633), 10.0), "panel": "panel_4", "desc": "Telegram Комментарии"},
        "3018": {"name": "Telegram Авто - Просмотры - 5 Будущих постов [Для закрытых каналов]", "price": max(_p(25.3247), 10.0), "panel": "panel_4", "desc": "Telegram Авто-Просмотры [Для закрытых каналов]"},
        "3019": {"name": "Telegram Авто - Просмотры - 10 Будущих постов [Для закрытых]", "price": max(_p(50.6495), 10.0), "panel": "panel_4", "desc": "Telegram Авто-Просмотры [Для закрытых каналов]"},
        "3020": {"name": "Telegram Авто - Просмотры - 20 Будущих постов [Для закрытых]", "price": max(_p(101.299), 10.0), "panel": "panel_4", "desc": "Telegram Авто-Просмотры [Для закрытых каналов]"},
        "3021": {"name": "Telegram Авто - Просмотры - 30 Будущих постов [Для закрытых]", "price": max(_p(151.9484), 10.0), "panel": "panel_4", "desc": "Telegram Авто-Просмотры [Для закрытых каналов]"},
        "3022": {"name": "Telegram Авто - Просмотры - 50 Будущих постов [Для закрытых]", "price": max(_p(253.2474), 10.0), "panel": "panel_4", "desc": "Telegram Авто-Просмотры [Для закрытых каналов]"},
        "3023": {"name": "Telegram Авто - Просмотры - 100 Будущих постов [Для закрытых]", "price": max(_p(506.4948), 10.0), "panel": "panel_4", "desc": "Telegram Авто-Просмотры [Для закрытых каналов]"},
        "3024": {"name": "Telegram Авто - Просмотры - 250 Будущих постов [Для закрытых]", "price": max(_p(1266.2371), 10.0), "panel": "panel_4", "desc": "Telegram Авто-Просмотры [Для закрытых каналов]"},
        "3025": {"name": "Telegram Авто - Просмотры - 500 Будущих постов [Для закрытых]", "price": max(_p(2532.4741), 10.0), "panel": "panel_4", "desc": "Telegram Авто-Просмотры [Для закрытых каналов]"},
        "3026": {"name": "Telegram Авто - Просмотры - 1000 Будущих постов [Для закрытых]", "price": max(_p(5064.9482), 10.0), "panel": "panel_4", "desc": "Telegram Авто-Просмотры [Для закрытых каналов]"},
        "3028": {"name": "Telegram ИИ Подписчики в группу с общением 3 дня", "price": max(_p(1712.2793), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики (Продвижение групп)"},
        "3029": {"name": "Telegram ИИ Подписчики в группу с общением 7 дней", "price": max(_p(3424.5585), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики (Продвижение групп)"},
        "3030": {"name": "Telegram ИИ Подписчики в группу с общением 15 дней", "price": max(_p(7705.2567), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики (Продвижение групп)"},
        "3031": {"name": "Telegram ИИ Подписчики в группу с общением 30 дней", "price": max(_p(13912.269), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики (Продвижение групп)"},
        "3032": {"name": "Telegram Старты бота [ИИ Поиск по ключевым словам]", "price": max(_p(43.1338), 10.0), "panel": "panel_4", "desc": "Telegram Старты бота [ИИ]"},
        "3033": {"name": "🇷🇺Telegram Старты бота [ИИ Поиск по ключевым словам][Россия]", "price": max(_p(53.9172), 10.0), "panel": "panel_4", "desc": "Telegram Старты бота [ИИ]"},
        "3034": {"name": "🇨🇳Telegram Старты бота [ИИ Поиск][Китай]", "price": max(_p(53.9172), 10.0), "panel": "panel_4", "desc": "Telegram Старты бота [ИИ]"},
        "3035": {"name": "🇺🇸Telegram Старты бота [ИИ Поиск][США]", "price": max(_p(53.9172), 10.0), "panel": "panel_4", "desc": "Telegram Старты бота [ИИ]"},
        "3036": {"name": "🇺🇦Telegram Старты бота [ИИ Поиск][Украина]", "price": max(_p(53.9172), 10.0), "panel": "panel_4", "desc": "Telegram Старты бота [ИИ]"},
        "3037": {"name": "🇺🇿Telegram Старты бота [ИИ Поиск][Узбекистан]", "price": max(_p(53.9172), 10.0), "panel": "panel_4", "desc": "Telegram Старты бота [ИИ]"},
        "3038": {"name": "🇮🇱Telegram Старты бота [ИИ Поиск][Израиль]", "price": max(_p(53.9172), 10.0), "panel": "panel_4", "desc": "Telegram Старты бота [ИИ]"},
        "3039": {"name": "🇮🇳Telegram Старты бота [ИИ Поиск][Индия]", "price": max(_p(53.9172), 10.0), "panel": "panel_4", "desc": "Telegram Старты бота [ИИ]"},
        "3040": {"name": "🇸🇦Telegram Старты бота [ИИ Поиск][Арабы]", "price": max(_p(53.9172), 10.0), "panel": "panel_4", "desc": "Telegram Старты бота [ИИ]"},
        "3043": {"name": "Telegram Premium Старты бота [ИИ Поиск]", "price": max(_p(624.4591), 10.0), "panel": "panel_4", "desc": "Telegram Premium Старты бота [ИИ]"},
        "3044": {"name": "🇷🇺Telegram Premium Старты бота [ИИ Поиск][Россия]", "price": max(_p(637.2032), 10.0), "panel": "panel_4", "desc": "Telegram Premium Старты бота [ИИ]"},
        "3045": {"name": "🇨🇳Telegram Premium Старты бота [ИИ Поиск][Китай]", "price": max(_p(637.2032), 10.0), "panel": "panel_4", "desc": "Telegram Premium Старты бота [ИИ]"},
        "3046": {"name": "🇺🇸Telegram Premium Старты бота [ИИ Поиск][США]", "price": max(_p(637.2032), 10.0), "panel": "panel_4", "desc": "Telegram Premium Старты бота [ИИ]"},
        "3047": {"name": "🇺🇦Telegram Premium Старты бота [ИИ Поиск][Украина]", "price": max(_p(637.2032), 10.0), "panel": "panel_4", "desc": "Telegram Premium Старты бота [ИИ]"},
        "3048": {"name": "🇺🇿Telegram Premium Старты бота [ИИ Поиск][Узбекистан]", "price": max(_p(637.2032), 10.0), "panel": "panel_4", "desc": "Telegram Premium Старты бота [ИИ]"},
        "3049": {"name": "🇮🇱Telegram Premium Старты бота [ИИ Поиск][Израиль]", "price": max(_p(637.2032), 10.0), "panel": "panel_4", "desc": "Telegram Premium Старты бота [ИИ]"},
        "3050": {"name": "🇮🇳Telegram Premium Старты бота [ИИ Поиск][Индия]", "price": max(_p(637.2032), 10.0), "panel": "panel_4", "desc": "Telegram Premium Старты бота [ИИ]"},
        "3051": {"name": "🇹🇷Telegram Premium Старты бота [ИИ Поиск][Турция]", "price": max(_p(637.2032), 10.0), "panel": "panel_4", "desc": "Telegram Premium Старты бота [ИИ]"},
        "3052": {"name": "🔥Telegram ИИ Подписчики [90 Дней без списаний♻️][Из Поиска]", "price": max(_p(62.4949), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики"},
        "3053": {"name": "Telegram Комментарии [Свои][Лучшая цена][Россия]", "price": max(_p(152.0), 10.0), "panel": "panel_4", "desc": "Telegram Комментарии"},
        "3059": {"name": "🔥Telegram Подписчики + Авто Просмотры [Россия] [30 дней]", "price": max(_p(438.8737), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики + Авто Просмотры"},
        "3060": {"name": "🔥Telegram Подписчики + Авто Просмотры [Россия] [60 дней]", "price": max(_p(655.7883), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики + Авто Просмотры"},
        "3061": {"name": "🔥Telegram Подписчики + Авто Просмотры [Россия] [90 дней]", "price": max(_p(918.1036), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики + Авто Просмотры"},
        "3062": {"name": "Telegram Подписчики + Авто Просмотры [Россия] [7 дней]", "price": max(_p(319.0917), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики + Авто Просмотры"},
        "3063": {"name": "Telegram Подписчики + Авто Просмотры [Россия] [14 дней]", "price": max(_p(531.8196), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики + Авто Просмотры"},
        "3064": {"name": "Telegram Подписчики + Авто Просмотры [Казахстан] [7 дней]", "price": max(_p(319.0917), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики + Авто Просмотры"},
        "3065": {"name": "Telegram Подписчики + Авто Просмотры [Казахстан] [14 дней]", "price": max(_p(531.8196), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики + Авто Просмотры"},
        "3066": {"name": "Telegram Подписчики + Авто Просмотры [Казахстан] [30 дней]", "price": max(_p(850.9113), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики + Авто Просмотры"},
        "3067": {"name": "Telegram Подписчики + Авто Просмотры [Казахстан] [60 дней]", "price": max(_p(1489.0948), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики + Авто Просмотры"},
        "3108": {"name": "Telegram Просмотры + Клики по рекламе [Ads][По ключевому слову]", "price": max(_p(30.3897), 10.0), "panel": "panel_4", "desc": "Telegram Просмотры/Клики по рекламе [Tg Ads]"},
        "3109": {"name": "🇷🇺 РУ Telegram Просмотры рекламы [Ads][По ключевому слову]", "price": max(_p(75.9742), 10.0), "panel": "panel_4", "desc": "Telegram Просмотры/Клики по рекламе [Tg Ads]"},
        "3110": {"name": "🇷🇺 РУ Telegram Просмотры рекламы [Ads][Для каналов/Ботов/Чатов]", "price": max(_p(75.9742), 10.0), "panel": "panel_4", "desc": "Telegram Просмотры/Клики по рекламе [Tg Ads]"},
        "3111": {"name": "🇺🇿 Узбекистан Telegram Просмотры рекламы [Ads][По ключевому слову]", "price": max(_p(75.9742), 10.0), "panel": "panel_4", "desc": "Telegram Просмотры/Клики по рекламе [Tg Ads]"},
        "3112": {"name": "🇺🇿 Узбекистан Telegram Просмотры рекламы [Ads][Для каналов]", "price": max(_p(75.9742), 10.0), "panel": "panel_4", "desc": "Telegram Просмотры/Клики по рекламе [Tg Ads]"},
        "3113": {"name": "🇩🇪 Германия Telegram Просмотры рекламы [Ads][По ключевому слову]", "price": max(_p(75.9742), 10.0), "panel": "panel_4", "desc": "Telegram Просмотры/Клики по рекламе [Tg Ads]"},
        "3114": {"name": "🇩🇪 Германия Telegram Просмотры рекламы [Ads][Для каналов]", "price": max(_p(75.9742), 10.0), "panel": "panel_4", "desc": "Telegram Просмотры/Клики по рекламе [Tg Ads]"},
        "3115": {"name": "🇺🇸 США Telegram Просмотры рекламы [Ads][По ключевому слову]", "price": max(_p(75.9742), 10.0), "panel": "panel_4", "desc": "Telegram Просмотры/Клики по рекламе [Tg Ads]"},
        "3116": {"name": "🇺🇸 США Telegram Просмотры рекламы [Ads][Для каналов]", "price": max(_p(75.9742), 10.0), "panel": "panel_4", "desc": "Telegram Просмотры/Клики по рекламе [Tg Ads]"},
        "3145": {"name": "Telegram Подписчики в группу [Без списаний]", "price": max(_p(57.6138), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики (Продвижение групп)"},
        "3146": {"name": "🌟🤖Telegram Запуск бота Premium Аккаунты [Ежедневный рестарт]", "price": max(_p(379.8711), 10.0), "panel": "panel_4", "desc": "Telegram Premium Старты бота"},
        "3158": {"name": "Telegram Premium Старты бота [Только номера +79..]", "price": max(_p(483.0327), 10.0), "panel": "panel_4", "desc": "Telegram Premium Старты бота [Россия]"},
        "3216": {"name": "Telegram Буст канала [30 Дней] [Стабильные]⚡️", "price": max(_p(20276.1314), 10.0), "panel": "panel_4", "desc": "Telegram Бусты"},
        "3217": {"name": "Telegram Старты Приложения [Mini APP]", "price": max(_p(1461.0148), 10.0), "panel": "panel_4", "desc": "Telegram Старты бота"},
        "3218": {"name": "Telegram Запуск бота + активность [Читайте описание]", "price": max(_p(50240.0), 10.0), "panel": "panel_4", "desc": "Telegram Старты бота"},
        "3219": {"name": "Запуск бота [Принимает реферальный код]", "price": max(_p(7.98), 10.0), "panel": "panel_4", "desc": "Telegram Старты бота"},
        "3221": {"name": "Telegram Подписчики [1 День без списаний♻️]", "price": max(_p(5.3672), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики"},
        "3223": {"name": "🔥[Акция] Telegram Подписчики [Без списаний]", "price": max(_p(19.3612), 10.0), "panel": "panel_4", "desc": "Telegram Подписчики"},
        "3224": {"name": "Telegram Комментарии [Случайные+Смайлы][Россия]", "price": max(_p(320.0), 10.0), "panel": "panel_4", "desc": "Telegram Комментарии"},
        "3225": {"name": "Telegram Комментарии [Свои] [Сервер 2]", "price": max(_p(400.0), 10.0), "panel": "panel_4", "desc": "Telegram Комментарии"},
        "3243": {"name": "Telegram Буст канала [15 Дней] [Лучшая цена]⚡️", "price": max(_p(8373.5031), 10.0), "panel": "panel_4", "desc": "Telegram Бусты"},
        "3244": {"name": "Telegram Буст канала [30 Дней] [Лучшая цена]⚡️", "price": max(_p(14737.3654), 10.0), "panel": "panel_4", "desc": "Telegram Бусты"},
        "3245": {"name": "Telegram Premium Подписчики [30 Дней][Лимит 10000]", "price": max(_p(390.8179), 10.0), "panel": "panel_4", "desc": "Telegram Premium Подписчики"},
        "3246": {"name": "Telegram Premium Подписчики [15 Дней][0% Дропа]", "price": max(_p(521.5263), 10.0), "panel": "panel_4", "desc": "Telegram Premium Подписчики"},
        "3247": {"name": "Telegram Premium Подписчики [7 Дней][0% Дропа]", "price": max(_p(274.4875), 10.0), "panel": "panel_4", "desc": "Telegram Premium Подписчики"},
        "3248": {"name": "Telegram Premium Подписчики [45 Дней][0% Дропа]", "price": max(_p(1137.1626), 10.0), "panel": "panel_4", "desc": "Telegram Premium Подписчики"},
        "3249": {"name": "Telegram Premium Подписчики [60 Дней][0% Дропа]", "price": max(_p(1437.7917), 10.0), "panel": "panel_4", "desc": "Telegram Premium Подписчики"},
        "3250": {"name": "Telegram Premium Подписчики [90 Дней][0% Дропа]", "price": max(_p(1900.4993), 10.0), "panel": "panel_4", "desc": "Telegram Premium Подписчики"},
        "3251": {"name": "Telegram Premium Подписчики [20 Дней][0% Дропа]", "price": max(_p(640.4709), 10.0), "panel": "panel_4", "desc": "Telegram Premium Подписчики"},
        "3252": {"name": "Telegram Premium Подписчики [30 Дней][0% Дропа]", "price": max(_p(782.943), 10.0), "panel": "panel_4", "desc": "Telegram Premium Подписчики"},
        "3255": {"name": "Telegram Premium Подписчики [7 Дней][Гарантия]", "price": max(_p(236.7455), 10.0), "panel": "panel_4", "desc": "Telegram Premium Подписчики"},
        "3256": {"name": "Telegram Premium Подписчики [10 Дней][Гарантия]", "price": max(_p(227.0178), 10.0), "panel": "panel_4", "desc": "Telegram Premium Подписчики"},
        "3257": {"name": "Telegram Premium Подписчики [15 Дней][Гарантия]", "price": max(_p(394.5758), 10.0), "panel": "panel_4", "desc": "Telegram Premium Подписчики"},
        "3258": {"name": "Telegram Premium Подписчики [25 Дней][Гарантия]", "price": max(_p(526.1011), 10.0), "panel": "panel_4", "desc": "Telegram Premium Подписчики"},
        "3259": {"name": "Telegram Premium Подписчики [45 Дней][Гарантия]", "price": max(_p(599.3343), 10.0), "panel": "panel_4", "desc": "Telegram Premium Подписчики"},
        "3262": {"name": "Telegram Premium Онлайн Подписчики [7 Дней][Гарантия]", "price": max(_p(389.6696), 10.0), "panel": "panel_4", "desc": "Telegram Premium Подписчики"},
        "3263": {"name": "Telegram Premium Онлайн Подписчики [14 Дней][Гарантия]", "price": max(_p(589.0355), 10.0), "panel": "panel_4", "desc": "Telegram Premium Подписчики"},
        "3264": {"name": "Telegram Premium Онлайн Подписчики [20 Дней][Гарантия]", "price": max(_p(860.8981), 10.0), "panel": "panel_4", "desc": "Telegram Premium Подписчики"},
        "3265": {"name": "Telegram Premium Онлайн Подписчики [28 Дней][Гарантия]", "price": max(_p(933.3947), 10.0), "panel": "panel_4", "desc": "Telegram Premium Подписчики"},
        "3266": {"name": "Telegram Premium Онлайн Подписчики [35 Дней][Гарантия]", "price": max(_p(1042.1398), 10.0), "panel": "panel_4", "desc": "Telegram Premium Подписчики"},
    },
    # ============ VEXBOOST — INSTAGRAM ============
    "instagram": {
        "title": "📸 INSTAGRAM",
        "items": {
            "vex_ig_subs_30d_10": {"name": "👥 Подписчики [30 Дней] [10% Списаний]", "id": "2295", "price": round(196.06 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Списания 10%"},
            "vex_ig_subs_mobile": {"name": "👥 Подписчики [Реальные] [С Мобильного]", "id": "2562", "price": round(319.46 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Списания 5-12%"},
            "vex_ig_subs_30d_mix": {"name": "👥 Подписчики [30 Дней] [Реальные+Микс]", "id": "3099", "price": round(289.80 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Быстрые"},
            "vex_ig_subs_365": {"name": "👥 Подписчики [365 Дней♻️]", "id": "2643", "price": round(516.30 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "365 дней гарантии"},
            "vex_ig_subs_no_guar_20_70": {"name": "👥 Подписчики [Без гарантии] [20-70%]", "id": "3254", "price": round(23.61 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Списания 20-70%"},
            "vex_ig_subs_no_guar_10_20": {"name": "👥 Подписчики [Без гарантии] [10-20%]", "id": "3027", "price": round(52.12 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Списания 10-20%"},
            "vex_ig_subs_new_profiles": {"name": "👥 Подписчики [Новые профили]", "id": "3027", "price": round(23.61 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Списания 40-90%"},
            "vex_ig_subs_live_ru": {"name": "🇷🇺 Подписчики [Россия] [Живые]", "id": "3008", "price": round(2369.64 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Живые"},
            "vex_ig_subs_old_profiles": {"name": "👥 Подписчики [Старые профили]", "id": "2643", "price": round(516.30 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Списания 40-90%"},
            "vex_ig_subs_priority": {"name": "⚡🌟 Подписчики [Авто-Восстановление 30] [Приоритет]", "id": "3285", "price": round(392.13 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Списания до 45%"},
            "vex_ig_subs_5_days_arab": {"name": "🇸🇦 Подписчики [Арабы][Гарантия 30♻️]", "id": "2763", "price": round(325.46 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Подписчики из Арабских стран"},
            "vex_ig_subs_5_days_asia": {"name": "🇮🇩🇹🇭 Подписчики [Азия][Гарантия 30♻️]", "id": "2764", "price": round(325.46 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Подписчики из Индонезии, Таиланда"},
            "vex_ig_subs_5_days_europe": {"name": "🇪🇺 Подписчики [Европа][Гарантия 30♻️]", "id": "2765", "price": round(325.46 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Подписчики из Европы"},
            "vex_ig_subs_5_days_turkey": {"name": "🇹🇷 Подписчики [Турция][Гарантия 30♻️]", "id": "2766", "price": round(325.46 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Подписчики из Турции"},
            "vex_ig_subs_5_days_usa": {"name": "🇺🇸 Подписчики [США][Гарантия 30♻️]", "id": "2767", "price": round(378.60 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Подписчики из США/Канады"},
            "vex_ig_subs_india": {"name": "🇮🇳 Подписчики [Индия]", "id": "2768", "price": round(222.20 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Подписчики из Индии"},
            
            "vex_ig_likes_ru_live": {"name": "❤️ Лайки [Россия]", "id": "2566", "price": round(358.01 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Моментальный старт"},
            "vex_ig_likes_30k_hour": {"name": "❤️ Лайки [30000 в час]", "id": "2420", "price": round(26.95 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Списания 0-5%"},
            "vex_ig_likes_30d_0": {"name": "❤️ Лайки [30 Дней] [0% Списаний]", "id": "2529", "price": round(10.78 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Аккаунты с аватарками"},
            "vex_ig_likes_no_guar_cheap": {"name": "❤️ Лайки [Без гарантии] [Лучшая цена]", "id": "2584", "price": round(11.76 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Без гарантии"},
            "vex_ig_likes_no_guar": {"name": "❤️ Лайки [Без гарантии]", "id": "2584", "price": round(11.76 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Низкое качество"},
            "vex_ig_likes_live_ru": {"name": "❤️ Лайки [РУ+СНГ] [Живые]", "id": "2762", "price": round(192.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Русские женские"},
            "vex_ig_likes_365": {"name": "❤️ Лайки [365 Дней гарантии]", "id": "2565", "price": round(20.21 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Кнопки восстановления"},
            "vex_ig_likes_india": {"name": "🇮🇳 Лайки [Индия] [10000/Сутки]", "id": "2769", "price": round(41.82 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Лайки Индия"},
            "vex_ig_likes_turkey": {"name": "🇹🇷 Лайки [Турция] [1000/Сутки]", "id": "2770", "price": round(77.11 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Лайки Турция"},
            "vex_ig_likes_usa": {"name": "🇺🇸 Лайки [США]", "id": "2771", "price": round(129.40 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Лайки США"},
            
            "vex_ig_views_video": {"name": "👁 Просмотры видео [Все ссылки]", "id": "2411", "price": 17.0, "pack": 1000, "panel": "panel_4", "desc": "Лучшая цена"},
            "vex_ig_views_video_fast": {"name": "👁 Просмотры видео [Быстрые]", "id": "1694", "price": round(14 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "0 списаний"},
            "vex_ig_views_video_stable": {"name": "👁 Просмотры видео [Стабильные]", "id": "2423", "price": round(14 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Всегда стабильные"},
            "vex_ig_views_video_reach": {"name": "👁 Просмотры видео + Охваты", "id": "2424", "price": round(14 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Вместе с просмотрами поступает охват"},
            "vex_ig_views_photo": {"name": "👁 Просмотры Фото [Карусель + Охваты]", "id": "2776", "price": round(16 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Для постов с фото или каруселью"},
            "vex_ig_profile_visits": {"name": "📊 Посещения профиля", "id": "3242", "price": round(4.64 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Переходы в профиль"},
            "vex_ig_story_views": {"name": "👀 Просмотры сторис [Живые][Россия]", "id": "3220", "price": round(1240.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Живые, Россия"},
            "vex_ig_story_views_all": {"name": "👀 Просмотры сторис [Всех]", "id": "3284", "price": round(9.4355 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Указывайте ссылку на профиль"},
            "vex_ig_saves": {"name": "💾 Сохранения [Быстрый старт]", "id": "991", "price": round(1.9770 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Для публичных профилей"},
            "vex_ig_repost": {"name": "🔄 Поделиться [Репост]", "id": "2298", "price": round(1.3929 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Качество: Микс"},
            "vex_ig_reach_post": {"name": "📊 Охват + Показы [Плавно]", "id": "2299", "price": round(5.6981 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Быстрый старт, плавная накрутка"},
            
            "vex_ig_comments_custom": {"name": "💬 Комментарии [Свои]", "id": "2302", "price": round(60.65 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Микс юзеры"},
            "vex_ig_comments_custom_hq": {"name": "💬 Комментарии [Свои] [Высокое качество]", "id": "2303", "price": round(1772.73 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Быстрая накрутка"},
            "vex_ig_comments_real_custom": {"name": "💬 Комментарии реальные [Свои]", "id": "3240", "price": round(957.95 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Свои, реальные"},
            "vex_ig_comments_real_ru": {"name": "💬 Комментарии реальные [Россия]", "id": "3238", "price": round(966.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Россия, реальные"},
            "vex_ig_comments_random": {"name": "💬 Комментарии реальные [Случайные]", "id": "3239", "price": round(644.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Случайные"},
            "vex_ig_smiles": {"name": "😊 Смайлики [Позитивные]", "id": "3241", "price": round(885.50 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "От разных людей"}
        }
    },

    # ============ VEXBOOST — YOUTUBE ============
    "youtube": {
        "title": "▶️ YOUTUBE",
        "items": {
            "vex_yt_subs_cheap": {"name": "👥 Подписчики [Лучшая цена]", "id": "2276", "price": round(3.0586 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Списания до 100%"},
            "vex_yt_subs_30d_250": {"name": "👥 Подписчики [30 Дней гарантии]", "id": "2945", "price": round(3797.44 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Скорость до 250/сутки"},
            "vex_yt_subs_real_100": {"name": "👥 Подписчики [Реальные] [100/День]", "id": "2332", "price": round(3919.94 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Пожизненная гарантия"},
            "vex_yt_subs_real_300": {"name": "👥 Подписчики [Реальные] [300/День]", "id": "2333", "price": round(4573.48 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Из поиска YouTube"},
            "vex_yt_subs_real_1500": {"name": "👥 Подписчики [Реальные][1500 в день]", "id": "2944", "price": round(5243.45 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Пожизненная гарантия"},
            "vex_yt_subs_ru_lifetime": {"name": "🇷🇺 Русские подписчики [Пожизненная гарантия]", "id": "3104", "price": round(5998.50 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Пожизненная гарантия"},
            
            "vex_yt_likes_shorts": {"name": "❤️ Лайки на Shorts [Моментальный старт]", "id": "2257", "price": round(71.37 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Бонус до 150%"},
            "vex_yt_likes_comments": {"name": "❤️ Лайки на комментарий [Видео/Шортс]", "id": "2375", "price": round(148.27 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Указывать ссылку на комментарий"},
            "vex_yt_likes_real": {"name": "❤️ Лайки [Реальные] [+100% Просмотров]", "id": "2334", "price": round(443.18 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Из поиска Гугл"},
            "vex_yt_likes_fast": {"name": "❤️ Лайки [Быстрые][Гарантия 30 дней]", "id": "1909", "price": round(301.04 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "До 50000 за 24 часа"},
            "vex_yt_likes_real_30d": {"name": "❤️ Лайки [Реальные][Гарантия 30 дней]", "id": "2409", "price": round(496.70 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "На данный момент без списаний"},
            "vex_yt_likes_crypto_nft": {"name": "❤️ Лайки [Crypto/NFT] [Гарантия 30♻️]", "id": "2937", "price": round(55 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Реальные, тематика"},
            "vex_yt_likes_crypto_365": {"name": "❤️ Лайки [Crypto] [Гарантия 365♻️]", "id": "2936", "price": round(103 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Реальные, 365 дней"},
            
            "vex_yt_views_shorts": {"name": "👀 Просмотры Shorts [Без списаний]", "id": "2335", "price": round(151.95 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Пожизненная гарантия"},
            "vex_yt_views_10k": {"name": "👀 Просмотры [Скорость 10к/День]", "id": "2943", "price": round(78.43 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Гарантия 30 дней"},
            "vex_yt_views_auto": {"name": "👀 Просмотры [1-2к/День] [Авто-восстановление]", "id": "2274", "price": round(96.19 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Гарантия 30 дней"},
            "vex_yt_views_1k": {"name": "👀 Просмотры [Скорость 1к/День] [Гарантия 30 дней]", "id": "1692", "price": round(83.49 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Гарантия 30 дней"},
            "vex_yt_views_200_500": {"name": "👀 Просмотры [200-500/день] [Без списаний]", "id": "3105", "price": round(56.86 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Гарантия 60 дней"},
            "vex_yt_views_365": {"name": "🇷🇺 Просмотры [RU+СНГ] [Гарантия 365♻️]", "id": "3103", "price": round(37.82 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Из внешних источников"},
            "vex_yt_views_ru_2k": {"name": "🇷🇺 Просмотры [Скорость 2000-3000] [СНГ]", "id": "1907", "price": round(99.80 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Гарантия 60 дней"},
            "vex_yt_views_ru_live": {"name": "🇷🇺 Живые просмотры [Рекомендации + внешние]", "id": "1997", "price": round(131.75 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Гарантия 180 дней"},
            "vex_yt_views_no_guar_2k": {"name": "👀 Просмотры [Скорость 2к/День] [Без гарантии]", "id": "2451", "price": round(55.71 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Претензии не принимаются"},
            "vex_yt_views_unique": {"name": "👀 Просмотры [Уникальные - реальные]", "id": "1657", "price": round(326.09 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "90-дневная гарантия"},
            "vex_yt_views_native_2k": {"name": "👀 Нативные Просмотры [От 2000]", "id": "2938", "price": round(73.45 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Пожизненная гарантия"},
            "vex_yt_views_native_3k": {"name": "👀 Нативные Просмотры [От 3000]", "id": "2939", "price": round(72.12 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Пожизненная гарантия"},
            "vex_yt_views_native_5k": {"name": "👀 Нативные Просмотры [От 5000]", "id": "2940", "price": round(68.81 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Пожизненная гарантия"},
            "vex_yt_views_native_10k": {"name": "👀 Нативные Просмотры [От 10000]", "id": "2941", "price": round(66.16 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Пожизненная гарантия"},
            
            "vex_yt_viewers_15m": {"name": "👥 Зрители [15 Мин] [Дешевые]", "id": "3208", "price": round(9.46 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Быстрый старт"},
            "vex_yt_viewers_30m": {"name": "👥 Зрители [30 Мин] [Дешевые]", "id": "3209", "price": round(18.93 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Быстрый старт"},
            "vex_yt_viewers_60m": {"name": "👥 Зрители [60 Мин] [Дешевые]", "id": "3210", "price": round(37.86 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Умеренный старт"},
            "vex_yt_viewers_90m": {"name": "👥 Зрители [90 Мин] [Дешевые]", "id": "3211", "price": round(56.79 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Дешевые"},
            "vex_yt_viewers_120m": {"name": "👥 Зрители [120 Мин] [Дешевые]", "id": "3212", "price": round(75.72 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Дешевые"},
            "vex_yt_viewers_150m": {"name": "👥 Зрители [150 Мин] [Дешевые]", "id": "3213", "price": round(94.65 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Дешевые"},
            "vex_yt_viewers_180m": {"name": "👥 Зрители [180 Мин] [Дешевые]", "id": "3214", "price": round(113.58 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Дешевые"},
            "vex_yt_viewers_300m": {"name": "👥 Зрители [300 Мин] [Дешевые]", "id": "3215", "price": round(189.30 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Дешевые"},
            
            "vex_yt_reposts_50": {"name": "🔁 Репосты в соц. сетях [~50/День]", "id": "1616", "price": round(122.28 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Пожизненная гарантия"},
            "vex_yt_reposts_100": {"name": "🔁 Репосты в соц. сетях [~100/День]", "id": "1617", "price": round(122.28 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Пожизненная гарантия"},
            "vex_yt_reposts_250": {"name": "🔁 Репосты в соц. сетях [~250/День]", "id": "1618", "price": round(122.28 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Пожизненная гарантия"},
            "vex_yt_reposts_750": {"name": "🔁 Репосты в соц. сетях [~750/День]", "id": "1619", "price": round(122.28 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Пожизненная гарантия"},
                        "vex_yt_reposts_1500": {"name": "🔁 Репосты в соц. сетях [~1500/День]", "id": "1620", "price": round(122.28 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Пожизненная гарантия"},
            "vex_yt_reposts_3000": {"name": "🔁 Репосты в соц. сетях [~3000/День]", "id": "1621", "price": round(122.28 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Пожизненная гарантия"},
            
            "vex_yt_hours_3m": {"name": "⏳ Часы просмотров [Видео 3+ минут]", "id": "2336", "price": round(758.48 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Пожизненная гарантия"},
            "vex_yt_hours_5m": {"name": "⏳ Часы просмотров [Видео 5+ минут]", "id": "2337", "price": round(1253.57 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Пожизненная гарантия"},
            "vex_yt_hours_15m": {"name": "⏳ Часы просмотров [Видео 15+ минут]", "id": "2338", "price": round(2393.19 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Пожизненная гарантия"},
            
            "vex_yt_search_boost": {"name": "🔝 Поисковой прогрев [Вывод в ТОП]", "id": "3161", "price": round(3596000.00 * 1.35, 2), "pack": 1, "panel": "panel_4", "desc": "За 1 видео"},
            "vex_yt_recommended": {"name": "🔝 Вывод в рекомендованные", "id": "3160", "price": round(2356000.00 * 1.35, 2), "pack": 1, "panel": "panel_4", "desc": "За 1 видео"},
            "vex_yt_dislikes": {"name": "👎 Дизлайки [Офферы СНГ]", "id": "1911", "price": round(638.60 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Гео: СНГ"}
        }
    },

    # ============ VEXBOOST — VK ============
    "vk": {
        "title": "🅱️ ВКОНТАКТЕ",
        "items": {
            "vex_vk_subs_group": {"name": "👥 Подписчики в группу [Моментальный старт]", "id": "1119", "price": round(39.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Крупные списания"},
            "vex_vk_subs_premium": {"name": "👥 Подписчики Премиум Живые [Гарантия 90 дней♻️]", "id": "1797", "price": round(2600.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Без списаний"},
            "vex_vk_subs_live_group": {"name": "👥 Подписчики [Живые в группу]", "id": "1798", "price": round(1016.40 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Боты и дропы: не более 5–15%"},
            "vex_vk_subs_live_friends": {"name": "👥 Подписчики [Живые в друзья]", "id": "1799", "price": round(500.50 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Боты и дропы: не более 5–15%"},
            "vex_vk_subs_ai_group": {"name": "🤖 VK ИИ Подписчики [Группа]", "id": "3235", "price": round(152.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Минимум собачек"},
            "vex_vk_subs_ai_friends": {"name": "🤖 VK ИИ Подписчики [Друзья]", "id": "3236", "price": round(152.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Минимум собачек"},
            "vex_vk_subs_small_dogs": {"name": "👥 Подписчики [Маленький процент собачек]", "id": "2784", "price": round(248.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Запуск в течение 30 минут"},
            "vex_vk_subs_groups_pages": {"name": "👥 Подписчики для групп и страниц", "id": "2785", "price": round(116.22 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Редко бывают списания и собачки"},
            "vex_vk_subs_cis_small_dogs": {"name": "👥 Подписчики [СНГ] [Маленький процент собачек]", "id": "2090", "price": round(271.25 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Возможны небольшие дропы"},
            "vex_vk_subs_12d": {"name": "👥 Подписчики в группу [СНГ] [Гарантия 12 дней]", "id": "2327", "price": round(75.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Возможны отписки/списания"},
            
            "vex_vk_likes_fast": {"name": "❤️ Лайки [Быстрые] [Фото/Видео/Клипы]", "id": "3144", "price": round(123.80 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Скорость до 1000 в сутки"},
            "vex_vk_likes_live": {"name": "❤️ Живые Лайки [СНГ] [Быстрые]", "id": "1801", "price": round(82.50 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Без ботов, списаний нет"},
            "vex_vk_likes_mix": {"name": "❤️ Лайки на посты [Россия + Азия] [Быстрые]", "id": "2787", "price": round(29.05 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Возможны собачки"},
            "vex_vk_likes_bots": {"name": "❤️ Лайки на посты [СНГ] [Быстрые]", "id": "2783", "price": round(116.64 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Боты"},
            "vex_vk_likes_ugly": {"name": "❤️ Живые Красивые лайки [Быстрые]", "id": "2782", "price": round(226.80 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Лайки от живых пользователей"},
            "vex_vk_likes_slow": {"name": "❤️ Лайки на посты [Медленные]", "id": "1722", "price": round(18.94 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Боты, возможен очень долгий старт"},
            
            "vex_vk_views_fast": {"name": "👀 Просмотры Видео и Клипов [Мгновенные]", "id": "2663", "price": round(5.43 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Скорость до 1.5 млн в сутки"},
            "vex_vk_views_hold_5m": {"name": "👀 Просмотры Видео и Клипов [Удержание 5 минут]", "id": "2664", "price": round(10.54 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Мгновенные просмотры ВК"},
            "vex_vk_views_hold_10m": {"name": "👀 Просмотры Видео и Клипов [Удержание 10 минут]", "id": "2665", "price": round(15.81 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Мгновенные просмотры ВК"},
            "vex_vk_views_hold_30m": {"name": "👀 Просмотры Видео и Клипов [Удержание 30 минут]", "id": "2666", "price": round(19.76 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Мгновенные просмотры ВК"},
            "vex_vk_views_post_ru": {"name": "👀 Просмотр на пост [Россия]", "id": "2756", "price": round(6.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Просматривают посты из России"},
            "vex_vk_views_post_real_ru": {"name": "👀 Просмотр на пост [Реальные Россия]", "id": "1802", "price": round(14.32 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Старт в течение 5 минут"},
            "vex_vk_views_post_mix": {"name": "👀 Просмотр на пост [Микс]", "id": "2382", "price": round(0.15 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Скорость до 30000 в сутки"},
            "vex_vk_views_video": {"name": "👀 Просмотры на видео [Средняя скорость]", "id": "1803", "price": round(0.50 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "До 20 000 за 24 часа"},
            "vex_vk_views_clips": {"name": "👀 Просмотры на клипы [Средняя скорость]", "id": "1804", "price": round(0.50 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "До 20 000 за 24 часа"},
            "vex_vk_views_auto": {"name": "👀 Авто-просмотры [Глазик] - на новые посты 30 дней", "id": "1805", "price": round(46.20 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "До 80 000 за 24 часа"},
            "vex_vk_views_music": {"name": "👀 Прослушивание на плейлисты / альбом", "id": "1806", "price": round(8.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "До 30 000 за 24 часа"},
            "vex_vk_views_goods": {"name": "👀 Просмотры на товары / услуги [Быстрые]", "id": "2755", "price": round(0.50 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Скорость ~ 50к/сутки"},
            "vex_vk_views_visits": {"name": "👀 Посещение Группы/Страницы", "id": "2124", "price": round(3.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Скорость до 5000 в сутки"},
            "vex_vk_views_video_ru": {"name": "👀 Просмотры Видео и Клипов [Мгновенные][Россия]", "id": "3271", "price": round(6.60 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Скорость до 300000 в сутки"},
            
            "vex_vk_reposts_fast": {"name": "🔁 Репосты [Быстрые] [Большая база]", "id": "3237", "price": round(136.80 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Русское оформление"},
            "vex_vk_reposts_cis_fast": {"name": "🔁 Репосты СНГ + Микс [Быстрые]", "id": "2091", "price": round(232.50 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Без дропов"},
            "vex_vk_reposts_slow": {"name": "🔁 Репосты [Медленные]", "id": "2342", "price": round(63.31 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Скорость 50-300 в сутки"},
            
            "vex_vk_polls_live": {"name": "📊 Голоса в Опрос [Живые]", "id": "1444", "price": round(545.10 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Старт до 30 минут"},
            "vex_vk_polls_slow": {"name": "📊 Голоса в опрос [Медленные]", "id": "2331", "price": round(67.40 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Скорость 50-200 в сутки"},
            
            "vex_vk_comments_custom": {"name": "💬 Комментарии Кастомные [Россия]", "id": "3185", "price": round(750.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Запуск: до 30 мин"},
            "vex_vk_comments_custom_m": {"name": "💬 Комментарии [Мужской пол]", "id": "3184", "price": round(750.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Мужские"},
            "vex_vk_comments_custom_f": {"name": "💬 Комментарии [Женский пол]", "id": "3183", "price": round(750.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Женские"},
            "vex_vk_comments_positive": {"name": "💬 Комментарии [Россия] [Положительные]", "id": "3186", "price": round(750.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Положительные"},
            "vex_vk_likes_comments_bots": {"name": "❤️ Лайки на комментарий [Боты]", "id": "3187", "price": round(63.55 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "До 300 за сутки"},
            "vex_vk_likes_comments_live": {"name": "❤️ Лайки на комментарий [Живые]", "id": "3188", "price": round(1240.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "До 1000 лайков в день"},
            "vex_vk_likes_comments": {"name": "❤️ Лайки на комментарий", "id": "2586", "price": round(98.31 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Скорость до 2000 в сутки"},
            
            "vex_vk_play_viewers_1h": {"name": "👥 VK Play Зрители на 1 час", "id": "1829", "price": round(353.16 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "VK Play"},
            "vex_vk_play_viewers_2h": {"name": "👥 VK Play Зрители на 2 часа", "id": "1830", "price": round(706.34 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "VK Play"},
            "vex_vk_play_viewers_3h": {"name": "👥 VK Play Зрители на 3 часа", "id": "1831", "price": round(1059.51 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "VK Play"},
            "vex_vk_play_viewers_4h": {"name": "👥 VK Play Зрители на 4 часа", "id": "1832", "price": round(1412.68 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "VK Play"},
            "vex_vk_play_subs": {"name": "👥 VK Play Подписчики [Гарантия 30 дней]", "id": "1833", "price": round(28252.15 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "VK Play"}
        }
    },

    # ============ VEXBOOST — TWITTER (X) ============
    "twitter": {
        "title": "🐦 TWITTER (X)",
        "items": {
            "vex_twt_subs": {"name": "👥 Подписчики [Без гарантии] [Лучшая цена]", "id": "1664", "price": round(91.66 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Возможен долгий старт"},
            "vex_twt_subs_ai": {"name": "🚀 Подписчики [AI + Гарантия]", "id": "1667", "price": round(928.03 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Медленные, Новый алгоритм AI"},
            "vex_twt_subs_us_uk_es": {"name": "👥 Подписчики [US / UK / ES] [Гарантия 30 Дней]", "id": "1695", "price": round(1259.17 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Скорость: В день до 3к"},
            "vex_twt_subs_live": {"name": "👥 Подписчики [Живые] [до 1000/сутки]", "id": "3174", "price": round(5444.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Списания: 10-15%"},
            "vex_twt_subs_avg": {"name": "👥 Подписчики [Средняя скорость] [до 100/сутки]", "id": "3175", "price": round(1799.63 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Гарантия 30 дней"},
            "vex_twt_subs_fast": {"name": "👥 Подписчики [Быстрый старт] [до 5-10к/сутки]", "id": "3176", "price": round(1879.33 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Возможны высокие списания!"},
            "vex_twt_subs_usa_mix": {"name": "🇺🇸 Подписчики [Профили США + Микс]", "id": "3177", "price": round(1073.33 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Скорость: до 2к/сутки"},
            "vex_twt_subs_usa_real": {"name": "🇺🇸 Подписчики [США] [Реальные]", "id": "3178", "price": round(15262.19 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Гарантия 30 дней"},
            "vex_twt_subs_japan_real": {"name": "🇯🇵 Подписчики [Япония] [Реальные]", "id": "3179", "price": round(14735.90 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Гарантия 30 дней"},
            "vex_twt_subs_korea_real": {"name": "🇰🇷 Подписчики [Южная Корея] [Реальные]", "id": "3180", "price": round(14735.90 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Гарантия 30 дней"},
            "vex_twt_subs_turkey_real": {"name": "🇹🇷 Подписчики [Турция] [Реальные]", "id": "3181", "price": round(14735.90 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Гарантия 30 дней"},
            "vex_twt_subs_blue": {"name": "👥 Подписчики [Аккаунты с синей галочкой]", "id": "3162", "price": round(75227.41 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Гарантия 30 дней"},
            "vex_twt_subs_blue_no_guar": {"name": "👥 Подписчики [Синяя галочка] [Без гарантии]", "id": "3163", "price": round(37613.70 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Сервер #2"},
            "vex_twt_subs_7d": {"name": "👥 Подписчики [Гарантия 7 дней♻️]", "id": "3269", "price": round(377.42 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Возможен долгий старт"},
            "vex_twt_subs_live_ru": {"name": "🇷🇺 Живые подписчики [Россия]", "id": "3268", "price": round(643.50 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "До 90% пользователей из РФ"},
            "vex_twt_subs_nft_blue": {"name": "👥 NFT Подписчики [Синяя галочка] [Низкие списания]", "id": "3172", "price": round(33597.27 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Без гарантии"},
            
            "vex_twt_likes": {"name": "❤️ Лайки [Быстрый старт]", "id": "1665", "price": round(404.38 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Гарантия 30"},
            "vex_twt_likes_fast": {"name": "❤️ Лайки [Гарантия 30 Дней] [Быстрые]", "id": "1696", "price": round(323.50 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Быстрый старт"},
            "vex_twt_likes_30d": {"name": "❤️ Лайки [Гарантия 30♻️] [20-30%]", "id": "1675", "price": round(201.33 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Списания до 30%"},
            "vex_twt_likes_no_guar": {"name": "❤️ Лайки [Без Гарантии] [Лучшая цена]", "id": "2426", "price": round(79.77 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Списания до 30%"},
            "vex_twt_likes_blue": {"name": "❤️ Лайки [Аккаунты с синей галочкой]", "id": "3164", "price": round(16798.64 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Без гарантии"},
                        "vex_twt_likes_live_ru": {"name": "🇷🇺 Живые лайки [Россия]", "id": "3270", "price": round(643.50 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Запуск до часа"},
            
            "vex_twt_retweets": {"name": "🔁 Ретвиты [Лучшая цена] [Гарантия 30 Дней]", "id": "1668", "price": round(1040.87 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Высокое качество аккаунтов"},
            "vex_twt_retweets_min_drop": {"name": "🔁 Ретвиты [Минимум списаний] [Гарантия 30 Дней]", "id": "2436", "price": round(876.15 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Скорость до 5000 в сутки"},
            "vex_twt_retweets_blue": {"name": "🔁 Ретвиты [Аккаунты с синей галочкой]", "id": "3165", "price": round(20998.29 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Без гарантии"},
            
            "vex_twt_views": {"name": "👀 Просмотры [Без списаний]", "id": "1669", "price": round(0.5032 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Старт моментальный"},
            "vex_twt_views_video": {"name": "👀 Просмотры видео [Быстрые]", "id": "1671", "price": round(0.5065 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Быстрый старт"},
            "vex_twt_views_no_over": {"name": "👀 Просмотры на твит/видео [Без перекрута]", "id": "2564", "price": round(0.0784 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Без перекрута"},
            
            "vex_twt_comments_korea": {"name": "💬 Случайные комментарии [Корея]", "id": "2427", "price": round(6257.74 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "100% Органическая услуга"},
            "vex_twt_comments_japan": {"name": "💬 Случайные комментарии [Япония]", "id": "2428", "price": round(6257.74 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "100% Органическая услуга"},
            "vex_twt_comments_germany": {"name": "💬 Случайные комментарии [Германия]", "id": "2429", "price": round(6257.74 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "100% Органическая услуга"},
            "vex_twt_comments_france": {"name": "💬 Случайные комментарии [Франция]", "id": "2430", "price": round(6424.89 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "100% Органическая услуга"},
            "vex_twt_comments_arab": {"name": "💬 Случайные комментарии [Арабские]", "id": "2431", "price": round(6257.74 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "100% Органическая услуга"},
            "vex_twt_comments_russia": {"name": "💬 Случайные комментарии [Россия]", "id": "2432", "price": round(6257.74 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "100% Органическая услуга"},
            "vex_twt_comments_portugal": {"name": "💬 Случайные комментарии [Португалия]", "id": "2433", "price": round(6424.89 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "100% Органическая услуга"},
            "vex_twt_comments_spain": {"name": "💬 Случайные комментарии [Испания]", "id": "2434", "price": round(6424.89 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "100% Органическая услуга"},
            "vex_twt_comments_custom_blue": {"name": "💬 Кастомные комментарии [Синяя галочка]", "id": "3166", "price": round(27997.73 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Без гарантии"},
            "vex_twt_comments_ai_blue": {"name": "💬 ИИ Комментарии [Синяя галочка]", "id": "3167", "price": round(30797.50 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Без гарантии"}
        }
    },

    # ============ VEXBOOST — FACEBOOK ============
    "facebook": {
        "title": "📘 FACEBOOK",
        "items": {
            "vex_fb_subs_fast": {"name": "👥 Подписчики [До 2к/сутки]", "id": "1360", "price": round(20.13 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Гарантия 30 Дней"},
            "vex_fb_subs_more": {"name": "👥 Подписчики [Гарантия 30 Дней]", "id": "1361", "price": round(99.39 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Для страницы/профиля"},
            "vex_fb_likes_page": {"name": "❤️ Лайки на страницу 30🔥♻️", "id": "1243", "price": round(188.71 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Лайки на Профиль / Страницу"},
            "vex_fb_likes_fast": {"name": "❤️ Лайки на пост [Моментально] [30к/день]", "id": "1364", "price": round(35.23 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Моментально"},
            "vex_fb_likes_hq": {"name": "❤️ Лайки на пост [Высокое качество]", "id": "1365", "price": round(33.34 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Без списаний"},
            "vex_fb_react_like": {"name": "👍 Реакция на пост [👍]", "id": "1368", "price": round(51.58 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Реакции"},
            "vex_fb_react_heart": {"name": "❤️ Реакция на пост [❤️]", "id": "1369", "price": round(51.58 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Реакции"},
            "vex_fb_react_hug": {"name": "🤗 Реакция на пост [🤗]", "id": "1370", "price": round(51.58 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Реакции"},
            "vex_fb_views_video_60": {"name": "👀 Просмотры Видео [60 сек удержание]", "id": "1371", "price": round(53.78 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Монетизируемый"},
            "vex_fb_views_video_30": {"name": "👀 Просмотры Видео [30 сек удержание]", "id": "1372", "price": round(106.31 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Монетизируемый"},
            "vex_fb_views_video_10": {"name": "👀 Просмотры Видео [10 сек удержание]", "id": "1373", "price": round(85.86 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Монетизируемый"},
            "vex_fb_repost_photo": {"name": "🔁 Пост Фото Репост [Высокое качество]", "id": "1374", "price": round(87.46 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Высокое качество"}
        }
    },

    # ============ VEXBOOST — TWITCH ============
    "twitch": {
        "title": "🎮 TWITCH",
        "items": {
            "vex_tw_subs_auto": {"name": "👥 Подписчики [30 Авто-восст.]", "id": "1356", "price": round(13.48 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Каждые 24 часа авто восстановление"},
            "vex_tw_subs_30d": {"name": "👥 Подписчики [30 Дней гарантии] [Макс: 1млн]", "id": "1759", "price": round(23.90 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Стабильная услуга"},
            "vex_tw_subs_90d": {"name": "👥 Подписчики [90 Дней гарантии] [100К/День]", "id": "1984", "price": round(30.06 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Стабильная услуга"},
            "vex_tw_subs_hq_auto": {"name": "👥 Подписчики [Высокое качество] [Авто-восст. 30♻️]", "id": "2531", "price": round(173.60 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Без Списаний"},
            "vex_tw_subs_no_drop": {"name": "👥 Подписчики [Без списаний] [Гарантия 30♻️]", "id": "3106", "price": round(5.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Лучшая цена"},
            "vex_tw_subs_prime": {"name": "👥 Подписчики Prime", "id": "2185", "price": round(16538.37 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Выплаты не гарантируются"},
            "vex_tw_views_clips": {"name": "👀 Просмотры клипов [Лучшая цена]", "id": "2560", "price": round(4.04 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Медленные"},
            "vex_tw_views_clips_fast": {"name": "👀 Просмотры Клипов/Видео [Быстрые]", "id": "3147", "price": round(7.84 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Быстрые"},
            "vex_tw_bits": {"name": "💎 Bits на ваш канал", "id": "2184", "price": round(82.25 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Выплаты не гарантируются"},
            "vex_tw_chat_1h": {"name": "💬 Чат-Бот [1 Час] [Свой список]", "id": "1778", "price": round(351.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Чат должен быть открыт"},
            "vex_tw_chat_1d": {"name": "💬 Чат-Бот [1 День] [Свой список]", "id": "1779", "price": round(1521.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Чат должен быть открыт"},
            "vex_tw_chat_1w": {"name": "💬 Чат-Бот [1 Неделю] [Свой список]", "id": "1780", "price": round(9243.02 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Чат должен быть открыт"},
            "vex_tw_viewers_1h": {"name": "👥 Зрители [1 Час][Авто-гео]", "id": "2170", "price": round(235.52 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Рейд, Опросы, Авторизация"},
            "vex_tw_viewers_2h": {"name": "👥 Зрители [2 Часа][Авто-гео]", "id": "2171", "price": round(471.04 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Рейд, Опросы, Авторизация"},
            "vex_tw_viewers_3h": {"name": "👥 Зрители [3 Часа][Авто-гео]", "id": "2172", "price": round(706.56 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Рейд, Опросы, Авторизация"},
            "vex_tw_viewers_4h": {"name": "👥 Зрители [4 Часа][Авто-гео]", "id": "2173", "price": round(942.08 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Рейд, Опросы, Авторизация"},
            "vex_tw_viewers_24h": {"name": "👥 Зрители [24 Часа][Авто-гео]", "id": "2174", "price": round(1797.02 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Рейд, Опросы, Авторизация"},
            "vex_tw_viewers_1w": {"name": "👥 Зрители [1 Неделя][Авто-гео]", "id": "2175", "price": round(7301.12 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Рейд, Опросы, Авторизация"},
            "vex_tw_viewers_1m": {"name": "👥 Зрители [1 Месяц][Авто-гео]", "id": "2176", "price": round(21667.85 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Рейд, Опросы, Авторизация"},
            "vex_tw_viewers_15m_raid": {"name": "👥 Зрители [15 Минут + Рейды]", "id": "3133", "price": round(35.29 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Дроп до 10%"},
            "vex_tw_viewers_30m_raid": {"name": "👥 Зрители [30 Минут + Рейды]", "id": "3134", "price": round(70.58 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Дроп до 10%"},
            "vex_tw_viewers_45m_raid": {"name": "👥 Зрители [45 Минут + Рейды]", "id": "3135", "price": round(94.11 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Дроп до 10%"},
            "vex_tw_viewers_2h_raid": {"name": "👥 Зрители [2 Часа + Рейды]", "id": "3136", "price": round(287.56 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Дроп до 10%"},
            "vex_tw_viewers_3h_raid": {"name": "👥 Зрители [3 Часа + Рейды]", "id": "3137", "price": round(431.34 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Дроп до 10%"},
            "vex_tw_viewers_4h_raid": {"name": "👥 Зрители [4 Часа + Рейды]", "id": "3138", "price": round(575.12 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Дроп до 10%"},
            "vex_tw_viewers_5h_raid": {"name": "👥 Зрители [5 Часов + Рейды]", "id": "3139", "price": round(718.90 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Дроп до 10%"},
            "vex_tw_viewers_6h_raid": {"name": "👥 Зрители [6 Часов + Рейды]", "id": "3140", "price": round(862.68 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Дроп до 10%"},
            "vex_tw_viewers_7h_raid": {"name": "👥 Зрители [7 Часов + Рейды]", "id": "3141", "price": round(1006.45 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Дроп до 10%"},
            "vex_tw_viewers_8h_raid": {"name": "👥 Зрители [8 Часов + Рейды]", "id": "3142", "price": round(1150.23 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Дроп до 10%"},
            "vex_tw_viewers_24h_raid": {"name": "👥 Зрители [24 Часа + Рейды]", "id": "3143", "price": round(1305.78 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Дроп до 10%"},
            "vex_tw_viewers_1h_ru": {"name": "🇷🇺 Зрители [1 Час][100% Авторизации][Россия]", "id": "2803", "price": round(285.63 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Удержание 5 минут"},
            "vex_tw_viewers_1d_ru": {"name": "🇷🇺 Зрители [1 День][100% Авторизации][Россия]", "id": "2804", "price": round(1563.81 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Удержание 5 минут"},
            "vex_tw_viewers_1w_ru": {"name": "🇷🇺 Зрители [1 Неделя][100% Авторизации][Россия]", "id": "2805", "price": round(8373.59 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Удержание 5 минут"},
            "vex_tw_viewers_1m_ru": {"name": "🇷🇺 Зрители [1 Месяц][100% Авторизации][Россия]", "id": "2806", "price": round(25505.18 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Удержание 5 минут"},
            "vex_tw_viewers_15m_ru": {"name": "🇷🇺 Зрители [15 Минут][100% Авторизации][Россия]", "id": "2807", "price": round(122.92 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Удержание 5 минут"},
            "vex_tw_viewers_3h_ru": {"name": "🇷🇺 Зрители [3 Часа][100% Авторизации][Россия]", "id": "2808", "price": round(1211.05 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Удержание 5 минут"},
            "vex_tw_viewers_4h_ru": {"name": "🇷🇺 Зрители [4 Часа][100% Авторизации][Россия]", "id": "2809", "price": round(1614.74 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Удержание 5 минут"},
            "vex_tw_viewers_5h_ru": {"name": "🇷🇺 Зрители [5 Часов][100% Авторизации][Россия]", "id": "2810", "price": round(2016.76 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Удержание 5 минут"},
            "vex_tw_viewers_24h_ru": {"name": "🇷🇺 Зрители [24 Часа][100% Авторизации][Россия]", "id": "2811", "price": round(2232.72 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Удержание 5 минут"},
            "vex_tw_viewers_30m_ru": {"name": "🇷🇺 Зрители [30 Минут][100% Авторизации][Россия]", "id": "2812", "price": round(244.21 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Удержание 5 минут"},
            "vex_tw_viewers_45m_ru": {"name": "🇷🇺 Зрители [45 Минут][100% Авторизации][Россия]", "id": "2813", "price": round(305.67 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Удержание 5 минут"},
            "vex_tw_ai_chat_1h": {"name": "🤖 Twitch ИИ Чат-Бот [1 Час]", "id": "3148", "price": round(20843.53 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Автоопределение языка стрима"},
            "vex_tw_ai_chat_2h": {"name": "🤖 Twitch ИИ Чат-Бот [2 Часа]", "id": "3149", "price": round(41687.06 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Автоопределение языка стрима"},
            "vex_tw_ai_chat_3h": {"name": "🤖 Twitch ИИ Чат-Бот [3 Часа]", "id": "3150", "price": round(62530.58 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Автоопределение языка стрима"},
            "vex_tw_ai_chat_4h": {"name": "🤖 Twitch ИИ Чат-Бот [4 Часа]", "id": "3151", "price": round(83374.11 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Автоопределение языка стрима"},
            "vex_tw_ai_chat_5h": {"name": "🤖 Twitch ИИ Чат-Бот [5 Часов]", "id": "3152", "price": round(104217.64 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Автоопределение языка стрима"},
            "vex_tw_ai_chat_6h": {"name": "🤖 Twitch ИИ Чат-Бот [6 Часов]", "id": "3153", "price": round(180643.91 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Автоопределение языка стрима"},
            "vex_tw_ai_chat_7h": {"name": "🤖 Twitch ИИ Чат-Бот [7 Часов]", "id": "3154", "price": round(214323.28 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Автоопределение языка стрима"},
            "vex_tw_ai_chat_8h": {"name": "🤖 Twitch ИИ Чат-Бот [8 Часов]", "id": "3155", "price": round(244940.90 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Автоопределение языка стрима"},
            "vex_tw_ai_chat_9h": {"name": "🤖 Twitch ИИ Чат-Бот [9 Часов]", "id": "3156", "price": round(275558.51 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Автоопределение языка стрима"},
            "vex_tw_ai_chat_10h": {"name": "🤖 Twitch ИИ Чат-Бот [10 Часов]", "id": "3157", "price": round(306176.12 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Автоопределение языка стрима"}
         }
    },

    # ============ VEXBOOST — MAX ============
    "max": {
        "title": "💠 MAX",
        "items": {
            "vex_mx_subs_7d": {"name": "👥 Подписчики [7 Дней]", "id": "3098", "price": round(198.56 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Оформленные аккаунты, Гео: РУ"},
            "vex_mx_subs_30d": {"name": "👥 Подписчики [30 Дней]", "id": "3041", "price": round(324.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Гарантия 30 дней"},
            "vex_mx_subs_60d": {"name": "👥 Подписчики [60 Дней]", "id": "3042", "price": round(720.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "25000 в сутки"},
            "vex_mx_subs_90d": {"name": "👥 Подписчики [90 Дней]", "id": "2992", "price": round(1224.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Женские Профили, Гео: РУ/СНГ"},
            "vex_mx_subs_no_drop_1": {"name": "👥 Подписчики [Без списаний] [Сервер 1]", "id": "3119", "price": round(2088.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Без гарантии"},
            "vex_mx_subs_no_drop_2": {"name": "👥 Подписчики [Без списаний] [Сервер 2]", "id": "3128", "price": round(2218.50 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Без гарантии"},
            "vex_mx_subs_male": {"name": "👥 Подписчики Чат/Канал [Мужские профили]", "id": "3120", "price": round(2232.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Без списаний"},
            "vex_mx_subs_female": {"name": "👥 Подписчики Чат/Канал [Женские профили]", "id": "3121", "price": round(2232.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Без списаний"},
            "vex_mx_subs_real_1000": {"name": "👥 Подписчики Чат/Канал [Реальные до 1000/сутки]", "id": "2684", "price": round(6372.03 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Гео: Россия + Беларусь"},
            "vex_mx_subs_live_male": {"name": "👥 Подписчики Чат/Канал [Мужские живые до 1000/сутки]", "id": "3000", "price": round(4712.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Живые люди"},
            "vex_mx_subs_live_female": {"name": "👥 Подписчики Чат/Канал [Женские живые до 1000/сутки]", "id": "2999", "price": round(4712.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Живые люди"},
            "vex_mx_subs_action": {"name": "👥 Подписчики [Без списаний] [Акция]🔥", "id": "3272", "price": round(1164.12 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Имена Микс/Ру/СНГ"},
            "vex_mx_subs_for_views": {"name": "👥 Подписчики для просмотров/реакций [Закрытые каналы]", "id": "3190", "price": round(2078.96 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Закажите столько подписчиков, сколько нужно"},
            "vex_mx_views_1post": {"name": "👀 Просмотры [На 1 пост] [Лучшая цена]", "id": "3097", "price": round(137.60 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Кнопка отмены, Гео: СНГ"},
            "vex_mx_views_closed": {"name": "👀 Просмотры [Для закрытых каналов]", "id": "3191", "price": round(112.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Сначала закажите подписчиков"},
            "vex_mx_views_smart": {"name": "👀 Умные Просмотры [Лесенкой]", "id": "3234", "price": round(194.40 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Старт - 3%, 5 мин - 3%"},
            "vex_mx_views_last_5": {"name": "👀 Просмотры на 5 последних постов", "id": "3122", "price": round(806.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Быстрая скорость"},
            "vex_mx_views_last_10": {"name": "👀 Просмотры на 10 последних постов", "id": "3123", "price": round(1612.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Быстрая скорость"},
            "vex_mx_views_last_25": {"name": "👀 Просмотры на 25 последних постов", "id": "3124", "price": round(4212.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Быстрая скорость"},
            "vex_mx_views_last_50": {"name": "👀 Просмотры на 50 последних постов", "id": "3125", "price": round(8424.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Быстрая скорость"},
            "vex_mx_views_last_100": {"name": "👀 Просмотры на 100 последних постов", "id": "3126", "price": round(16848.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Быстрая скорость"},
            "vex_mx_views_all": {"name": "👀 Просмотр ВСЕХ постов", "id": "3127", "price": round(14256.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Указывайте ссылку на канал"},
            "vex_mx_views_future_5": {"name": "👀 Просмотры на 5 будущих постов", "id": "3273", "price": round(806.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Быстрая скорость"},
            "vex_mx_views_future_10": {"name": "👀 Просмотры на 10 будущих постов", "id": "3274", "price": round(1612.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Быстрая скорость"},
            "vex_mx_views_future_20": {"name": "👀 Просмотры на 20 будущих постов", "id": "3275", "price": round(3224.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Быстрая скорость"},
            "vex_mx_views_future_50": {"name": "👀 Просмотры на 50 будущих постов", "id": "3276", "price": round(8060.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Быстрая скорость"},
            "vex_mx_views_future_100": {"name": "👀 Просмотры на 100 будущих постов", "id": "3277", "price": round(16120.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Быстрая скорость"},
            "vex_mx_views_closed_5": {"name": "👀 Просмотры [5 последних постов][Для закрытых]", "id": "3196", "price": round(468.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Сначала закажите подписчиков"},
            "vex_mx_views_closed_10": {"name": "👀 Просмотры [10 последних постов][Для закрытых]", "id": "3197", "price": round(936.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Сначала закажите подписчиков"},
            "vex_mx_views_closed_25": {"name": "👀 Просмотры [25 последних постов][Для закрытых]", "id": "3198", "price": round(2210.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Сначала закажите подписчиков"},
            "vex_mx_views_closed_50": {"name": "👀 Просмотры [50 последних постов][Для закрытых]", "id": "3199", "price": round(4160.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Сначала закажите подписчиков"},
            "vex_mx_views_closed_100": {"name": "👀 Просмотры [100 последних постов][Для закрытых]", "id": "3200", "price": round(7800.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Сначала закажите подписчиков"},
            "vex_mx_reactions_live": {"name": "❤️ Живые Реакции [Позитивные]", "id": "2683", "price": round(1235.19 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Гео: Россия + Беларусь"},
            "vex_mx_reactions_pos": {"name": "❤️ Позитивные реакции [👍❤️🔥😍]", "id": "3082", "price": round(473.60 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Реакции"},
            "vex_mx_reactions_neg": {"name": "👎 Негативные реакции [🤮💩🤡🤬]", "id": "3086", "price": round(473.60 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Реакции"},
            "vex_mx_reaction_like": {"name": "👍 Реакция [👍]", "id": "3083", "price": round(473.60 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Реакции"},
            "vex_mx_reaction_dislike": {"name": "👎 Реакция [👎]", "id": "3084", "price": round(473.60 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Реакции"},
            "vex_mx_reaction_heart": {"name": "❤️ Реакция [❤️]", "id": "3085", "price": round(473.60 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Реакции"},
            "vex_mx_reaction_party": {"name": "🥳 Реакция [🥳]", "id": "3087", "price": round(473.60 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Реакции"},
            "vex_mx_reaction_confetti": {"name": "🎉 Реакция [🎉]", "id": "3088", "price": round(473.60 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Реакции"},
            "vex_mx_reaction_pray": {"name": "🙏 Реакция [🙏]", "id": "3089", "price": round(473.60 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Реакции"},
            "vex_mx_reaction_vomit": {"name": "🤮 Реакция [🤮]", "id": "3090", "price": round(473.60 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Реакции"},
            "vex_mx_reaction_poop": {"name": "💩 Реакция [💩]", "id": "3091", "price": round(473.60 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Реакции"},
            "vex_mx_reaction_clown": {"name": "🤡 Реакция [🤡]", "id": "3092", "price": round(473.60 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Реакции"},
            "vex_mx_reaction_swear": {"name": "🤬 Реакция [🤬]", "id": "3093", "price": round(473.60 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Реакции"},
            "vex_mx_reaction_rofl": {"name": "🤣 Реакция [🤣]", "id": "3094", "price": round(473.60 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Реакции"},
            "vex_mx_reaction_fire": {"name": "🔥 Реакция [🔥]", "id": "3095", "price": round(473.60 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Реакции"},
            "vex_mx_reaction_crown": {"name": "👑 Реакция [👑]", "id": "3096", "price": round(473.60 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Реакции"},
            "vex_mx_reactions_closed": {"name": "❤️ Положительные реакции [Закрытые каналы]", "id": "3192", "price": round(260.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Сначала закажите подписчиков"},
            "vex_mx_reaction_heart_closed": {"name": "❤️ Реакция [❤️][Для закрытых каналов]", "id": "3193", "price": round(260.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Сначала закажите подписчиков"},
            "vex_mx_reaction_fire_closed": {"name": "🔥 Реакция [🔥][Для закрытых каналов]", "id": "3194", "price": round(260.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Сначала закажите подписчиков"},
            "vex_mx_reaction_like_closed": {"name": "👍 Реакция [👍][Для закрытых каналов]", "id": "3195", "price": round(260.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Сначала закажите подписчиков"},
            "vex_mx_reaction_rofl_closed": {"name": "🤣 Реакция [🤣][Для закрытых каналов]", "id": "3201", "price": round(260.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Сначала закажите подписчиков"},
            "vex_mx_reaction_cool_closed": {"name": "😎 Реакция [😎][Для закрытых каналов]", "id": "3202", "price": round(416.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Сначала закажите подписчиков"},
            "vex_mx_reaction_star_closed": {"name": "🤩 Реакция [🤩][Для закрытых каналов]", "id": "3203", "price": round(416.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Сначала закажите подписчиков"},
            "vex_mx_reaction_handshake_closed": {"name": "🤝 Реакция [🤝][Для закрытых каналов]", "id": "3204", "price": round(416.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Сначала закажите подписчиков"},
            "vex_mx_reaction_clap_closed": {"name": "👏 Реакция [👏][Для закрытых каналов]", "id": "3205", "price": round(416.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Сначала закажите подписчиков"},
            "vex_mx_reaction_love_closed": {"name": "🥰 Реакция [🥰][Для закрытых каналов]", "id": "3206", "price": round(416.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Сначала закажите подписчиков"},
            "vex_mx_reposts": {"name": "🔁 Репосты", "id": "2994", "price": round(360.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Женские Профили, Гео: РУ/СНГ"},
            "vex_mx_bot_start": {"name": "🤖 Запуск бота", "id": "2993", "price": round(2592.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Бот старты без отмены"}
        }
    },

    # ============ VEXBOOST — RUTUBE ============
    "rutube": {
        "title": "🟣 RUTUBE",
        "items": {
            "vex_rt_subs_fast": {"name": "👥 Rutube Подписчики [Быстрый старт] [Микс]", "id": "3253", "price": round(31.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Гео: Микс + Россия"},
            "vex_rt_subs_ru": {"name": "🇷🇺 Rutube Подписчики [Быстрый старт] [Россия]", "id": "2789", "price": round(100.10 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Без списаний"},
            "vex_rt_subs_30d": {"name": "👥 Rutube Подписчики [Гарантия 30♻️]", "id": "1875", "price": round(150.15 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Скорость до 15000 в день"},
            "vex_rt_likes_ru": {"name": "🇷🇺 Rutube Лайки [Быстрый старт]", "id": "2790", "price": round(100.10 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Без списаний"},
            "vex_rt_likes_30d": {"name": "❤️ Rutube Лайки на Видео [Гарантия 30♻️]", "id": "1876", "price": round(145.15 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Скорость накрутки ~10k в сутки"},
            "vex_rt_likes_shorts_30d": {"name": "❤️ Rutube Лайки на Shorts [Гарантия 30♻️]", "id": "1878", "price": round(145.15 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Скорость накрутки ~10k в сутки"},
            "vex_rt_top_ru": {"name": "🇷🇺 Rutube В Топ [Быстрые]", "id": "2788", "price": round(100.10 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Влияет положительно на вывод видео в ТОП"},
            "vex_rt_top": {"name": "🚀 Rutube В ТОП", "id": "2781", "price": round(112.62 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Будут накручены нажатия на кнопку \"В топ\""},
            "vex_rt_reactions_random": {"name": "⭐️ Rutube Реакции случайные", "id": "2780", "price": round(112.62 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Случайный выбор эмоций"},
            "vex_rt_views_fast": {"name": "👀 Rutube Просмотры [Моментальные]", "id": "2468", "price": round(4.95 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Скорость до 1кк в сутки"},
            "vex_rt_views_cheap": {"name": "👀 Rutube Просмотры [Лучшая цена]", "id": "2662", "price": round(1.2826 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Без списаний"},
            "vex_rt_views_auto_5": {"name": "👀 Rutube Авто - Просмотры на 5 видео", "id": "1872", "price": round(262.50 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Реальные, ГЕО Россия"},
            "vex_rt_views_auto_10": {"name": "👀 Rutube Авто - Просмотры на 10 видео", "id": "1873", "price": round(455.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Реальные, ГЕО Россия"},
            "vex_rt_views_auto_20": {"name": "👀 Rutube Авто - Просмотры на 20 видео", "id": "1874", "price": round(910.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Реальные, ГЕО Россия"},
            "vex_rt_comments_custom": {"name": "💬 Rutube Комментарии [Собственные]", "id": "1877", "price": round(315.32 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Скорость накрутки до 15к в сутки"}
        }
    },

    # ============ VEXBOOST — KICK ============
    "kick": {
        "title": "🟢 KICK.COM",
        "items": {
            "vex_kick_subs": {"name": "👥 Подписчики [Высокое качество]", "id": "2237", "price": round(36.72 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Возможен долгий старт"},
            "vex_kick_subs_30d": {"name": "👥 Подписчики [Гарантия 30 Дней]", "id": "1295", "price": round(47.76 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Старт: Моментально"},
            "vex_kick_subs_60d": {"name": "👥 Подписчики [Гарантия 60 Дней]", "id": "1294", "price": round(69.28 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Ссылка на профиль"},
            "vex_kick_views_video": {"name": "👀 Просмотры видео [Высокое качество]", "id": "2238", "price": round(4.71 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Аккаунты высокого качества"},
            "vex_kick_views_clips": {"name": "👀 Просмотры клипов [Моментальные]", "id": "2239", "price": round(10.80 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Моментальные"},
                        "vex_kick_views_cheap": {"name": "👀 Просмотры Клипы/Видео [Лучшая цена]", "id": "2946", "price": round(2.70 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Лучшая цена"},
            "vex_kick_chat_30m": {"name": "💬 Чат-Бот [30 Минут] [Свой текст]", "id": "2589", "price": round(371.70 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Чат-бот будет писать каждые 30-60 секунд"},
            "vex_kick_chat_60m": {"name": "💬 Чат-Бот [60 Минут] [Свой текст]", "id": "2590", "price": round(475.78 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Чат-бот будет писать каждые 30-60 секунд"},
            "vex_kick_chat_2h": {"name": "💬 Чат-Бот [2 Часа] [Свой текст]", "id": "2592", "price": round(892.08 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Чат-бот будет писать каждые 30-60 секунд"},
            "vex_kick_chat_3h": {"name": "💬 Чат-Бот [3 Часа] [Свой текст]", "id": "2593", "price": round(1338.13 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Чат-бот будет писать каждые 30-60 секунд"},
            "vex_kick_chat_1d": {"name": "💬 Чат-Бот [1 День] [Свой текст]", "id": "2594", "price": round(2676.25 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Чат-бот будет писать каждые 30-60 секунд"},
            "vex_kick_ai_chat_15m": {"name": "🤖 ИИ Чат-Бот [15 Минут]", "id": "3079", "price": round(5653.19 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Интервал 5-20 сек"},
            "vex_kick_ai_chat_30m": {"name": "🤖 ИИ Чат-Бот [30 Минут]", "id": "3080", "price": round(10175.74 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Интервал 5-20 сек"},
            "vex_kick_ai_chat_60m": {"name": "🤖 ИИ Чат-Бот [60 Минут]", "id": "3081", "price": round(14181.52 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Интервал 5-20 сек"},
            "vex_kick_viewers_5m": {"name": "👀 Зрители [5 Минут] [Без Падений]", "id": "2546", "price": round(13.64 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Гео: Микс"},
            "vex_kick_viewers_10m": {"name": "👀 Зрители [10 Минут] [Без Падений]", "id": "2547", "price": round(6.82 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Гео: Микс"},
            "vex_kick_viewers_15m": {"name": "👀 Зрители [15 Минут] [Без Падений]", "id": "2548", "price": round(5.06 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Гео: Микс"},
            "vex_kick_viewers_30m": {"name": "👀 Зрители [30 Минут] [Без Падений]", "id": "2549", "price": round(11.40 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Гео: Микс"},
            "vex_kick_viewers_45m": {"name": "👀 Зрители [45 Минут] [Без Падений]", "id": "2550", "price": round(17.73 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Гео: Микс"},
            "vex_kick_viewers_60m": {"name": "👀 Зрители [60 Минут] [Без Падений]", "id": "2551", "price": round(22.79 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Гео: Микс"},
            "vex_kick_viewers_90m": {"name": "👀 Зрители [90 Минут] [Без Падений]", "id": "2552", "price": round(34.19 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Гео: Микс"},
            "vex_kick_viewers_120m": {"name": "👀 Зрители [120 Минут] [Без Падений]", "id": "2553", "price": round(44.32 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Гео: Микс"},
            "vex_kick_viewers_150m": {"name": "👀 Зрители [150 Минут] [Без Падений]", "id": "2554", "price": round(79.77 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Гео: Микс"},
            "vex_kick_viewers_180m": {"name": "👀 Зрители [180 Минут] [Без Падений]", "id": "2555", "price": round(67.11 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Гео: Микс"},
            "vex_kick_viewers_240m": {"name": "👀 Зрители [240 Минут] [Без Падений]", "id": "2556", "price": round(88.64 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Гео: Микс"},
            "vex_kick_viewers_300m": {"name": "👀 Зрители [300 Минут] [Без Падений]", "id": "2557", "price": round(111.43 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Гео: Микс"},
            "vex_kick_viewers_24h": {"name": "👀 Зрители [24 Часы] [Без Падений]", "id": "2558", "price": round(531.82 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Гео: Микс"},
            "vex_kick_viewers_top_1h": {"name": "👀 Зрители [Вывод в топ][1 Час]", "id": "2736", "price": round(559.77 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Уникальный IP, С Авторизацией"},
            "vex_kick_viewers_top_2h": {"name": "👀 Зрители [Вывод в топ][2 Часа]", "id": "2737", "price": round(1119.53 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Уникальный IP, С Авторизацией"},
            "vex_kick_viewers_top_3h": {"name": "👀 Зрители [Вывод в топ][3 Часа]", "id": "2738", "price": round(1679.28 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Уникальный IP, С Авторизацией"},
            "vex_kick_viewers_top_4h": {"name": "👀 Зрители [Вывод в топ][4 Часа]", "id": "2739", "price": round(2239.05 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Уникальный IP, С Авторизацией"},
            "vex_kick_viewers_top_5h": {"name": "👀 Зрители [Вывод в топ][5 Часов]", "id": "2740", "price": round(2798.80 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Уникальный IP, С Авторизацией"},
            "vex_kick_viewers_top_24h": {"name": "👀 Зрители [Вывод в топ][24 Часа]", "id": "2741", "price": round(6980.55 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Уникальный IP, С Авторизацией"}
        }
    },

    # ============ VEXBOOST — LIKEE ============
    "likee": {
        "title": "🎬 LIKEE",
        "items": {
            "vex_lk_subs": {"name": "👥 Подписчики [Высокое качество]", "id": "2486", "price": round(775.43 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Высокое качество"},
            "vex_lk_subs_live": {"name": "👥 Подписчики [Живые - Офферы]", "id": "2492", "price": round(557.70 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Гео: РФ, СНГ, ЕВРОПА"},
            "vex_lk_likes": {"name": "❤️ Лайки [Высокое качество]", "id": "2487", "price": round(148.68 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Высокое качество"},
            "vex_lk_likes_live": {"name": "❤️ Лайки [Живые - Офферы]", "id": "2493", "price": round(182.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Аккаунты проявляют активность"},
            "vex_lk_views": {"name": "👀 Просмотры [Высокое качество]", "id": "2488", "price": round(148.68 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Высокое качество"},
            "vex_lk_reposts": {"name": "🔁 Репосты (Поделиться)", "id": "2489", "price": round(148.68 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Высокое качество"},
            "vex_lk_comments_random": {"name": "💬 Случайные комментарии", "id": "2490", "price": round(560.41 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Высокое качество"},
            "vex_lk_comments_custom": {"name": "💬 Свои комментарии [Выполнение до 10 часов]", "id": "2491", "price": round(823.46 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Свои комментарии"}
        }
    },

    # ============ VEXBOOST — WHATSAPP ============
    "whatsapp": {
        "title": "🟢 WHATSAPP",
        "items": {
            "vex_wa_subs": {"name": "👥 Подписчики в Канал", "id": "2676", "price": round(26.14 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "До 10к в день, Без списаний"},
            "vex_wa_react_pos": {"name": "❤️ Реакции в канал [Положительные]", "id": "3189", "price": round(2.84 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "❤️👍🔥🎉😁"}
        }
    },

    # ============ VEXBOOST — ДРУГИЕ ПЛОЩАДКИ ============
    "dzen": {
        "title": "⚡ ДЗЕН",
        "items": {
            "vex_dzen_subs": {"name": "👥 Дзен Подписчики", "id": "1858", "price": round(586.53 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Скорость накрутки до 3к в сутки"},
            "vex_dzen_likes": {"name": "❤️ Дзен Лайки", "id": "1859", "price": round(391.02 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "С лайками частично увеличивается статистика просмотров"},
            "vex_dzen_comments_custom": {"name": "💬 Дзен Комментарии [Собственные]", "id": "1860", "price": round(1259.50 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Свои комментарии"},
            "vex_dzen_views_read": {"name": "👀 Дзен Дочитывания", "id": "1861", "price": round(52.92 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Скорость накрутки до 3–5 тысяч в сутки"},
            "vex_dzen_views_video_30": {"name": "👀 Дзен Просмотры Видео [30 сек.]", "id": "1862", "price": round(101.46 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Скорость накрутки до 5к в сутки"},
            "vex_dzen_views_video_60": {"name": "👀 Дзен Просмотры Видео [60 сек.]", "id": "1863", "price": round(142.88 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Скорость накрутки до 5к в сутки"},
            "vex_dzen_views_video_90": {"name": "👀 Дзен Просмотры Видео [90 сек.]", "id": "1864", "price": round(162.73 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Скорость накрутки до 5к в сутки"},
            "vex_dzen_views_video_120": {"name": "👀 Дзен Просмотры Видео [120 сек.]", "id": "1865", "price": round(187.87 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Скорость накрутки до 5к в сутки"}
        }
    },
    "ok": {
        "title": "🟠 ОДНОКЛАССНИКИ",
        "items": {
            "vex_ok_views_video": {"name": "👀 ОК Просмотры [Видео]", "id": "3010", "price": round(12.66 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Скорость: До 500к в сутки"},
            "vex_ok_reposts_bots": {"name": "🔁 ОК Репосты [Боты]", "id": "3011", "price": round(13.07 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Безопасная - плавная накрутка"},
            "vex_ok_reposts_live": {"name": "🔁 ОК Репосты [Реальные Люди]", "id": "3012", "price": round(2115.51 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Гарантия в случае списаний"},
            "vex_ok_subs": {"name": "👥 ОК Подписчики на группу/страницу", "id": "3013", "price": round(240.25 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Старт до 30 минут"},
            "vex_ok_likes": {"name": "❤️ ОК Лайки(Классы) на посты [Микс]", "id": "3014", "price": round(119.35 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Аккаунты высокого качества"},
            "vex_ok_subs_cis_ru": {"name": "🇷🇺 ОК Подписчики на группу/страницу [СНГ+РФ]", "id": "3015", "price": round(507.20 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Скорость до 500 в сутки"},
            "vex_ok_likes_cis": {"name": "🇷🇺 ОК Лайки(Классы) СНГ", "id": "3016", "price": round(376.00 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Скорость до 500 в сутки"}
        }
    },
    "spotify": {
        "title": "🟢 SPOTIFY",
        "items": {
            "vex_sp_plays_usa": {"name": "🇺🇸 Spotify Прослушивания [США]", "id": "2363", "price": round(21.53 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Пожизненная гарантия"},
            "vex_sp_plays_eu": {"name": "🇪🇺 Spotify Прослушивания [Европа]", "id": "2364", "price": round(21.53 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Пожизненная гарантия"},
            "vex_sp_listeners": {"name": "Spotify Ежемесячные слушатели [Микс]", "id": "2365", "price": round(213.99 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "До 10к/День"},
            "vex_sp_saves": {"name": "Spotify Сохранения [Трек/Альбом]", "id": "2366", "price": round(27.86 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Гарантия 30 дней"},
            "vex_sp_plays_mix": {"name": "Spotify Прослушивания [Микс]", "id": "2367", "price": round(21.53 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "До 50к/День, Гарантия"},
            "vex_sp_plays_slow": {"name": "Spotify Прослушивания [Медленные]", "id": "2368", "price": round(30.39 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "До 200/День, Гарантия"},
            "vex_sp_subs_no_guar": {"name": "Spotify Подписчики [Микс] [Без Гарантии]", "id": "2370", "price": round(17.73 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Артисты/Плейлист/Пользователь"},
            "vex_sp_subs_30d": {"name": "Spotify Подписчики [Микс] [30 Дней Гарантии]", "id": "2371", "price": round(20.26 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "Артисты/Плейлист/Пользователь"},
            "vex_sp_combo_base": {"name": "Spotify Базовое комбо", "id": "2372", "price": round(378.60 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "3к Прослушиваний + 300 Сохранений + 300 Подписчиков"},
            "vex_sp_combo_pro": {"name": "Spotify Про комбо", "id": "2373", "price": round(1138.35 * 1.35, 2), "pack": 1000, "panel": "panel_4", "desc": "10к Прослушиваний + 1к Сохранений + 1к Подписчиков"}
        }
    }
}

# ============ ЭКСПОРТ КАТАЛОГА ДЛЯ MINI APP ============
def export_miniapp_catalog():
    meta = {
        "telegram":  ("fab fa-telegram", "#0088cc"),
        "tiktok":    ("fab fa-tiktok", "#ffffff"),
        "youtube":   ("fab fa-youtube", "#ff0000"),
        "instagram": ("fab fa-instagram", "#e84393"),
        "vk":        ("fab fa-vk", "#4a76a8"),
        "twitch":    ("fab fa-twitch", "#9146ff"),
        "twitter":   ("fab fa-twitter", "#1da1f2"),
        "likee":     ("fas fa-video", "#ff0050"),
        "whatsapp":  ("fab fa-whatsapp", "#25D366"),
        "facebook":  ("fab fa-facebook", "#1877f2"),
        "rutube":    ("fas fa-play-circle", "#ff0000"),
        "max":       ("fas fa-comment-dots", "#00c853"),
        "kick":      ("fas fa-bolt", "#53fc18"),
        "dzen":      ("fas fa-fire", "#ffffff"),
        "ok":        ("fab fa-odnoklassniki", "#ee8208"),
        "spotify":   ("fab fa-spotify", "#1db954"),
    }
    catalog = {}
    for plat, pdata in SERVICES.items():
        icon, color = meta.get(plat, ("fas fa-globe", "#b829ff"))
        items_list = []
        for key, item in pdata.get("items", {}).items():
            items_list.append({
                "key": str(key),
                "name": item.get("name", ""),
                "desc": item.get("desc", ""),
                "price": float(item.get("price", 0)),
                "pack": int(item.get("pack", 1000)),
                "speed": "⚡ Быстро",
            })
        catalog[plat] = {
            "title": pdata.get("title", plat.upper()),
            "icon": icon,
            "color": color,
            "items": items_list,
        }
    with open("catalog.js", "w", encoding="utf-8") as f:
        f.write("const CATALOG = " + json.dumps(catalog, ensure_ascii=False) + ";\n")

export_miniapp_catalog()

_PLAT_TITLES = {"tiktok": "🎵 TIKTOK", "telegram": "✈️ TELEGRAM"}
for _plat, _pdata in list(SERVICES.items()):
    if "items" not in _pdata:
        _items = {}
        for _k, _v in _pdata.items():
            if isinstance(_v, dict):
                _v.setdefault("id", str(_k))
                _v.setdefault("pack", 1000)
                _items[_k] = _v
        SERVICES[_plat] = {
            "title": _PLAT_TITLES.get(_plat, _plat.upper()),
            "items": _items,
        }


# ============ УСЛУГИ БЕЗ ПЛАВНОЙ НАКРУТКИ ============
SMOOTH_DISABLED_KEYS = {
    "tg_stars", "tg_stars_small", "tg_stars_medium", "tg_stars_big",
    "tg_report_menu", "tg_report_1", "tg_report_2", "tg_report_3",
    "sniper_tg_report",
    "tg_bot_start", "vex_tg_bot_start_premium", "vex_tg_refs_start",
    "mx_bot_start",
}

def can_be_smooth(plat, key):
    """Можно ли растянуть услугу по дням"""
    if plat == "privat":
        return True  # приват — всегда плавный
    if key in SMOOTH_DISABLED_KEYS:
        return False
    return True
    
# ============ ПАКЕТЫ ============
BUNDLES = {
    "tg_start": {"name": "🚀 TG Старт", "category": "telegram", "desc": "500 подписчиков + 5000 просмотров", "items": [("telegram", "tg_subs", 500), ("telegram", "tg_views", 5000)], "discount": 10},
    "tg_boost": {"name": "💫 TG Boost", "category": "telegram", "desc": "1000 подписчиков + 10000 просмотров + 500 реакций", "items": [("telegram", "tg_subs", 1000), ("telegram", "tg_views", 10000), ("telegram", "tg_react_pos", 500)], "discount": 15},
    "tg_pro": {"name": "⭐️ TG Pro", "category": "telegram", "desc": "2000 подписчиков + 20000 просмотров + 1000 реакций", "items": [("telegram", "tg_subs", 2000), ("telegram", "tg_views", 20000), ("telegram", "tg_react_pos", 1000)], "discount": 17},
    "tg_full": {"name": "👑 TG Полный", "category": "telegram", "desc": "3000 подписчиков + 30000 просмотров + 1500 реакций + 10000 запусков", "items": [("telegram", "tg_subs", 3000), ("telegram", "tg_views", 30000), ("telegram", "tg_react_pos", 1500), ("telegram", "tg_bot_start", 10000)], "discount": 20},
    "tg_react_pos_pack": {"name": "🚀 TG Позитив", "category": "telegram", "desc": "2000 позитивных реакций 👍🔥❤️", "items": [("telegram", "tg_react_pos", 2000)], "discount": 8},
    "tg_react_neg_pack": {"name": "👎 TG Негатив", "category": "telegram", "desc": "2000 негативных реакций 🖕💩", "items": [("telegram", "tg_react_neg", 2000)], "discount": 8},
    "tg_stars_small": {"name": "🌟 Звёзды 500", "category": "telegram", "desc": "500 звёзд на аккаунт", "items": [("telegram", "tg_stars", 500)], "discount": 5},
    "tg_stars_medium": {"name": "🌟 Звёзды 1000", "category": "telegram", "desc": "1000 звёзд на аккаунт", "items": [("telegram", "tg_stars", 1000)], "discount": 8},
    "tg_stars_big": {"name": "🌟 Звёзды 2500", "category": "telegram", "desc": "2500 звёзд на аккаунт", "items": [("telegram", "tg_stars", 2500)], "discount": 12},
    "tg_bot_start_pack": {"name": "🤖 TG Запуск бота", "category": "telegram", "desc": "50000 запусков бота", "items": [("telegram", "tg_bot_start", 50000)], "discount": 10},
    "tg_reports_mega": {"name": "🚨 TG Жалобы MEGA", "category": "telegram", "desc": "5000 жалоб на аккаунт", "items": [("telegram", "tg_report_menu", 5000)], "discount": 0},

    "tt_start": {"name": "🚀 TikTok Старт", "category": "tiktok", "desc": "1000 просмотров + 500 лайков", "items": [("tiktok", "tt_views", 1000), ("tiktok", "tt_likes_vingboost", 500)], "discount": 10},
    "tt_trend": {"name": "📈 TikTok Тренд", "category": "tiktok", "desc": "10000 просмотров + 1000 лайков + 500 сохранений", "items": [("tiktok", "tt_views", 10000), ("tiktok", "tt_likes_vingboost", 1000), ("tiktok", "tt_saves", 500)], "discount": 15},
    "tt_viral": {"name": "🔥 TikTok Виральный", "category": "tiktok", "desc": "50000 просмотров + 2000 лайков + 500 подписчиков + 1000 сохранений", "items": [("tiktok", "tt_views", 50000), ("tiktok", "tt_likes_vingboost", 2000), ("tiktok", "tt_subs", 500), ("tiktok", "tt_saves", 1000)], "discount": 20},
    "tt_mega": {"name": "💎 TikTok MEGA", "category": "tiktok", "desc": "100000 просмотров + 5000 лайков + 2000 подписчиков + 3000 сохранений + 1000 репостов", "items": [("tiktok", "tt_views", 100000), ("tiktok", "tt_likes_vingboost", 5000), ("tiktok", "tt_subs", 2000), ("tiktok", "tt_saves", 3000), ("tiktok", "tt_reposts", 1000)], "discount": 25},
    "tt_likes_reposts": {"name": "🔁 TikTok Лайки + Репосты", "category": "tiktok", "desc": "500 лайков + 300 репостов", "items": [("tiktok", "tt_likes_vingboost", 500), ("tiktok", "tt_reposts", 300)], "discount": 12},
    "tt_subs_likes": {"name": "💫 TikTok Подписчики + Лайки", "category": "tiktok", "desc": "1000 подписчиков + 2000 лайков", "items": [("tiktok", "tt_subs", 1000), ("tiktok", "tt_likes_vingboost", 2000)], "discount": 15},
    "tt_views_pack": {"name": "👀 TikTok Просмотры", "category": "tiktok", "desc": "50000 просмотров", "items": [("tiktok", "tt_views", 50000)], "discount": 10},
    "tt_mix_555": {"name": "🎯 Микс 555", "category": "tiktok", "desc": "555 лайков + 7777 просмотров + 333 сохранения + 111 репостов", "items": [("tiktok", "tt_likes_vingboost", 555), ("tiktok", "tt_views", 7777), ("tiktok", "tt_saves", 333), ("tiktok", "tt_reposts", 111)], "discount": 0, "fixed_price": 414.13},

    "ig_start": {"name": "🚀 Instagram Старт", "category": "instagram", "desc": "500 подписчиков + 1000 лайков", "items": [("instagram", "ig_subs", 500), ("instagram", "ig_likes", 1000)], "discount": 10},
    "ig_reels": {"name": "🎬 Instagram Reels", "category": "instagram", "desc": "5000 просмотров + 1000 лайков + 500 сохранений", "items": [("instagram", "ig_views", 5000), ("instagram", "ig_likes", 1000), ("instagram", "ig_saves", 500)], "discount": 15},
    "ig_reach": {"name": "📊 Instagram Охват", "category": "instagram", "desc": "5000 просмотров + 5000 охвата + 500 подписчиков", "items": [("instagram", "ig_views", 5000), ("instagram", "ig_reach", 5000), ("instagram", "ig_subs", 500)], "discount": 12},
    "ig_pro": {"name": "⭐️ Instagram Pro", "category": "instagram", "desc": "2000 подписчиков + 5000 лайков + 10000 просмотров + 2000 сохранений", "items": [("instagram", "ig_subs", 2000), ("instagram", "ig_likes", 5000), ("instagram", "ig_views", 10000), ("instagram", "ig_saves", 2000)], "discount": 20},

    "yt_start": {"name": "🚀 YouTube Старт", "category": "youtube", "desc": "500 подписчиков + 5000 просмотров", "items": [("youtube", "yt_subs", 500), ("youtube", "yt_views", 5000)], "discount": 10},
    "yt_boost": {"name": "💫 YouTube Boost", "category": "youtube", "desc": "1000 подписчиков + 10000 просмотров + 500 лайков", "items": [("youtube", "yt_subs", 1000), ("youtube", "yt_views", 10000), ("youtube", "yt_likes", 500)], "discount": 15},
    "yt_full": {"name": "👑 YouTube Полный", "category": "youtube", "desc": "2000 подписчиков + 20000 просмотров + 1000 лайков", "items": [("youtube", "yt_subs", 2000), ("youtube", "yt_views", 20000), ("youtube", "yt_likes", 1000)], "discount": 18},
    "yt_views_pack": {"name": "👀 YouTube Просмотры", "category": "youtube", "desc": "10000 просмотров", "items": [("youtube", "yt_views", 10000)], "discount": 8},

    "vk_start": {"name": "🚀 ВК Старт", "category": "vk", "desc": "1000 подписчиков + 5000 просмотров + 500 лайков", "items": [("vk", "vk_subs", 1000), ("vk", "vk_views", 5000), ("vk", "vk_likes", 500)], "discount": 10},
    "vk_boost": {"name": "💫 ВК Boost", "category": "vk", "desc": "2000 подписчиков + 10000 просмотров + 1000 лайков", "items": [("vk", "vk_subs", 2000), ("vk", "vk_views", 10000), ("vk", "vk_likes", 1000)], "discount": 15},
    "vk_full": {"name": "👑 ВК Полный", "category": "vk", "desc": "5000 подписчиков + 20000 просмотров + 2000 лайков + 1000 репостов", "items": [("vk", "vk_subs", 5000), ("vk", "vk_views", 20000), ("vk", "vk_likes", 2000), ("vk", "vk_reposts", 1000)], "discount": 20},

    "mini_boost": {"name": "⚡ Мини-буст", "category": "universal", "desc": "TG 500 подписчиков + TikTok 1000 лайков", "items": [("telegram", "tg_subs", 500), ("tiktok", "tt_likes_vingboost", 1000)], "discount": 12},
    "cross_platform": {"name": "🌐 Кросс-платформа", "category": "universal", "desc": "TG 1000 подписчиков + TikTok 5000 просмотров + IG 1000 лайков", "items": [("telegram", "tg_subs", 1000), ("tiktok", "tt_views", 5000), ("instagram", "ig_likes", 1000)], "discount": 15},
    "mega_pack": {"name": "💎 Мега-пакет", "category": "universal", "desc": "TG + TikTok + Instagram + YouTube — всё сразу", "items": [("telegram", "tg_subs", 2000), ("tiktok", "tt_views", 20000), ("tiktok", "tt_likes_vingboost", 2000), ("instagram", "ig_subs", 1000), ("instagram", "ig_likes", 2000), ("youtube", "yt_views", 5000)], "discount": 25},
    "influencer_pack": {"name": "🔥 Инфлюенсер", "category": "universal", "desc": "TG + TikTok + Instagram + YouTube + ВК", "items": [("telegram", "tg_subs", 5000), ("telegram", "tg_views", 50000), ("tiktok", "tt_views", 50000), ("tiktok", "tt_likes_vingboost", 5000), ("instagram", "ig_subs", 2000), ("instagram", "ig_likes", 5000), ("youtube", "yt_views", 20000), ("vk", "vk_subs", 2000)], "discount": 30},
    "stars_mega": {"name": "🌟 Мега-звёзды", "category": "universal", "desc": "10000 звёзд на аккаунт", "items": [("telegram", "tg_stars", 10000)], "discount": 15},
    "cheap_start": {"name": "💚 Старт за 50₽", "category": "universal", "desc": "500 просмотров TG + 50 лайков VK", "items": [("telegram", "tg_views", 500), ("vk", "vk_likes", 50)], "discount": 5},
    "cheap_tt": {"name": "💚 TikTok за 50₽", "category": "tiktok", "desc": "1000 просмотров + 100 лайков", "items": [("tiktok", "tt_views", 1000), ("tiktok", "tt_likes_vingboost", 100)], "discount": 5},
    "cheap_ig": {"name": "💚 Instagram за 50₽", "category": "instagram", "desc": "500 просмотров + 50 лайков", "items": [("instagram", "ig_views", 500), ("instagram", "ig_likes", 50)], "discount": 5},
}

BUNDLE_CATEGORIES = {
    "telegram":  {"name": "✈️ Telegram",  "emoji": "✈️"},
    "tiktok":    {"name": "🎵 TikTok",    "emoji": "🎵"},
    "instagram": {"name": "📸 Instagram", "emoji": "📸"},
    "youtube":   {"name": "▶️ YouTube",   "emoji": "▶️"},
    "vk":        {"name": "🅱️ ВКонтакте", "emoji": "🅱️"},
    "universal": {"name": "🌐 Универсальные", "emoji": "🌐"},
}

# ============ УМНЫЙ ПОДБОР (КВИЗ) ============
QUIZ_PLATFORMS = {
    "telegram":  {"title": "✈️ Telegram",  "emoji": "✈️"},
    "tiktok":    {"title": "🎵 TikTok",    "emoji": "🎵"},
    "youtube":   {"title": "▶️ YouTube",   "emoji": "▶️"},
    "instagram": {"title": "📸 Instagram", "emoji": "📸"},
    "vk":        {"title": "🅱️ ВКонтакте", "emoji": "🅱️"},
}

QUIZ_GOALS = {
    "growth":  {"title": "📈 Рост канала (подписчики)", "emoji": "📈"},
    "views":   {"title": "👀 Виральность (просмотры)",  "emoji": "👀"},
    "likes":   {"title": "❤️ Активность (лайки)",       "emoji": "❤️"},
}

QUIZ_BUDGETS = {
    "small":  {"title": "💚 До 100 ₽",   "max": 100},
    "medium": {"title": "💰 До 500 ₽",   "max": 500},
    "big":    {"title": "💎 До 2000 ₽",  "max": 2000},
    "pro":    {"title": "👑 Без границ", "max": 9999999},
}

def classify_service(key: str, item: dict = None) -> str:
    name = item.get("name", "").lower() if item else ""
    k = str(key).lower()
    full_text = f"{k} {name}"
    
    # Зрители и Стримы проверяем ПЕРВЫМИ, чтобы они не попадали в Лайки
    if "live" in full_text or "зрител" in full_text or "стрим" in full_text or "эфир" in full_text: 
        return "live"
    
    if "report" in full_text or "жалоб" in full_text: return "reports"
    if "star" in full_text or "звезд" in full_text: return "stars"
    if "bot_start" in full_text or "запуск" in full_text or "старт" in full_text: return "starts"
    if "react" in full_text or "реакц" in full_text: return "reactions"
    if "save" in full_text or "сохран" in full_text or "избран" in full_text: return "saves"
    if "repost" in full_text or "retweet" in full_text or "репост" in full_text or "поделит" in full_text: return "reposts"
    if "comment" in full_text or "коммент" in full_text: return "comments"
    if "like" in full_text or "лайк" in full_text: return "likes"
    if "sub" in full_text or "подпис" in full_text or "участник" in full_text or "member" in full_text: return "subs"
    if "view" in full_text or "просмотр" in full_text or "охват" in full_text: return "views"
    if "boost" in full_text or "буст" in full_text: return "starts"
    
    return "other"

def quiz_recommend(plat, goal, budget_key):
    budget = QUIZ_BUDGETS[budget_key]["max"]
    candidates = []
    for bkey, bundle in BUNDLES.items():
        plats_in_bundle = {p for p, k, q in bundle["items"]}
        if plat not in plats_in_bundle:
            continue
        if "fixed_price" in bundle:
            final = bundle["fixed_price"]
        else:
            total = 0
            for p, k, q in bundle["items"]:
                it = SERVICES[p]["items"][k]
                unit = it["price"] / it["pack"]
                total += unit * q
            final = round(total * (1 - bundle["discount"] / 100), 2)
        if final > budget:
            continue
        keys = [k for p, k, q in bundle["items"] if p == plat]
        ok = False
        for k in keys:
            action = classify_service(k)
            if goal == "growth" and action == "subs": ok = True
            elif goal == "views" and action == "views": ok = True
            elif goal == "likes" and action in ("likes", "reactions"): ok = True
        if ok:
            candidates.append((bkey, bundle, final))
    if candidates:
        candidates.sort(key=lambda x: x[2], reverse=True)
        return ("bundle", candidates[0])
    for key, item in SERVICES[plat]["items"].items():
        action = classify_service(key, item)
        if goal == "growth" and action == "subs": return ("service", (plat, key, item))
        if goal == "views" and action == "views": return ("service", (plat, key, item))
        if goal == "likes" and action in ("likes", "reactions"): return ("service", (plat, key, item))
    return (None, None)

# ============ ЛИНКИ И ВАЛИДАЦИЯ ============
LINK_PATTERNS = {
    "telegram": ["t.me/", "telegram.me/", "telegram.org/"],
    "tiktok": ["tiktok.com/", "vm.tiktok.com/", "vt.tiktok.com/"],
    "youtube": ["youtube.com/", "youtu.be/", "www.youtube.com/"],
    "instagram": ["instagram.com/", "www.instagram.com/"],
    "vk": ["vk.com/", "vk.ru/", "m.vk.com/"],
    "twitch": ["twitch.tv/", "www.twitch.tv/"],
    "twitter": ["twitter.com/", "x.com/", "www.twitter.com/"],
    "likee": ["likee.video/", "l.likee.video/", "likee.com/"],
    "facebook": ["facebook.com/", "fb.com/", "www.facebook.com/"],
    "rutube": ["rutube.ru/", "www.rutube.ru/"],
    "max": ["max.ru/", "web.max.ru/"]
}

import re

def is_valid_link_universal(link):
    link = (link or "").strip()
    if len(link) < 2: 
        return False
    if " " in link: 
        return False
    
    # Полные ссылки (http/https)
    if re.match(r'^https?://\S+$', link, re.IGNORECASE):
        return True
    # Ссылки без протокола (vk.com/page или t.me/name)
    if re.match(r'^(www\.)?[a-zа-яё0-9-]+(\.[a-zа-яё0-9-]+)+(\/\S*)?$', link, re.IGNORECASE):
        return True
    # Юзернеймы (@username или username)
    if re.match(r'^@?[a-z0-9_]{4,32}$', link, re.IGNORECASE):
        return True
    return False
    
# ============ СОЗДАНИЕ БОТА ============
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher(storage=MemoryStorage())

crypto = AioCryptoPay(
    token=CRYPTO_PAY_TOKEN,
    network=Networks.MAIN_NET if CRYPTO_PAY_NETWORK == "mainnet" else Networks.TEST_NET
)

# ============ ЛОГИ ============
async def log_to_channel(text: str):
    if not LOG_CHANNEL_ID:
        return
    try:
        await bot.send_message(LOG_CHANNEL_ID, text)
    except Exception as e:
        print(f"Ошибка лога в канал: {e}")

async def notify_channel_new_order(order_id, user_id, username, service_name, qty, price, panel_name):
    uname = f"@{username}" if username else f"id{user_id}"
    await log_to_channel(
        f"🆕 *Новый заказ №{order_id}*\n\n"
        f"👤 {uname}\n📦 {service_name}\n🔢 {qty} шт\n"
        f"💸 {price:.2f} ₽\n🖥 Панель: `SMM`\n\n⚡️ Отправлен в работу!"
    )

async def notify_channel_topup(user_id, username, amount_rub, amount_usdt, tx_type="CryptoBot"):
    if amount_rub < 500:
        return
    uname = f"@{username}" if username else f"id{user_id}"
    await log_to_channel(
        f"💰 *Пополнение баланса*\n\n👤 {uname}\n"
        f"💵 {amount_rub:.2f} ₽ ({amount_usdt} USDT)\n🏦 {tx_type}\n\n✅ Зачислено"
    )

async def notify_channel_error(panel_name, service_name, error_text):
    await log_to_channel(
        f"⚠️ *Ошибка при заказе*\n\n🖥 Панель: `SMM`\n"
        f"📦 Услуга: {service_name}\n❌ `{str(error_text)[:200]}`\n\n💰 Возврат клиенту"
    )

async def notify_admin_error(error_text, context=""):
    try:
        await bot.send_message(ADMIN_ID,
            f"🚨 *Ошибка в боте!*\n\n📍 Контекст: `{context}`\n❌ Ошибка: `{str(error_text)[:500]}`")
    except Exception:
        pass
    await log_to_channel(f"🚨 Ошибка: `{context}` — `{str(error_text)[:200]}`")

# ============ АНТИФЛУД MIDDLEWARE ============
_flood_msg = defaultdict(list)
_flood_cb = defaultdict(list)
_flood_banned = {}

def _check_flood(bucket, user_id, limit, window):
    now = _time.time()
    bucket[user_id] = [t for t in bucket[user_id] if now - t < window]
    if len(bucket[user_id]) >= limit:
        return True
    bucket[user_id].append(now)
    return False

class FloodMessageMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user = data.get("event_from_user")
        if not user:
            return await handler(event, data)
        uid = user.id
        if uid == ADMIN_ID:
            return await handler(event, data)
        now = _time.time()
        if uid in _flood_banned:
            if now < _flood_banned[uid]:
                return
            else:
                del _flood_banned[uid]
        if _check_flood(_flood_msg, uid, FLOOD_MSG_LIMIT, FLOOD_MSG_WINDOW):
            _flood_banned[uid] = now + FLOOD_BAN_TIME
            try:
                await event.answer("🚫 Слишком много сообщений. Подождите 15 секунд.")
            except Exception:
                pass
            return
        return await handler(event, data)

class FloodCallbackMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user = data.get("event_from_user")
        if not user:
            return await handler(event, data)
        uid = user.id
        if uid == ADMIN_ID:
            return await handler(event, data)
        now = _time.time()
        if uid in _flood_banned and now < _flood_banned[uid]:
            try:
                await event.answer("🚫 Подождите 15 секунд", show_alert=False)
            except Exception:
                pass
            return
        if _check_flood(_flood_cb, uid, FLOOD_CB_LIMIT, FLOOD_CB_WINDOW):
            _flood_banned[uid] = now + FLOOD_BAN_TIME
            try:
                await event.answer("🚫 Слишком часто жмёте. Подождите 15 секунд.", show_alert=True)
            except Exception:
                pass
            return
        return await handler(event, data)

# ============ УТИЛИТЫ ============
def status_emoji(status):
    return {
        "paid": "💳", "pending": "⏳", "in_progress": "🚀",
        "partial": "⚠️", "completed": "✅", "canceled": "❌", "error": "⚠️"
    }.get(status, "ℹ️")

def progress_bar(done, total, width=10):
    try:
        done = int(done); total = int(total)
        if total <= 0: return ""
        filled = int(width * done / total)
        filled = max(0, min(width, filled))
        return "[" + "█" * filled + "░" * (width - filled) + f"] {int(100*done/total)}%"
    except Exception:
        return ""

def predict_order(plat, key, qty):
    item = SERVICES.get(plat, {}).get("items", {}).get(key)
    if not item:
        return ""
    action = classify_service(key)
    if action == "views":
        time_est = "~15 минут" if qty <= 1000 else ("~1 час" if qty <= 10000 else "~6-12 часов")
        effect = "+5-10% охвата" if qty <= 1000 else ("+15-30% охвата" if qty <= 10000 else "Высокий шанс попасть в рекомендации")
    elif action == "subs":
        time_est = "~30 минут" if qty <= 500 else ("~2 часа" if qty <= 2000 else "~12-24 часа")
        effect = "Канал станет заметнее в поиске" if qty <= 500 else "Рост органики"
    elif action == "likes":
        time_est = "~30 минут"
        effect = "Рост охвата постов"
    elif action == "reactions":
        time_est = "~1 час"
        effect = "Посты будут выглядеть живыми"
    else:
        time_est = "~1 час"
        effect = "Улучшение показателей"
    return f"\n📈 *Прогноз заказа:*\n⏱ Время: *{time_est}*\n📊 Результат: *{effect}*"

def get_weekend_discount():
    wd = datetime.now().weekday()
    return WEEKEND_DISCOUNT if wd in (4, 5, 6) else 0

def is_valid_link(platform, link):
    patterns = LINK_PATTERNS.get(platform, [])
    if not patterns:
        return True
    return any(p in link for p in patterns)

# ============ ВАЛИДАТОРЫ ССЫЛОК ПО УСЛУГАМ ============
def _is_tme_profile(link):
    link = link.strip().lower()
    if not link.startswith(("https://t.me/", "http://t.me/", "t.me/")): return False
    if any(b in link for b in ("/post/", "/c/", "?comment=", "t.me/+", "/joinchat/")): return False
    try:
        tail = link.split("t.me/", 1)[1].strip("/")
        return bool(tail) and "/" not in tail
    except IndexError:
        return False

def _is_tme_post(link):
    link = link.strip().lower()
    if not link.startswith(("https://t.me/", "http://t.me/", "t.me/")): return False
    return "/post/" in link or "/c/" in link

def _is_tiktok_video(link):
    l = link.strip().lower()
    if "vm.tiktok.com" in l or "vt.tiktok.com" in l: return True
    return "tiktok.com" in l and ("/video/" in l or "/photo/" in l)

def _is_tiktok_profile(link):
    l = link.strip().lower()
    return "tiktok.com/@" in l and "/video/" not in l

def _is_instagram_post(link):
    l = link.strip().lower()
    return "instagram.com" in l and ("/p/" in l or "/reel/" in l or "/reels/" in l or "/tv/" in l)

def _is_instagram_profile(link):
    l = link.strip().lower()
    return "instagram.com/" in l and "/p/" not in l and "/reel" not in l

def _is_youtube_video(link):
    l = link.strip().lower()
    return "youtu.be/" in l or ("youtube.com" in l and ("/watch" in l or "/shorts/" in l))

def _is_youtube_channel(link):
    l = link.strip().lower()
    return "youtube.com" in l and not ("/watch" in l or "/shorts/" in l)

def _is_vk_any(link):
    return "vk.com" in link.strip().lower() or "vk.ru" in link.strip().lower()

def _is_twitter_post(link):
    l = link.strip().lower()
    return ("twitter.com/" in l or "x.com/" in l) and "/status/" in l

def _is_twitter_profile(link):
    l = link.strip().lower()
    return ("twitter.com/" in l or "x.com/" in l) and "/status/" not in l

def _is_twitch(link):
    return "twitch.tv/" in link.strip().lower()

def _is_likee(link):
    return "likee" in link.strip().lower()

def _is_fb(link):
    l = link.strip().lower()
    return "facebook.com" in l or "fb.com" in l

def _is_rutube(link):
    return "rutube.ru/" in link.strip().lower()

def _is_max(link):
    return "max.ru/" in link.strip().lower() or "web.max.ru/" in link.strip().lower()

SERVICE_LINK_VALIDATORS = {
    "tg_stars": _is_tme_profile, "tg_subs": _is_tme_profile, "tg_views": _is_tme_post,
    "tg_bot_start": _is_tme_profile, "tg_react_pos": _is_tme_post, "tg_react_neg": _is_tme_post,
    "tt_subs": _is_tiktok_profile, "tt_views": _is_tiktok_video, "tt_likes_vingboost": _is_tiktok_video,
    "tt_saves": _is_tiktok_video, "tt_reposts": _is_tiktok_video,
    "yt_subs": _is_youtube_channel, "yt_views": _is_youtube_video, "yt_likes": _is_youtube_video,
    "ig_subs": _is_instagram_profile, "ig_likes": _is_instagram_post, "ig_views": _is_instagram_post,
    "ig_reach": _is_instagram_post, "ig_saves": _is_instagram_post, "ig_reposts": _is_instagram_post,
    "vk_subs": _is_vk_any, "vk_likes": _is_vk_any, "vk_views": _is_vk_any, "vk_reposts": _is_vk_any,
    "tw_subs": _is_twitch, "tw_views": _is_twitch, "tw_viewers": _is_twitch,
    "twt_subs": _is_twitter_profile, "twt_likes": _is_twitter_post, "twt_views": _is_twitter_post,
    "lk_subs": _is_likee, "lk_likes": _is_likee,
    "fb_subs": _is_fb,
    "rt_views1": _is_rutube, "rt_views2": _is_rutube, "rt_emojis": _is_rutube, "rt_likes": _is_rutube,
    "mx_subs": _is_max, "mx_views": _is_max, "mx_reposts": _is_max, "mx_bot_start": _is_max,
}

def validate_link_for_service(plat, key, link):
    link = (link or "").strip()
    if not link:
        return False, "⚠️ Пустая ссылка"
    if is_valid_link_universal(link):
        return True, ""
    return False, f"⚠️ Неверная ссылка для *{SERVICES[plat]['title']}*\nПроверьте формат (нужна ссылка или @username)."
    
# ============ БАЗА ДАННЫХ ============
def db_connect():
    conn = sqlite3.connect(DB_PATH, timeout=30)
    try:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA busy_timeout=30000")
    except Exception:
        pass
    return conn

def _table_columns(cur, table):
    cur.execute(f"PRAGMA table_info({table})")
    return [r[1] for r in cur.fetchall()]

def db_init():
    try:
        if os.path.exists(DB_PATH):
            conn_check = sqlite3.connect(DB_PATH, timeout=30)
            cur_check = conn_check.cursor()
            cur_check.execute("PRAGMA integrity_check")
            result = cur_check.fetchone()
            conn_check.close()
            if not result or result[0] != "ok":
                raise sqlite3.DatabaseError("База повреждена")
    except Exception as e:
        print(f"⚠️ БД повреждена: {e}. Пересоздаём...")
        if os.path.exists(DB_PATH):
            os.rename(DB_PATH, f"{DB_PATH}.broken_{int(datetime.now().timestamp())}")

conn = db_connect()
cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    balance REAL DEFAULT 0,
    lang TEXT DEFAULT 'ru',
    referrer_id INTEGER,
    reg_date TEXT,
    total_spent REAL DEFAULT 0,
    first_order_done INTEGER DEFAULT 0,
    theme_tier TEXT DEFAULT 'free')""")

cur.execute("""CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    platform TEXT,
    service_name TEXT,
    service_id TEXT,
    quantity INTEGER,
    price REAL,
    link TEXT,
    status TEXT DEFAULT 'paid',
    created_at TEXT,
    panel TEXT DEFAULT 'panel_1',
    panel_order_id INTEGER,
    panel_status TEXT DEFAULT 'pending')""")

cur.execute("""CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    invoice_id TEXT UNIQUE,
    amount_usdt REAL,
    amount_rub REAL,
    status TEXT DEFAULT 'paid',
    created_at TEXT)""")

cur.execute("""CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    order_id INTEGER,
    rating INTEGER,
    comment TEXT,
    created_at TEXT)""")


# ============================================================
# ТАБЛИЦА ДЛЯ ПЛАВНОЙ НАКРУТКИ
# ============================================================
cur.execute("""CREATE TABLE IF NOT EXISTS privat_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT, order_id INTEGER, panel TEXT, service_id TEXT,
    link TEXT, quantity INTEGER, total_qty INTEGER, step_qty INTEGER,
    days INTEGER DEFAULT 7, interval_minutes INTEGER DEFAULT 60,
    last_sent_at TEXT, last_notified_percent INTEGER DEFAULT 0,
    status TEXT DEFAULT 'active', created_at TEXT)""")

cur.execute("""CREATE TABLE IF NOT EXISTS promos (
    code TEXT PRIMARY KEY, discount INTEGER DEFAULT 5,
    uses_left INTEGER DEFAULT 100, created_at TEXT)""")

cur.execute("""CREATE TABLE IF NOT EXISTS user_promo_usage (
    user_id INTEGER, code TEXT, used_at TEXT)""")

cur.execute("""CREATE TABLE IF NOT EXISTS favorites (
    user_id INTEGER, platform TEXT, service_key TEXT, created_at TEXT,
    PRIMARY KEY (user_id, platform, service_key))""")

cur.execute("""CREATE TABLE IF NOT EXISTS vip_users (
    user_id INTEGER PRIMARY KEY, expire_date TEXT)""")

cur.execute("""CREATE TABLE IF NOT EXISTS auctions (
    id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, desc TEXT, start_price REAL,
    current_bid REAL, current_winner INTEGER, end_time TEXT, status TEXT DEFAULT 'active')""")

cur.execute("""CREATE TABLE IF NOT EXISTS promos_custom (
    id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, platform TEXT, key TEXT,
    discount INTEGER, end_time TEXT, status TEXT DEFAULT 'active')""")

# ============================================================
# МИГРАЦИИ (добавление новых колонок в старые БД)
# ============================================================
migrations = [
    ("users", "lang", "ALTER TABLE users ADD COLUMN lang TEXT DEFAULT 'ru'"),
    ("users", "referrer_id", "ALTER TABLE users ADD COLUMN referrer_id INTEGER"),
    ("users", "total_spent", "ALTER TABLE users ADD COLUMN total_spent REAL DEFAULT 0"),
    ("users", "first_order_done", "ALTER TABLE users ADD COLUMN first_order_done INTEGER DEFAULT 0"),
    ("users", "theme_tier", "ALTER TABLE users ADD COLUMN theme_tier TEXT DEFAULT 'free'"),
    ("orders", "panel_order_id", "ALTER TABLE orders ADD COLUMN panel_order_id INTEGER"),
    ("orders", "panel_status", "ALTER TABLE orders ADD COLUMN panel_status TEXT DEFAULT 'pending'"),
    ("orders", "panel", "ALTER TABLE orders ADD COLUMN panel TEXT DEFAULT 'panel_1'"),
    ("privat_orders", "days", "ALTER TABLE privat_orders ADD COLUMN days INTEGER DEFAULT 7"),
    ("privat_orders", "interval_minutes", "ALTER TABLE privat_orders ADD COLUMN interval_minutes INTEGER DEFAULT 60"),
    ("privat_orders", "last_sent_at", "ALTER TABLE privat_orders ADD COLUMN last_sent_at TEXT"),
    ("privat_orders", "last_notified_percent", "ALTER TABLE privat_orders ADD COLUMN last_notified_percent INTEGER DEFAULT 0"),
]

for table, col, sql in migrations:
    cols = _table_columns(cur, table)
    if col not in cols:
        try:
            cur.execute(sql)
            print(f"✅ Добавлена колонка {table}.{col}")
        except Exception as e:
            print(f"⚠️ {table}.{col}: {e}")

conn.commit()
conn.close()
print("✅ БД готова к работе")

# ---------- ПОЛЬЗОВАТЕЛИ ----------
def db_user_add(user_id, username, first_name, referrer_id=None):
    conn = db_connect(); cur = conn.cursor()
    cur.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
    if not cur.fetchone():
        cur.execute(
            "INSERT INTO users (user_id, username, first_name, balance, lang, referrer_id, reg_date, total_spent, first_order_done, theme_tier) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            (user_id, username or "", first_name or "", 0, "ru", referrer_id,
             datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0, 0, "free")
        )
        conn.commit()
    conn.close()

def db_get_user(user_id):
    conn = db_connect(); cur = conn.cursor()
    cur.execute(
        "SELECT user_id, username, first_name, balance, lang, referrer_id, total_spent "
        "FROM users WHERE user_id=?", (user_id,)
    )
    row = cur.fetchone(); conn.close(); return row

def db_get_balance(user_id):
    conn = db_connect(); cur = conn.cursor()
    cur.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone(); conn.close()
    return row[0] if row else 0

def db_set_balance(user_id, amount):
    conn = db_connect(); cur = conn.cursor()
    cur.execute("UPDATE users SET balance=? WHERE user_id=?", (amount, user_id))
    conn.commit(); conn.close()

def db_add_balance(user_id, amount):
    conn = db_connect(); cur = conn.cursor()
    cur.execute("UPDATE users SET balance = COALESCE(balance,0) + ? WHERE user_id=?", (amount, user_id))
    conn.commit(); conn.close()

def db_charge_balance(user_id, amount):
    conn = db_connect(); cur = conn.cursor()
    cur.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    if not row or (row[0] or 0) < amount:
        conn.close(); return False
    cur.execute("UPDATE users SET balance = balance - ? WHERE user_id=?", (amount, user_id))
    conn.commit(); conn.close(); return True

def db_add_spent(user_id, amount):
    conn = db_connect(); cur = conn.cursor()
    cur.execute("UPDATE users SET total_spent = COALESCE(total_spent,0) + ? WHERE user_id=?", (amount, user_id))
    conn.commit(); conn.close()

def db_mark_first_order(user_id):
    conn = db_connect(); cur = conn.cursor()
    cur.execute("UPDATE users SET first_order_done=1 WHERE user_id=?", (user_id,))
    conn.commit(); conn.close()

def db_is_first_order(user_id):
    conn = db_connect(); cur = conn.cursor()
    cur.execute("SELECT first_order_done FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone(); conn.close()
    return not row or (row[0] or 0) == 0

def get_user_discount(user_id):
    user = db_get_user(user_id)
    if not user: return 0
    spent = user[6] if len(user) > 6 and user[6] else 0
    if spent >= DISCOUNT_THRESHOLD: return DISCOUNT_PERCENT
    return 0

def is_vip(user_id):
    cnt, _ = db_user_orders_count(user_id)
    return cnt >= 10

def get_vip_discount(user_id):
    return 3 if is_vip(user_id) else 0

def db_set_lang(user_id, lang):
    conn = db_connect(); cur = conn.cursor()
    cur.execute("UPDATE users SET lang=? WHERE user_id=?", (lang, user_id))
    conn.commit(); conn.close()
    
# ---------- ЗАКАЗЫ ----------
def db_add_order(user_id, platform, service_name, service_id, quantity, price, link, panel="panel_1"):
    conn = db_connect(); cur = conn.cursor()
    cur.execute(
        "INSERT INTO orders (user_id, platform, service_name, service_id, quantity, price, link, status, created_at, panel) "
        "VALUES (?,?,?,?,?,?,?,?,?,?)",
        (user_id, platform, service_name, service_id, quantity, price, link, "paid",
         datetime.now().strftime("%Y-%m-%d %H:%M:%S"), panel)
    )
    oid = cur.lastrowid; conn.commit(); conn.close(); return oid

def db_set_panel_order_id(order_id, panel_order_id):
    conn = db_connect(); cur = conn.cursor()
    cur.execute("UPDATE orders SET panel_order_id=?, panel_status='in_progress' WHERE id=?",
                (panel_order_id, order_id))
    conn.commit(); conn.close()

def db_update_panel_status(order_id, panel_status):
    conn = db_connect(); cur = conn.cursor()
    cur.execute("UPDATE orders SET panel_status=?, status=? WHERE id=?",
                (panel_status, panel_status, order_id))
    conn.commit(); conn.close()

def db_get_orders_with_panel():
    conn = db_connect(); cur = conn.cursor()
    cur.execute("""
        SELECT id, user_id, panel_order_id, service_name, quantity, link, panel_status, platform, panel
        FROM orders WHERE panel_order_id IS NOT NULL
        AND panel_status NOT IN ('completed', 'canceled', 'error')
        ORDER BY id DESC LIMIT 50
    """)
    rows = cur.fetchall(); conn.close(); return rows

def db_user_orders(user_id, limit=20, status_filter=None):
    conn = db_connect(); cur = conn.cursor()
    if status_filter:
        cur.execute("""
            SELECT id, platform, service_name, quantity, price, status, created_at
            FROM orders WHERE user_id=? AND status=? ORDER BY id DESC LIMIT ?
        """, (user_id, status_filter, limit))
    else:
        cur.execute("""
            SELECT id, platform, service_name, quantity, price, status, created_at
            FROM orders WHERE user_id=? ORDER BY id DESC LIMIT ?
        """, (user_id, limit))
    rows = cur.fetchall(); conn.close(); return rows

def db_all_orders(limit=30):
    conn = db_connect(); cur = conn.cursor()
    cur.execute("""
        SELECT id, user_id, platform, service_name, quantity, price, status, link, created_at
        FROM orders ORDER BY id DESC LIMIT ?
    """, (limit,))
    rows = cur.fetchall(); conn.close(); return rows

def db_orders_today():
    conn = db_connect(); cur = conn.cursor()
    cur.execute("""
        SELECT id, user_id, platform, service_name, quantity, price, status, link, created_at
        FROM orders WHERE DATE(created_at)=DATE('now') ORDER BY id DESC
    """)
    rows = cur.fetchall(); conn.close(); return rows

def db_update_order_status(order_id, status):
    conn = db_connect(); cur = conn.cursor()
    cur.execute("UPDATE orders SET status=? WHERE id=?", (status, order_id))
    conn.commit(); conn.close()

def db_get_order(order_id, user_id):
    conn = db_connect(); cur = conn.cursor()
    cur.execute(
        "SELECT platform, service_name, service_id, quantity, link FROM orders WHERE id=? AND user_id=?",
        (order_id, user_id)
    )
    row = cur.fetchone(); conn.close(); return row

def db_get_order_admin(order_id):
    conn = db_connect(); cur = conn.cursor()
    cur.execute("""
        SELECT id, user_id, platform, service_name, service_id, quantity, price,
        link, status, created_at, panel, panel_order_id, panel_status
        FROM orders WHERE id=?
    """, (order_id,))
    row = cur.fetchone()
    if not row:
        cur.execute("""
            SELECT id, user_id, platform, service_name, service_id, quantity, price,
            link, status, created_at, panel, panel_order_id, panel_status
            FROM orders WHERE panel_order_id=?
        """, (order_id,))
        row = cur.fetchone()
    conn.close(); return row

def db_count_orders_today(user_id):
    conn = db_connect(); cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM orders WHERE user_id=? AND DATE(created_at)=DATE('now')", (user_id,))
    row = cur.fetchone(); conn.close(); return row[0] if row else 0

def db_sum_orders_last_hour(user_id):
    conn = db_connect(); cur = conn.cursor()
    cur.execute(
        "SELECT COALESCE(SUM(price),0) FROM orders WHERE user_id=? AND created_at >= datetime('now', '-1 hour')",
        (user_id,)
    )
    row = cur.fetchone(); conn.close(); return row[0] if row else 0

def db_orders_today_sum(user_id):
    conn = db_connect(); cur = conn.cursor()
    cur.execute("""
        SELECT COALESCE(SUM(price),0) FROM orders
        WHERE user_id=? AND DATE(created_at)=DATE('now')
    """, (user_id,))
    row = cur.fetchone(); conn.close()
    return row[0] if row else 0

def db_orders_last_hour(user_id):
    conn = db_connect(); cur = conn.cursor()
    cur.execute(
        "SELECT COUNT(*) FROM orders WHERE user_id=? AND created_at >= datetime('now', '-1 hour')",
        (user_id,)
    )
    row = cur.fetchone(); conn.close(); return row[0] if row else 0

def db_user_orders_count(user_id):
    conn = db_connect(); cur = conn.cursor()
    cur.execute("SELECT COUNT(*), COALESCE(SUM(price),0) FROM orders WHERE user_id=?", (user_id,))
    row = cur.fetchone(); conn.close(); return row if row else (0, 0)

def db_user_has_ordered_on_platform(user_id, platform):
    conn = db_connect(); cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM orders WHERE user_id=? AND platform=?", (user_id, platform))
    row = cur.fetchone(); conn.close()
    return (row[0] if row else 0) > 0

def db_get_users():
    conn = db_connect(); cur = conn.cursor()
    cur.execute("SELECT user_id, username, first_name, balance FROM users ORDER BY user_id")
    rows = cur.fetchall(); conn.close(); return rows

def db_stats():
    conn = db_connect(); cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users"); users = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM orders"); orders = cur.fetchone()[0]
    cur.execute("SELECT COALESCE(SUM(price),0) FROM orders"); total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM orders WHERE DATE(created_at)=DATE('now')"); today = cur.fetchone()[0]
    cur.execute("SELECT COALESCE(SUM(price),0) FROM orders WHERE DATE(created_at)=DATE('now')"); today_sum = cur.fetchone()[0]
    conn.close(); return users, orders, total, today, today_sum

def db_top_today():
    conn = db_connect(); cur = conn.cursor()
    cur.execute("""
        SELECT service_name, COUNT(*), COALESCE(SUM(price),0) FROM orders
        WHERE DATE(created_at)=DATE('now') GROUP BY service_id ORDER BY COUNT(*) DESC LIMIT 3
    """)
    top = cur.fetchall()
    cur.execute("""
        SELECT user_id, COUNT(*), COALESCE(SUM(price),0) FROM orders
        WHERE DATE(created_at)=DATE('now') GROUP BY user_id ORDER BY SUM(price) DESC LIMIT 3
    """)
    top_users = cur.fetchall(); conn.close(); return top, top_users

def db_top_services(limit=5):
    conn = db_connect(); cur = conn.cursor()
    cur.execute("""
        SELECT service_id, service_name, platform, COUNT(*) as cnt
        FROM orders GROUP BY service_id ORDER BY cnt DESC LIMIT ?
    """, (limit,))
    rows = cur.fetchall(); conn.close(); return rows

# ---------- ПЛАТЕЖИ ----------
def db_save_payment(user_id, invoice_id, amount_usdt, amount_rub, status="paid"):
    conn = db_connect(); cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO payments (user_id, invoice_id, amount_usdt, amount_rub, status, created_at) "
            "VALUES (?,?,?,?,?,?)",
            (user_id, invoice_id, amount_usdt, amount_rub, status,
             datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit(); return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def db_user_payments(user_id, limit=20):
    conn = db_connect(); cur = conn.cursor()
    cur.execute(
        "SELECT id, amount_usdt, amount_rub, status, created_at FROM payments WHERE user_id=? ORDER BY id DESC LIMIT ?",
        (user_id, limit)
    )
    rows = cur.fetchall(); conn.close(); return rows

# ---------- РЕФЕРАЛЫ ----------
def db_ref_count(user_id):
    conn = db_connect(); cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users WHERE referrer_id=?", (user_id,))
    row = cur.fetchone(); conn.close(); return row[0] if row else 0

def db_ref_earned(user_id):
    conn = db_connect(); cur = conn.cursor()
    cur.execute("""
        SELECT COALESCE(SUM(price),0) FROM orders WHERE user_id IN
        (SELECT user_id FROM users WHERE referrer_id=?)
    """, (user_id,))
    row = cur.fetchone(); conn.close()
    total = row[0] if row else 0
    return round(total * REF_BONUS_PERCENT / 100, 2)

def db_ref_list(user_id, limit=REF_STATS_LIMIT):
    conn = db_connect(); cur = conn.cursor()
    cur.execute("""
        SELECT u.user_id, u.username, u.first_name, u.reg_date,
        COALESCE((SELECT COUNT(*) FROM orders WHERE user_id=u.user_id), 0),
        COALESCE((SELECT SUM(price) FROM orders WHERE user_id=u.user_id), 0)
        FROM users u WHERE u.referrer_id=? ORDER BY u.reg_date DESC LIMIT ?
    """, (user_id, limit))
    rows = cur.fetchall(); conn.close(); return rows

def db_find_user_by_username(username):
    conn = db_connect(); cur = conn.cursor()
    u = username.lstrip("@").lower()
    cur.execute(
        "SELECT user_id, username, first_name, balance, reg_date, total_spent FROM users WHERE LOWER(username)=?",
        (u,)
    )
    row = cur.fetchone(); conn.close(); return row

# ---------- ОТЗЫВЫ ----------
def db_add_review(user_id, order_id, rating, comment=""):
    conn = db_connect(); cur = conn.cursor()
    cur.execute(
        "INSERT INTO reviews (user_id, order_id, rating, comment, created_at) VALUES (?,?,?,?,?)",
        (user_id, order_id, rating, comment,
         datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit(); conn.close()

def db_reviews_avg():
    conn = db_connect(); cur = conn.cursor()
    cur.execute("SELECT COUNT(*), COALESCE(AVG(rating),0) FROM reviews")
    row = cur.fetchone(); conn.close()
    return row[0], round(row[1], 2)

def db_last_reviews(limit=5):
    conn = db_connect(); cur = conn.cursor()
    cur.execute("SELECT user_id, rating, comment, created_at FROM reviews ORDER BY id DESC LIMIT ?", (limit,))
    rows = cur.fetchall(); conn.close(); return rows

def db_review_delete(review_id):
    conn = db_connect(); cur = conn.cursor()
    cur.execute("DELETE FROM reviews WHERE id=?", (review_id,))
    conn.commit(); conn.close()

def db_reviews_list(limit=50):
    conn = db_connect(); cur = conn.cursor()
    cur.execute("SELECT id, user_id, rating, comment, created_at FROM reviews ORDER BY id DESC LIMIT ?", (limit,))
    rows = cur.fetchall(); conn.close(); return rows

# ---------- ТИКЕТЫ ----------
def db_add_ticket(user_id, username, message):
    conn = db_connect(); cur = conn.cursor()
    cur.execute(
        "INSERT INTO tickets (user_id, username, message, status, created_at) VALUES (?,?,?,?,?)",
        (user_id, username or "", message, "open",
         datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    tid = cur.lastrowid; conn.commit(); conn.close(); return tid

def db_open_tickets():
    conn = db_connect(); cur = conn.cursor()
    cur.execute("SELECT id, user_id, username, message, created_at FROM tickets WHERE status='open' ORDER BY id")
    rows = cur.fetchall(); conn.close(); return rows

def db_close_ticket(ticket_id, answer):
    conn = db_connect(); cur = conn.cursor()
    cur.execute("UPDATE tickets SET status='closed', answer=? WHERE id=?", (answer, ticket_id))
    conn.commit(); conn.close()

def db_get_ticket_user(ticket_id):
    conn = db_connect(); cur = conn.cursor()
    cur.execute("SELECT user_id FROM tickets WHERE id=?", (ticket_id,))
    row = cur.fetchone(); conn.close(); return row

# ---------- ПРОМОКОДЫ ----------
def db_promo_get(code):
    conn = db_connect(); cur = conn.cursor()
    cur.execute("SELECT code, discount, uses_left FROM promos WHERE code=?", (code.upper(),))
    row = cur.fetchone(); conn.close(); return row

def db_promo_add(code, discount, uses=100):
    conn = db_connect(); cur = conn.cursor()
    try:
        cur.execute("INSERT INTO promos (code, discount, uses_left, created_at) VALUES (?,?,?,?)",
                    (code.upper(), discount, uses, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit(); return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def db_promo_use(code):
    conn = db_connect(); cur = conn.cursor()
    cur.execute("UPDATE promos SET uses_left = uses_left - 1 WHERE code=?", (code.upper(),))
    conn.commit(); conn.close()

def db_promo_used_by_user(user_id, code):
    conn = db_connect(); cur = conn.cursor()
    cur.execute("SELECT 1 FROM user_promo_usage WHERE user_id=? AND code=?", (user_id, code.upper()))
    row = cur.fetchone(); conn.close(); return row is not None

def db_promo_mark_user(user_id, code):
    conn = db_connect(); cur = conn.cursor()
    cur.execute("INSERT INTO user_promo_usage (user_id, code, used_at) VALUES (?,?,?)",
                (user_id, code.upper(), datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit(); conn.close()

def db_promo_list():
    conn = db_connect(); cur = conn.cursor()
    cur.execute("SELECT code, discount, uses_left FROM promos ORDER BY code")
    rows = cur.fetchall(); conn.close(); return rows

def db_promo_delete(code):
    conn = db_connect(); cur = conn.cursor()
    cur.execute("DELETE FROM promos WHERE code=?", (code.upper(),))
    conn.commit(); conn.close()

def generate_promo_code(length=8):
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choice(chars) for _ in range(length))

# ---------- ИЗБРАННОЕ ----------
def db_fav_add(user_id, platform, service_key):
    conn = db_connect(); cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO favorites (user_id, platform, service_key, created_at) VALUES (?,?,?,?)",
            (user_id, platform, service_key, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit(); return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def db_fav_remove(user_id, platform, service_key):
    conn = db_connect(); cur = conn.cursor()
    cur.execute("DELETE FROM favorites WHERE user_id=? AND platform=? AND service_key=?",
                (user_id, platform, service_key))
    conn.commit(); conn.close()

def db_fav_is(user_id, platform, service_key):
    conn = db_connect(); cur = conn.cursor()
    cur.execute("SELECT 1 FROM favorites WHERE user_id=? AND platform=? AND service_key=?",
                (user_id, platform, service_key))
    row = cur.fetchone(); conn.close(); return row is not None

def db_fav_list(user_id):
    conn = db_connect(); cur = conn.cursor()
    cur.execute("SELECT platform, service_key FROM favorites WHERE user_id=? ORDER BY created_at DESC", (user_id,))
    rows = cur.fetchall(); conn.close(); return rows

# ---------- АУКЦИОН ----------
def db_get_active_auction():
    conn = db_connect(); cur = conn.cursor()
    cur.execute(
        "SELECT id, title, desc, start_price, current_bid, current_winner, end_time "
        "FROM auctions WHERE status='active' AND end_time > datetime('now') "
        "ORDER BY id DESC LIMIT 1"
    )
    row = cur.fetchone(); conn.close(); return row

def db_place_bid(auction_id, user_id, amount):
    conn = db_connect(); cur = conn.cursor()
    cur.execute("SELECT current_bid FROM auctions WHERE id=?", (auction_id,))
    row = cur.fetchone()
    if not row or amount <= row[0]:
        conn.close(); return False
    cur.execute("UPDATE auctions SET current_bid=?, current_winner=? WHERE id=?",
                (amount, user_id, auction_id))
    conn.commit(); conn.close(); return True

def db_add_auction(title, desc, start_price, hours):
    conn = db_connect(); cur = conn.cursor()
    end_time = (datetime.now() + timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M:%S")
    cur.execute(
        "INSERT INTO auctions (title, desc, start_price, current_bid, current_winner, end_time, status) "
        "VALUES (?,?,?,?,?,?,?)",
        (title, desc, start_price, start_price, None, end_time, "active")
    )
    conn.commit(); conn.close()

# ---------- АКЦИИ ----------
def db_get_active_promos():
    conn = db_connect(); cur = conn.cursor()
    cur.execute(
        "SELECT id, title, platform, key, discount, end_time FROM promos_custom "
        "WHERE status='active' AND end_time > datetime('now')"
    )
    rows = cur.fetchall(); conn.close(); return rows

def db_add_custom_promo(title, platform, key, discount, hours):
    conn = db_connect(); cur = conn.cursor()
    end_time = (datetime.now() + timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M:%S")
    cur.execute(
        "INSERT INTO promos_custom (title, platform, key, discount, end_time) VALUES (?,?,?,?,?)",
        (title, platform, key, discount, end_time)
    )
    conn.commit(); conn.close()

# ---------- VIP ----------
def db_is_vip_active(user_id):
    conn = db_connect(); cur = conn.cursor()
    cur.execute("SELECT expire_date FROM vip_users WHERE user_id=?", (user_id,))
    row = cur.fetchone(); conn.close()
    if not row: return False
    try:
        return datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S") > datetime.now()
    except Exception:
        return False

def db_grant_vip(user_id, days=30):
    conn = db_connect(); cur = conn.cursor()
    expire = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("INSERT OR REPLACE INTO vip_users (user_id, expire_date) VALUES (?, ?)", (user_id, expire))
    conn.commit(); conn.close()
    
# ============ API ПАНЕЛЕЙ ============
async def panel_add_order(panel_name, service_id, link, quantity, retries=2):
    panel = PANELS.get(panel_name)
    if not panel:
        return None, f"panel_not_found: {panel_name}"
    last_error = None
    for attempt in range(retries + 1):
        try:
            async with aiohttp.ClientSession() as s:
                payload = {
                    "key": panel["key"], "action": "add",
                    "service": int(service_id),
                    "link": link, "quantity": int(quantity)
                }
                async with s.post(
                    panel["url"], data=payload,
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as r:
                    data = await r.json()
                if "order" in data:
                    return data["order"], None
                if "order_id" in data:
                    return data["order_id"], None
                err = data.get("error", data.get("message", "unknown_error"))
                if "insufficient" in str(err).lower() or "funds" in str(err).lower():
                    return None, err
                last_error = err
        except Exception as e:
            last_error = f"connection_error: {e}"
        if attempt < retries:
            await asyncio.sleep(3)
    return None, last_error

async def panel_check_status(panel_name, panel_order_id):
    panel = PANELS.get(panel_name)
    if not panel:
        return None, None, None
    try:
        async with aiohttp.ClientSession() as s:
            async with s.post(
                panel["url"],
                data={"key": panel["key"], "action": "status", "order": panel_order_id},
                timeout=aiohttp.ClientTimeout(total=15)
            ) as r:
                data = await r.json()
            if "status" not in data:
                return None, None, None
            raw = data["status"]
            norm = {
                "Pending": "pending", "In progress": "in_progress",
                "Processing": "in_progress", "Completed": "completed",
                "Partial": "partial", "Canceled": "canceled"
            }.get(raw, "in_progress")
            return norm, data.get("start_count", 0), data.get("remains", 0)
    except Exception:
        return None, None, None

async def panel_get_balance(panel_name):
    panel = PANELS.get(panel_name)
    if not panel:
        return None
    try:
        async with aiohttp.ClientSession() as s:
            async with s.post(
                panel["url"],
                data={"key": panel["key"], "action": "balance"},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as r:
                data = await r.json()
            bal = data.get("balance")
            if bal is not None:
                return float(bal)
    except Exception:
        pass
    return None

# ---------- МУЛЬТИЯЗЫЧНОСТЬ ----------
TEXTS = {
    "ru": {
        "welcome": "👋 Привет! Вы на сервисе *ismaboost* — накрутка для соцсетей! 💫\n\n🔥 Умные люди юзают Ismaboost и залетают в тренды!\n\n💰 Цены — копейки!\n🤖 Всё на автомате!",
        "choose_platform": "👇 Выбери платформу:",
        "limit_exceeded": "🚫 Превышен лимит заказов в час. Попробуйте позже.",
        "daily_limit": "🚫 Достигнут дневной лимит заказов. Возвращайтесь завтра!",
        "sum_limit": "🚫 Превышен лимит суммы заказов за час. Попробуйте позже.",
        "ref_fraud": "🚫 Нельзя заказывать по своей же реферальной ссылке.",
    },
    "en": {
        "welcome": "👋 Hi! You are on *ismaboost* — social media boosting service! 💫",
        "choose_platform": "👇 Choose platform:",
        "limit_exceeded": "🚫 Hourly limit exceeded. Try later.",
        "daily_limit": "🚫 Daily limit reached. Come back tomorrow!",
        "sum_limit": "🚫 Hourly sum limit exceeded. Try later.",
        "ref_fraud": "🚫 You can't order on your own referral link.",
    }
}

def T(user_id, key):
    user = db_get_user(user_id)
    lang = user[4] if user and len(user) > 4 and user[4] else "ru"
    return TEXTS.get(lang, TEXTS["ru"]).get(key, key)

# ---------- КЛАВИАТУРЫ ----------
def main_menu_kb(user_id=None):
    url = WEBAPP_URL
    if user_id:
        orders_cnt, _ = db_user_orders_count(user_id)
        url = f"{WEBAPP_URL}&orders={orders_cnt}"
        
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Открыть Mini App", web_app=WebAppInfo(url=url))],
            [KeyboardButton(text="📦 Услуги"), KeyboardButton(text="⚡Доп. услуги")],
            [KeyboardButton(text="💰 Баланс"), KeyboardButton(text="👤 Профиль")],
            [KeyboardButton(text="⭐ Избранное"), KeyboardButton(text="⭐ Отзывы")],
            [KeyboardButton(text="🔥 Топ"), KeyboardButton(text="🎓 Школа накрутки")],
            [KeyboardButton(text="📢 Наш канал")],
            [KeyboardButton(text="✨🆘✨ ПОДДЕРЖКА ✨🆘✨")]
        ],
        resize_keyboard=True
    )

def platforms_kb():
    kb = [
        [InlineKeyboardButton(text="✈️ Telegram", callback_data="plat_telegram")],
        [InlineKeyboardButton(text="🎵 TikTok", callback_data="plat_tiktok")],
        [InlineKeyboardButton(text="▶️ YouTube", callback_data="plat_youtube")],
        [InlineKeyboardButton(text="📸 Instagram", callback_data="plat_instagram")],
        [InlineKeyboardButton(text="🅱️ ВКонтакте", callback_data="plat_vk")],
        [InlineKeyboardButton(text="🎮 Twitch", callback_data="plat_twitch")],
        [InlineKeyboardButton(text="🐦 Twitter (X)", callback_data="plat_twitter")],
        [InlineKeyboardButton(text="🎬 Likee", callback_data="plat_likee")],
        [InlineKeyboardButton(text="📘 Facebook", callback_data="plat_facebook")],
        [InlineKeyboardButton(text="🟣 Rutube", callback_data="plat_rutube")],
        [InlineKeyboardButton(text="💠 MAX", callback_data="plat_max")],
        [InlineKeyboardButton(text="🟢 WhatsApp", callback_data="plat_whatsapp")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

# ---------- FSM СОСТОЯНИЯ ----------
class OrderStates(StatesGroup):
    waiting_quantity = State()
    waiting_link = State()
    waiting_topup_amount = State()
    waiting_promo = State()
    bundle_waiting_link = State()
    waiting_gift_username = State()
    waiting_gift_quantity = State()
    waiting_gift_link = State()
    waiting_cart_qty = State()
    waiting_cart_link = State()
    waiting_br_server = State()
    waiting_br_nick = State()
    waiting_game_amount = State()
    waiting_cp_amount = State()
    waiting_bid = State()
    waiting_smooth_days = State()
    waiting_smooth_interval = State()
    waiting_smooth_custom_days = State()
    waiting_smooth_custom_interval = State()

class AdminStates(StatesGroup):
    waiting_broadcast = State()
    waiting_balance = State()
    waiting_status = State()
    waiting_promo_code = State()
    waiting_promo_discount = State()
    waiting_promo_uses = State()
    waiting_review_delete = State()
    waiting_order_find = State()
    waiting_user_find = State()
    waiting_edit_price = State()
    waiting_promo_bulk = State()
    waiting_auction_title = State()
    waiting_auction_desc = State()
    waiting_auction_price = State()
    waiting_auction_hours = State()

class ReviewStates(StatesGroup):
    waiting_rating = State()
    waiting_comment = State()

class TicketStates(StatesGroup):
    waiting_message = State()

# ---------- /start ----------
@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    referrer_id = None
    args = message.text.split()

    if len(args) > 1 and args[1].startswith("weborder_"):
        try:
            import urllib.parse, base64
            raw_data = args[1].replace("weborder_", "")
            try:
                decoded = base64.b64decode(raw_data.encode()).decode("utf-8")
                order_data = json.loads(decoded)
            except Exception:
                order_data = json.loads(urllib.parse.unquote(raw_data))

            markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Да, оплатить", callback_data="pay_yes")],
                [InlineKeyboardButton(text="❌ Отмена", callback_data="pay_no")]
            ])
            await state.update_data(
                pay_plat=order_data.get("plat"),
                pay_key=order_data.get("service"),
                pay_link=order_data.get("link"),
                pay_qty=order_data.get("qty"),
                pay_price=float(order_data.get("price")),
                pay_name=order_data.get("name"),
                pay_username=message.from_user.username,
                pay_first_name=message.from_user.first_name,
                pay_is_gift=order_data.get("is_gift", False),
                pay_gift_target=order_data.get("gift_target"),
                pay_priv_days=order_data.get("priv_days", 0),
            )
            
            smooth_line = f"\n🐢 *Плавно:* {order_data['priv_days']} дней" if order_data.get("priv_days") and int(order_data.get("priv_days")) >= 3 else ""
            
            await message.answer(
                f"💳 *Подтверждение заказа*\n\n"
                f"📱 Платформа: {str(order_data.get('plat')).capitalize()}\n"
                f"📦 Услуга: {order_data.get('name')}\n"
                f"🔢 Количество: {order_data.get('qty')} шт.\n"
                f"🔗 Ссылка: `{order_data.get('link')}`\n"
                f"💰 К оплате: *{float(order_data.get('price')):.2f} ₽*{smooth_line}\n\n"
                f"Подтверждаете покупку?",
                reply_markup=markup
            )
            return
        except Exception as e:
            logging.error(f"Ошибка парсинга weborder: {e}")

    if len(args) > 1 and args[1].startswith("ref"):
        try:
            ref = int(args[1].replace("ref", ""))
            if ref != message.from_user.id:
                referrer_id = ref
        except ValueError:
            pass

    is_new = db_get_user(message.from_user.id) is None
    db_user_add(message.from_user.id, message.from_user.username, message.from_user.first_name, referrer_id)
    balance = db_get_balance(message.from_user.id)

    header = T(message.from_user.id, "welcome")
    bal_line = f"\n\n💰 Ваш баланс: *{balance:.2f} ₽*"
    if balance < LOW_BALANCE_THRESHOLD:
        bal_line += f"\n⚠️ _Пополните баланс в Mini App для заказов_"
        
    await message.answer(header + bal_line)
    
    if is_new:
        await message.answer(f"🎁 *Бонус новичка!*\n\nСкидка *{FIRST_ORDER_DISCOUNT}%* на первый заказ применяется автоматически!")
    
    # Эта строка убирает старую Reply-клавиатуру (те кнопки со 2 скрина)
    await message.answer("👇 *Главное меню:*", reply_markup=ReplyKeyboardRemove())
    
    # Эта строка присылает новое красивое инлайн-меню
    await message.answer("Выберите действие ниже:", reply_markup=main_menu_kb(message.from_user.id))

@dp.callback_query(F.data == "quick_top")
async def cb_quick_top(call: CallbackQuery):
    await msg_top(call.message)
    await call.answer()

@dp.message(OrderStates.waiting_topup_amount)
async def process_topup_amount(message: Message, state: FSMContext):
    if not message.text or not message.text.strip().isdigit():
        await message.answer("⚠️ Пожалуйста, введи число (например: `500`). Буквы не принимаются 🙅‍♂️", parse_mode="Markdown")
        return
        
    amount = int(message.text.strip())
    
    if amount < 100:
        await message.answer(
            f"🚫 **Сумма слишком маленькая!**\n\n"
            f"Ты ввел: *{amount} ₽*\n"
            f"❗️ Минимальная сумма — **100 ₽** (защита карт от блокировки).\n\n"
            f"👇 Попробуй снова, введи от 100 ₽:",
            parse_mode="Markdown"
        )
        return
        
    if amount > 50000:
        await message.answer("⚠️ Максимальная сумма за один раз — 50 000 ₽. Напиши сумму поменьше.")
        return

    data = await state.get_data()
    topup_type = data.get("topup_type", "crypto")
    await state.clear()

    if topup_type == "crypto":
        # Создаем счет через CryptoBot
        await create_topup_invoice(message.from_user.id, amount)
    else:
        # Для СБП просим прислать чек
        await message.answer(
            f"✅ **Сумма указана:** *{amount} ₽*\n\n"
            f"📸 Теперь, пожалуйста, **пришли скриншот чека** (или файл) об оплате прямо в этот чат.\n"
            f"⏳ Администратор проверит его и зачислит баланс в течение 15 минут!",
            parse_mode="Markdown"
        )
        
@dp.message(F.photo)
async def handle_sbp_receipt(message: Message):
    # Проверяем, что юзер реально в процессе пополнения (опционально)
    # Для простоты принимаем любое фото и пересылаем админу
    
    user = message.from_user
    caption = f"🧾 **Новый чек СБП!**\n\n👤 От: @{user.username or user.first_name} (ID: `{user.id}`)"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить и начислить", callback_data=f"approve_sbp_{user.id}")]
    ])
    
    try:
        # Пересылаем фото админу
        await bot.send_photo(
            chat_id=ADMIN_ID,
            photo=message.photo[-1].file_id,
            caption=caption,
            reply_markup=kb,
            parse_mode="Markdown"
        )
        await message.answer("✅ **Чек отправлен на проверку!**\n\n⏳ Ожидай зачисления баланса (до 15 минут). Спасибо! ❤️")
    except Exception as e:
        await message.answer(f"⚠️ Ошибка при отправке чека админу. Напиши в поддержку @{SUPPORT_USERNAME}")

@dp.callback_query(F.data == "quick_repeat")
async def cb_quick_repeat(call: CallbackQuery, state: FSMContext):
    orders = db_user_orders(call.from_user.id, 1)
    if not orders:
        await call.answer("📭 У вас ещё не было заказов", show_alert=True)
        return
    oid = orders[0][0]
    fake = call.model_copy(update={"data": f"repeat_{oid}"})
    await cb_repeat_order(fake, state)
    
# --- ОБРАБОТЧИКИ КНОПОК ИЗ ГЛАВНОГО МЕНЮ ---

@dp.message(F.text == "📦 Услуги")
async def msg_services(message: Message):
    await show_platforms_page(message, 0)

async def show_platforms_page(message: Message, page: int):
    platforms = list(SERVICES.keys())
    ITEMS_PER_PAGE = 6
    total_pages = (len(platforms) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    page = max(0, min(page, total_pages - 1))
    
    start = page * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    current_platforms = platforms[start:end]
    
    kb_rows = []
    row = []
    plat_names = {
        "telegram": "✈️ Telegram", "tiktok": "🎵 TikTok", "youtube": "▶️ YouTube",
        "instagram": "📸 Instagram", "vk": "🅱️ ВКонтакте", "twitch": "🎮 Twitch",
        "twitter": "🐦 Twitter (X)", "likee": "🎬 Likee", "facebook": "📘 Facebook",
        "rutube": "🟣 Rutube", "max": "💠 MAX", "whatsapp": "🟢 WhatsApp"
    }
    
    for p in current_platforms:
        title = plat_names.get(p, p.upper())
        row.append(InlineKeyboardButton(text=title, callback_data=f"plat_{p}"))
        if len(row) == 2:
            kb_rows.append(row)
            row = []
    if row:
        kb_rows.append(row)
        
    # Кнопки навигации (Назад / Страница / Вперед)
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"page_plat_{page-1}"))
    nav_row.append(InlineKeyboardButton(text=f"📄 {page+1}/{total_pages}", callback_data="noop"))
    if page < total_pages - 1:
        nav_row.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"page_plat_{page+1}"))
    if nav_row:
        kb_rows.append(nav_row)

    await message.answer("👇 Выберите платформу:", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows))

@dp.callback_query(F.data.startswith("page_plat_"))
async def cb_page_plat(call: CallbackQuery):
    page = int(call.data.replace("page_plat_", ""))
    # Удаляем старое сообщение и шлем новое с кнопками
    await call.message.delete()
    await show_platforms_page(call.message, page)
    await call.answer()
    

@dp.message(F.text == "💎 Доп. услуги")
async def msg_extra_services(message: Message):
    # Заглушка, чтобы кнопка не выдавала ошибку "is not handled". 
    # Сюда можешь добавить вывод доп. услуг, если они есть.
    await message.answer("💎 Раздел дополнительных услуг в разработке.\n\nА пока загляни в '📦 Услуги' или '⚡ Каталог VexBoost'!")

@dp.message(F.text == "👤 Профиль")
async def msg_profile_button(message: Message):
    await msg_profile(message) # Вызываем существующую функцию профиля

@dp.message(F.text == "⭐ Избранное")
async def msg_favorites_button(message: Message):
    await msg_favorites(message) # Вызываем существующую функцию избранного

@dp.message(F.text == "⭐ Отзывы")
async def msg_reviews_button(message: Message):
    await msg_reviews_main(message) # Вызываем существующую функцию отзывов

@dp.message(F.text == "🔥 Топ")
async def msg_top_button(message: Message):
    await msg_top(message) # Вызываем существующую функцию топа

@dp.message(F.text == "🎓 Школа накрутки")
async def msg_school_button(message: Message):
    await msg_school(message) # Вызываем существующую функцию школы

# (Обработчики "Баланс", "Наш канал" и "Поддержка" у тебя уже есть в коде, их не трогаем)

# ---------- УСЛУГИ ----------
@dp.message(F.text == "📦 Услуги")
async def msg_services(message: Message):
    await message.answer(
        "💥 Что мы предлагаем: 🎯\n\n👥 Подписчики / ❤️ Лайки / 👀 Просмотры\n💬 Реакции / 🔁 Репосты / 💾 Сохранения\n🌟 Звёзды / 🚨 Жалобы на TG-аккаунты\n\n✨ 11 платформ и 5 игр, 250+ услуг!\n\n👇 Выбери платформу:",
        reply_markup=platforms_kb()
    )

@dp.message(F.text == "💰 Баланс")
async def msg_balance_button(message: Message):
    user = db_get_user(message.from_user.id)
    if not user:
        await message.answer("Напишите /start")
        return
    bal = user[3] or 0
    await message.answer(
        f"💰 *Ваш баланс:* {bal:.2f} ₽\n\n"
        f"👇 Для пополнения нажмите кнопку ниже:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💳 Пополнить", callback_data="topup")]
        ])
    )
    
@dp.message(F.text == "✨🆘✨ ПОДДЕРЖКА ✨🆘✨")
async def msg_beautiful_support(message: Message):
    text = (
        "✨💎 **ЦЕНТР ПОДДЕРЖКИ ISMABOOST** 💎✨\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "👋 Привет! Мы всегда на связи и готовы помочь.\n\n"
        "🛠 **Если у тебя:**\n"
        "❓ Вопрос по заказу\n"
        "💳 Проблема с оплатой\n"
        "🔄 Нужен возврат или замена\n"
        "💡 Есть предложение\n\n"
        "👇 **Нажми на кнопку ниже, чтобы написать нам напрямую!**\n"
        "⏳ *Среднее время ответа: 5-15 минут*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🚀 *Мы работаем 24/7 для тебя!* ❤️"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Написать в поддержку", url=f"https://t.me/{SUPPORT_USERNAME}")],
        [InlineKeyboardButton(text="📢 Наш канал (новости)", url=CHANNEL_URL)]
    ])
    await message.answer(text, reply_markup=kb, parse_mode="Markdown")
    
@dp.message(F.text == "📢 Наш канал")
async def msg_channel(message: Message):
    await message.answer(
        f"📢 *Наш канал*\n\nПодписывайтесь — там анонсы, промокоды и бонусы:\n\n👉 {CHANNEL_URL}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="📢 Подписаться", url=CHANNEL_URL)]])
    )

# ---------- ПРОФИЛЬ ----------
@dp.message(F.text == "👤 Профиль")
async def msg_profile(message: Message):
    user = db_get_user(message.from_user.id)
    if not user:
        await message.answer("Напишите /start")
        return
    uid, uname, fname, bal, lang, ref_id, spent = user
    ref_count = db_ref_count(uid)
    ref_earned = db_ref_earned(uid)
    me = await bot.me()
    ref_link = f"https://t.me/{me.username}?start=ref{uid}"
    reviews_count, reviews_avg = db_reviews_avg()
    discount = get_user_discount(uid)
    vip_mark = "💎 " if is_vip(uid) else ""
    spent = spent or 0
    discount_info = f"\n💎 *Скидка:* {discount}% (потрачено ≥{DISCOUNT_THRESHOLD} ₽)" if discount else f"\n💎 До скидки {DISCOUNT_PERCENT}%: осталось {DISCOUNT_THRESHOLD - spent:.0f} ₽"
    orders_today = db_count_orders_today(uid)
    sum_today = db_orders_today_sum(uid)
    
    def _bar(done, total, width=10):
        filled = int(width * done / total) if total else 0
        filled = max(0, min(width, filled))
        return "█" * filled + "░" * (width - filled)
        
    orders_bar = _bar(orders_today, MAX_ORDERS_PER_DAY)
    sum_bar = _bar(min(sum_today, MAX_SUM_PER_HOUR * 8), MAX_SUM_PER_HOUR * 8)
    vip_line = "💎 *VIP-статус активен* (скидка 3%)" if is_vip(uid) else f"📈 До VIP: {10 - db_user_orders_count(uid)[0]} заказов"
    
    text = (
        f"{vip_mark}👤 *Профиль*\n\n"
        f"🆔 ID: `{uid}`\n👤 Имя: {str(fname or '-').replace('_', ' ').replace('*', '')}\n🌐 Язык: `{lang}`\n\n"
        f"💰 *Баланс:* {(bal or 0):.2f} ₽\n💸 *Потрачено:* {spent:.2f} ₽{discount_info}\n{vip_line}\n\n"
        f"🎁 *Рефералов:* {ref_count}\n💰 *Заработано с рефов:* {ref_earned:.2f} ₽\n🔗 *Ваша ссылка:*\n`{ref_link}`\n\n"
        f"💡 За каждого друга — *{REF_BONUS_PERCENT}%* от заказов!\n\n"
        f"⭐ Рейтинг: *{reviews_avg}/5* ({reviews_count} отзывов)\n"
        f"\n📊 *Лимиты на сегодня:*\n🎯 Заказов: *{orders_today}/{MAX_ORDERS_PER_DAY}*  `{orders_bar}`\n"
        f"💰 Потрачено: *{sum_today:.0f}/{MAX_SUM_PER_HOUR * 8} ₽*  `{sum_bar}`\n⏰ Сбросится в 00:00"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 История заказов", callback_data="history_menu")],
        [InlineKeyboardButton(text="💳 Пополнить", callback_data="topup")],
        [InlineKeyboardButton(text="👥 Мои рефералы", callback_data="my_refs")],
        [InlineKeyboardButton(text="⭐ Отзывы клиентов", callback_data="show_reviews")]
    ])
    await message.answer(text, reply_markup=kb)

@dp.message(F.text == "📊 Мои цифры")
async def msg_my_stats(message: Message):
    uid = message.from_user.id
    user = db_get_user(uid)
    if not user:
        await message.answer("Напишите /start")
        return
    cnt, total = db_user_orders_count(uid)
    refs = db_ref_count(uid)
    ref_earned = db_ref_earned(uid)
    discount = get_user_discount(uid)
    text = (
        f"📊 *Ваша статистика*\n\n📦 Всего заказов: *{cnt}*\n💸 Потрачено: *{total:.2f} ₽*\n"
        f"💰 Баланс: *{db_get_balance(uid):.2f} ₽*\n💎 Скидка: *{discount}%*\n"
        f"🎁 Рефералов: *{refs}*\n💰 Заработано с рефов: *{ref_earned:.2f} ₽*"
    )
    last_orders = db_user_orders(uid, 5)
    if last_orders:
        text += "\n\n📋 *Последние 5 заказов:*\n"
        for oid, p, sname, qty, price, status, created in last_orders:
            text += f"{status_emoji(status)} #{oid} {sname[:25]} — {(price or 0):.0f}₽\n"
    await message.answer(text, parse_mode=None)

@dp.callback_query(F.data == "my_refs")
async def cb_my_refs(call: CallbackQuery):
    refs = db_ref_list(call.from_user.id, REF_STATS_LIMIT)
    if not refs:
        await call.message.answer("👥 У вас пока нет рефералов.")
        return await call.answer()
    text = f"👥 *Ваши рефералы* ({len(refs)}):\n\n"
    for r_uid, r_uname, r_fname, r_reg, r_cnt, r_sum in refs:
        text += f"• {r_fname or '-'} (@{r_uname or '-'})\n   📅 {r_reg} | 📦 {r_cnt} заказов | 💸 {(r_sum or 0):.0f} ₽\n\n"
    await call.message.answer(text)
    await call.answer()

# ---------- ИЗБРАННОЕ ----------
@dp.message(F.text == "⭐ Избранное")
async def msg_favorites(message: Message):
    favs = db_fav_list(message.from_user.id)
    if not favs:
        await message.answer("⭐ *Избранное*\n\n📭 Пока пусто.\n\n💡 Открой любую услугу и нажми *«⭐ В избранное»*.")
        return
    kb_rows = []
    for plat, key in favs:
        item = SERVICES.get(plat, {}).get("items", {}).get(key)
        if not item: continue
        kb_rows.append([InlineKeyboardButton(text=item["name"][:55], callback_data=f"srv|{plat}|{key}")])
    kb_rows.append([InlineKeyboardButton(text="🔙 К платформам", callback_data="back_platforms")])
    await message.answer(f"⭐ *Ваше избранное* ({len(favs)})\n\n👇 Нажмите — откроется карточка услуги:", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows))

# ---------- ОТЗЫВЫ ----------
@dp.message(F.text == "⭐ Отзывы")
async def msg_reviews_main(message: Message):
    count, avg = db_reviews_avg()
    last = db_last_reviews(10)
    text = f"⭐ *Отзывы клиентов*\n\n📊 Средний: *{avg}/5*\n💬 Всего: *{count}*\n\n"
    if last:
        text += "*Последние отзывы:*\n"
        for uid, rating, comment, created in last:
            text += f"\n{'⭐' * rating} — {comment or '(без комментария)'}\n"
    else:
        text += "_Пока отзывов нет. Станьте первым!_"
    await message.answer(text)

@dp.callback_query(F.data == "show_reviews")
async def cb_show_reviews(call: CallbackQuery):
    await msg_reviews_main(call.message)
    await call.answer()
    
# ---------- ТОП ----------
@dp.message(F.text == "🔥 Топ")
async def msg_top(message: Message):
    tops = db_top_services(TOP_SERVICES_COUNT)
    if not tops:
        await message.answer("🔥 Пока нет популярных услуг. Станьте первым!")
        return
    text = f"🔥 *Топ-{TOP_SERVICES_COUNT} популярных услуг:*\n\n"
    kb_rows = []
    for i, (sid, sname, plat, cnt) in enumerate(tops, 1):
        text += f"{i}. {sname} — заказано {cnt} раз\n"
        for p, pdata in SERVICES.items():
            for k, item in pdata["items"].items():
                if item["id"] == sid:
                    kb_rows.append([InlineKeyboardButton(text=f"{i}. {sname[:35]}", callback_data=f"srv|{p}|{k}")])
                    break
    if kb_rows:
        await message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows))
    else:
        await message.answer(text)

# ---------- ШКОЛА НАКРУТКИ ----------
SCHOOL_ARTICLES = {
    "tiktok_algorithm": {"title": "🎵 Почему TikTok любит просмотры", "text": "📈 *Как работает алгоритм TikTok:*\n\n1️⃣ Видео попадает в «тестовую ленту» — 200-500 показов\n2️⃣ Если много просмотров за короткое время — алгоритм даёт больше показов\n3️⃣ Лайки и сохранения усиливают эффект\n4️⃣ Комментарии — самый мощный сигнал\n\n💡 *Что делать:*\n• Заливай просмотры сразу после публикации\n• Добавь лайки и сохранения в первые 2 часа\n• Не заказывай 100к сразу — алгоритм не поймёт\n\n🎯 *Оптимально:* 5000-10000 просмотров + 500 лайков"},
    "safe_boost": {"title": "🛡 Как не получить бан за накрутку", "text": "⚠️ *Правила безопасной накрутки:*\n\n✅ *Можно:*\n• Заказывать просмотры и лайки\n• Плавные заказы (1000-10000 шт)\n• Комбинировать услуги\n\n❌ *Нельзя:*\n• Заказывать 100к просмотров за раз\n• Накручивать негативные реакции\n• Заказывать на конкурентов без причины\n\n💡 *Совет:* разбей крупный заказ на 3-4 части по дням"},
    "best_time": {"title": "⏰ Лучшее время для заказа", "text": "📅 *Когда заказывать накрутку:*\n\n🕐 *TikTok:*\n• Публикуешь видео 18:00-21:00\n• Накрутка — в первые 30 минут\n\n🕐 *Telegram:*\n• Утром 9:00-11:00 — просмотры\n• Вечером 19:00-22:00 — подписчики\n\n🕐 *Instagram:*\n• Reels — 12:00-14:00 и 19:00-21:00\n\n💡 Работает по часовому поясу аудитории"},
    "how_many": {"title": "📊 Сколько нужно для трендов", "text": "🎯 *Сколько заказать:*\n\n📱 *TikTok:*\n• Минимум для алгоритма: 5000-10000 просмотров\n• Для трендов: 50к + 2000 лайков + 500 сохранений\n\n✈️ *Telegram:*\n• Минимум: 500 подписчиков\n• Для канала 1к+: 2000 подписчиков + 20к просмотров\n\n📸 *Instagram:*\n• Reels: 5000 просмотров + 500 лайков\n• Профиль: 1000 подписчиков + охват 10к"},
    "why_not_work": {"title": "❓ Почему не работает накрутка", "text": "🤔 *Если накрутка не дала эффекта:*\n\n1️⃣ *Контент слабый*\nНакрутка усиливает то, что уже работает. Скучное видео не спасёт.\n\n2️⃣ *Слишком много сразу*\n100к просмотров за минуту = подозрение. Разбей на части.\n\n3️⃣ *Списание*\nНекоторые услуги списываются через 30 дней. Смотри описание.\n\n4️⃣ *Не тот формат*\nПросмотры для Reels ≠ просмотры для поста.\n\n💡 *Совет:* начни с 1 услуги, посмотри результат, потом комбинируй."},
    "choose_service": {"title": "🎯 Какую услугу выбрать", "text": "📋 *Краткий гид по услугам:*\n\n👀 *Просмотры* — для виральности (Reels, TikTok, Shorts)\n\n❤️ *Лайки* — усилить охват и доверие\n\n👥 *Подписчики* — для роста канала\n\n💬 *Реакции* — для постов в TG (создают активность)\n\n🔁 *Репосты* — виральность в TG/VK\n\n💾 *Сохранения* — сигнал алгоритму TikTok/IG\n\n🌟 *Звёзды TG* — для премиум-аккаунта и подарков"},
}

@dp.message(F.text == "🎓 Школа накрутки")
async def msg_school(message: Message):
    kb_rows = []
    for key, art in SCHOOL_ARTICLES.items():
        kb_rows.append([InlineKeyboardButton(text=art["title"], callback_data=f"school_{key}")])
    kb_rows.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_platforms")])
    await message.answer("🎓 *Школа накрутки*\n\nПолезные статьи про накрутку — читай и применяй 👇", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows))

@dp.callback_query(F.data.startswith("school_"))
async def cb_school_article(call: CallbackQuery):
    key = call.data.replace("school_", "")
    article = SCHOOL_ARTICLES.get(key)
    if not article:
        await call.answer("Статья не найдена", show_alert=True)
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 К статьям", callback_data="school_back")],
        [InlineKeyboardButton(text="📦 Заказать", callback_data="back_platforms")]
    ])
    await call.message.edit_text(article["text"], reply_markup=kb)
    await call.answer()

@dp.callback_query(F.data == "school_back")
async def cb_school_back(call: CallbackQuery):
    kb_rows = []
    for key, art in SCHOOL_ARTICLES.items():
        kb_rows.append([InlineKeyboardButton(text=art["title"], callback_data=f"school_{key}")])
    kb_rows.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_platforms")])
    await call.message.edit_text("🎓 *Школа накрутки*\n\nПолезные статьи про накрутку — читай и применяй 👇", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows))
    await call.answer()
    
# ---------- КВИЗ ----------
@dp.message(F.text == "🎯 Что мне нужно?")
async def msg_quiz_start(message: Message, state: FSMContext):
    await state.clear()
    kb_rows = []
    for key, p in QUIZ_PLATFORMS.items():
        kb_rows.append([InlineKeyboardButton(text=p["title"], callback_data=f"quiz_plat_{key}")])
    await message.answer("🎯 *Подбор услуги*\n\nОтветьте на 3 вопроса — подберу лучший пакет под вас 👇\n\n*Шаг 1 из 3:* Какая платформа?", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows))

@dp.callback_query(F.data.startswith("quiz_plat_"))
async def cb_quiz_plat(call: CallbackQuery, state: FSMContext):
    plat = call.data.replace("quiz_plat_", "")
    if plat not in QUIZ_PLATFORMS:
        await call.answer("Недоступно", show_alert=True)
        return
    await state.update_data(quiz_plat=plat)
    kb_rows = []
    for key, g in QUIZ_GOALS.items():
        kb_rows.append([InlineKeyboardButton(text=g["title"], callback_data=f"quiz_goal_{key}")])
    await call.message.edit_text(f"🎯 *Подбор услуги*\n\nПлатформа: *{QUIZ_PLATFORMS[plat]['title']}*\n\n*Шаг 2 из 3:* Что вам нужно?", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows))
    await call.answer()

@dp.callback_query(F.data.startswith("quiz_goal_"))
async def cb_quiz_goal(call: CallbackQuery, state: FSMContext):
    goal = call.data.replace("quiz_goal_", "")
    if goal not in QUIZ_GOALS:
        await call.answer("Недоступно", show_alert=True)
        return
    data = await state.get_data()
    plat = data.get("quiz_plat", "telegram")
    await state.update_data(quiz_goal=goal)
    kb_rows = []
    for key, b in QUIZ_BUDGETS.items():
        kb_rows.append([InlineKeyboardButton(text=b["title"], callback_data=f"quiz_budget_{key}")])
    await call.message.edit_text(f"🎯 *Подбор услуги*\n\nПлатформа: *{QUIZ_PLATFORMS[plat]['title']}*\nЦель: *{QUIZ_GOALS[goal]['title']}*\n\n*Шаг 3 из 3:* Ваш бюджет?", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows))
    await call.answer()
    
@dp.callback_query(F.data.startswith("quiz_budget_"))
async def cb_quiz_budget(call: CallbackQuery, state: FSMContext):
    budget_key = call.data.replace("quiz_budget_", "")
    if budget_key not in QUIZ_BUDGETS:
        await call.answer("Недоступно", show_alert=True)
        return
    data = await state.get_data()
    plat = data.get("quiz_plat")
    goal = data.get("quiz_goal")
    if not plat or not goal:
        await state.clear()
        await call.answer("❌ Квиз сброшен, начните заново", show_alert=True)
        return
    kind, payload = quiz_recommend(plat, goal, budget_key)
    if kind == "bundle":
        bkey, bundle, final = payload
        items_text = "\n".join(f"• {SERVICES[p]['items'][k]['name']} × {q}" for p, k, q in bundle["items"])
        text = f"✅ *Рекомендация готова!*\n\n🎁 *{bundle['name']}*\n{bundle['desc']}\n\n{items_text}\n\n💰 Скидка пакета: *-{bundle['discount']}%*\n💸 Итого: *{final:.2f} ₽*"
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"🎁 Взять пакет — {final:.0f} ₽", callback_data=f"bundle_{bkey}")],
            [InlineKeyboardButton(text="🎯 Пройти заново", callback_data="quiz_restart")],
            [InlineKeyboardButton(text="📦 Все услуги", callback_data="back_platforms")],
        ])
    elif kind == "service":
        pl, srv_key, item = payload
        unit = item["price"] / item["pack"]
        text = f"✅ *Рекомендация готова!*\n\n📦 *{item['name']}*\n{item['desc']}\n\n💸 Цена: *{item['price']} ₽ за {item['pack']} шт*\n(≈ {unit:.4f} ₽/шт)"
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"📦 Выбрать — {item['name'][:30]}", callback_data=f"srv|{pl}|{srv_key}")],
            [InlineKeyboardButton(text="🎯 Пройти заново", callback_data="quiz_restart")],
            [InlineKeyboardButton(text="📦 Все услуги", callback_data="back_platforms")],
        ])
    else:
        text = "😔 *Не нашёл подходящего варианта*\n\nПопробуйте другой бюджет или платформу."
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🎯 Пройти заново", callback_data="quiz_restart")],
            [InlineKeyboardButton(text="📦 Все услуги", callback_data="back_platforms")],
        ])
    await call.message.edit_text(text, reply_markup=kb)
    await state.clear()
    await call.answer("✅ Готово!")

@dp.callback_query(F.data == "quiz_restart")
async def cb_quiz_restart(call: CallbackQuery, state: FSMContext):
    await state.clear()
    kb_rows = []
    for key, p in QUIZ_PLATFORMS.items():
        kb_rows.append([InlineKeyboardButton(text=p["title"], callback_data=f"quiz_plat_{key}")])
    await call.message.edit_text("🎯 *Подбор услуги*\n\n*Шаг 1 из 3:* Какая платформа?", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows))
    await call.answer()

# ============ НОВЫЕ ФУНКЦИИ С ПАГИНАЦИЕЙ ============

async def show_platform_services(call: CallbackQuery, plat: str):
    if plat not in SERVICES:
        await call.answer("Платформа не найдена", show_alert=True)
        return
        
    data = SERVICES[plat]
    items_dict = data.get("items", data)
    
    # Считаем услуги по категориям
    groups = {}
    for key, item in items_dict.items():
        if key in ("title", "items"): continue
        if key.startswith("tg_report_") and key != "tg_report_menu": continue
            
        action = classify_service(key, item)
        group_info = {
            "views":   ("👀 Просмотры", "👀"), "likes":   ("❤️ Лайки / Реакции", "❤️"),
            "subs":    ("👥 Подписчики", "👥"), "starts":  ("🚀 Запуски", "🚀"),
            "live":    ("📡 Зрители / Стрим", "📡"), "reposts": ("🔁 Репосты", "🔁"),
            "saves":   ("⭐ Избранное", "⭐"), "reactions": ("🔥 Реакции", "🔥"),
            "comments": ("💬 Комментарии", "💬"), "other":   ("📦 Прочее", "📦")
        }
        g_name, g_icon = group_info.get(action, ("📦 Прочее", "📦"))
        if key == "tg_report_menu": g_name = "🚨 Жалобы"
            
        if g_name not in groups: groups[g_name] = []
        groups[g_name].append((key, item))
        
    kb_buttons = []
    row = []
    
    # Выводим кнопки категорий по 2 в ряд
    for g_name, items in groups.items():
        btn_text = f"{g_name} ({len(items)})"
        # В callback_data передаем категорию БЕЗ эмодзи, чтобы не ломалось
        row.append(InlineKeyboardButton(text=btn_text, callback_data=f"grp|{plat}|{g_name}"))
        if len(row) == 2:
            kb_buttons.append(row)
            row = []
    if row: kb_buttons.append(row)
        
    kb_buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_platforms")])
    
    title_text = f"{data.get('title', plat.upper())} // ЧТО ВАМ НУЖНО?\nДоступно услуг: {sum(len(v) for v in groups.values())} шт."
    
    try:
        await call.message.edit_text(title_text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_buttons))
    except Exception:
        await call.message.answer(title_text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_buttons))


@dp.callback_query(F.data.startswith("pg_srv|"))
async def cb_pg_srv(call: CallbackQuery):
    # Разбираем данные: pg_srv|telegram|👀 Просмотры|1
    parts = call.data.split("|")
    if len(parts) != 4:
        return await call.answer("Ошибка навигации", show_alert=True)
        
    plat = parts[1]
    group_name = parts[2]
    page = int(parts[3])
    
    data = SERVICES[plat]
    items_dict = data.get("items", data)
    valid_items = []
    
    for key, item in items_dict.items():
        if key in ("title", "items"): continue
        if key.startswith("tg_report_") and key != "tg_report_menu": continue
        
        action = classify_service(key, item)
        group_names = {
            "views": "👀 Просмотры", "likes": "❤️ Лайки / Реакции", "subs": "👥 Подписчики", 
            "starts": "🚀 Запуски", "live": "📡 Зрители / Стрим", "reposts": "🔁 Репосты",
            "saves": "⭐ Избранное", "reactions": "🔥 Реакции", "comments": "💬 Комментарии", "other": "📦 Прочее"
        }
        g_name = group_names.get(action, "📦 Прочее")
        if key == "tg_report_menu": g_name = "🚨 Жалобы"
        
        if g_name == group_name: 
            valid_items.append((key, item))
        
    await show_services_page(call, plat, group_name, valid_items, page)
    await call.answer()
    
# ---------- ВВОД КОЛИЧЕСТВА ----------
@dp.message(OrderStates.waiting_quantity)
async def process_quantity(message: Message, state: FSMContext):
    if not message.text or not message.text.strip().isdigit():
        await message.answer("⚠️ Введите число"); return
    qty = int(message.text.strip())
    if qty < 1:
        await message.answer("⚠️ Минимум 1"); return
    data = await state.get_data()
    if data.get("key") == "tg_stars" and qty % 100 != 0:
        await message.answer("⚠️ *Telegram Звёзды* кратно *100 шт*.\n\nВведите: `100`, `200`, `500`, `1000`."); return
    if db_orders_last_hour(message.from_user.id) >= MAX_ORDERS_PER_HOUR:
        await message.answer(T(message.from_user.id, "limit_exceeded")); return
    if db_count_orders_today(message.from_user.id) >= MAX_ORDERS_PER_DAY:
        await message.answer(T(message.from_user.id, "daily_limit")); return

    item = SERVICES[data["plat"]]["items"][data["key"]]
    unit = item["price"] / item["pack"]
    total = round(unit * qty, 2)
    await state.update_data(quantity=qty, total=total)

    # === ВЫБОР РЕЖИМА ===
    plat = data["plat"]; key = data["key"]
    kb_rows = [[InlineKeyboardButton(text="⚡ Моментально", callback_data="smooth_mode_0")]]
    if can_be_smooth(plat, key):
        kb_rows.append([InlineKeyboardButton(text="🐢 Плавно (меньше бан)", callback_data="smooth_mode_1")])
    kb_rows.append([InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_order")])

    forecast = predict_order(plat, key, qty)
    await message.answer(
        f"✅ Количество: *{qty}*\n💸 Итого: *{total} ₽*\n{forecast}\n\n"
        f"*Выберите режим выдачи:*",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows)
    )

# ---------- ВЫБОР РЕЖИМА ----------
@dp.callback_query(F.data.startswith("smooth_mode_"))
async def cb_smooth_mode(call: CallbackQuery, state: FSMContext):
    mode = call.data.replace("smooth_mode_", "")
    data = await state.get_data()
    plat = data.get("plat"); key = data.get("key")
    if not plat or not key:
        await call.answer("Данные потеряны", show_alert=True); return

    if mode == "0":
        # Моментально — сразу к ссылке
        await state.update_data(priv_days=0, smooth_interval=60)
        await state.set_state(OrderStates.waiting_link)
        await call.message.edit_text(
            "⚡ *Моментальный режим*\n\n🔗 Отправьте ссылку на аккаунт/пост:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_order")]
            ])
        )
        await call.answer(); return

    # Плавно — шаг 1: дни
    await state.set_state(OrderStates.waiting_smooth_days)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1 день", callback_data="sdays_1"),
         InlineKeyboardButton(text="7 дней", callback_data="sdays_7")],
        [InlineKeyboardButton(text="12 дней", callback_data="sdays_12"),
         InlineKeyboardButton(text="21 день", callback_data="sdays_21")],
        [InlineKeyboardButton(text="30 дней", callback_data="sdays_30"),
         InlineKeyboardButton(text="60 дней", callback_data="sdays_60")],
        [InlineKeyboardButton(text="✏️ Своё число", callback_data="sdays_custom")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_order")]
    ])
    await call.message.edit_text(
        "🐢 *Плавная накрутка*\n\n"
        "📆 *Шаг 1 из 2:* На сколько дней растянуть?\n\n"
        f"От *{SMOOTH_MIN_DAYS}* до *{SMOOTH_MAX_DAYS}* дней.",
        reply_markup=kb
    )
    await call.answer()


# ---------- ВЫБОР ДНЕЙ ----------
@dp.callback_query(F.data.startswith("sdays_"))
async def cb_smooth_days(call: CallbackQuery, state: FSMContext):
    val = call.data.replace("sdays_", "")
    if val == "custom":
        await state.set_state(OrderStates.waiting_smooth_custom_days)
        await call.message.edit_text(
            f"✏️ *Введите своё число дней*\n\n"
            f"📆 От *{SMOOTH_MIN_DAYS}* до *{SMOOTH_MAX_DAYS}*.\n"
            f"Например: `14`",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_order")]
            ])
        )
        await call.answer(); return

    try: days = int(val)
    except ValueError: return
    days = max(SMOOTH_MIN_DAYS, min(SMOOTH_MAX_DAYS, days))
    await state.update_data(smooth_days=days)
    await _ask_smooth_interval(call, days)
    await call.answer()


@dp.message(OrderStates.waiting_smooth_custom_days)
async def process_smooth_custom_days(message: Message, state: FSMContext):
    if not message.text or not message.text.strip().isdigit():
        await message.answer(f"⚠️ Введите число от {SMOOTH_MIN_DAYS} до {SMOOTH_MAX_DAYS}")
        return
    days = int(message.text.strip())
    if days < SMOOTH_MIN_DAYS or days > SMOOTH_MAX_DAYS:
        await message.answer(f"⚠️ От *{SMOOTH_MIN_DAYS}* до *{SMOOTH_MAX_DAYS}* дней. Попробуйте снова:")
        return
    await state.update_data(smooth_days=days)
    await _ask_smooth_interval_msg(message, days)


async def _ask_smooth_interval(call: CallbackQuery, days: int):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="15 минут", callback_data="sint_15"),
         InlineKeyboardButton(text="30 минут", callback_data="sint_30")],
        [InlineKeyboardButton(text="60 минут", callback_data="sint_60"),
         InlineKeyboardButton(text="3 часа", callback_data="sint_180")],
        [InlineKeyboardButton(text="9 часов", callback_data="sint_540"),
         InlineKeyboardButton(text="12 часов", callback_data="sint_720")],
        [InlineKeyboardButton(text="24 часа", callback_data="sint_1440")],
        [InlineKeyboardButton(text="✏️ Своё число (мин/час)", callback_data="sint_custom")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_order")]
    ])
    await call.message.edit_text(
        f"✅ Выбрано: *{days} дней*\n\n"
        f"⏱ *Шаг 2 из 2:* Как часто отправлять партии в панель?",
        reply_markup=kb
    )


async def _ask_smooth_interval_msg(message: Message, days: int):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="15 минут", callback_data="sint_15"),
         InlineKeyboardButton(text="30 минут", callback_data="sint_30")],
        [InlineKeyboardButton(text="60 минут", callback_data="sint_60"),
         InlineKeyboardButton(text="3 часа", callback_data="sint_180")],
        [InlineKeyboardButton(text="9 часов", callback_data="sint_540"),
         InlineKeyboardButton(text="12 часов", callback_data="sint_720")],
        [InlineKeyboardButton(text="24 часа", callback_data="sint_1440")],
        [InlineKeyboardButton(text="✏️ Своё число (мин/час)", callback_data="sint_custom")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_order")]
    ])
    await message.answer(
        f"✅ Выбрано: *{days} дней*\n\n"
        f"⏱ *Шаг 2 из 2:* Как часто отправлять партии в панель?",
        reply_markup=kb
    )


# ---------- ВЫБОР ИНТЕРВАЛА ----------
@dp.callback_query(F.data.startswith("sint_"))
async def cb_smooth_interval(call: CallbackQuery, state: FSMContext):
    val = call.data.replace("sint_", "")
    if val == "custom":
        await state.set_state(OrderStates.waiting_smooth_custom_interval)
        await call.message.edit_text(
            "✏️ *Введите свой интервал*\n\n"
            "Формат: `30м` или `2ч`\n"
            "📉 Минимум 5 минут, максимум 24 часа.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_order")]
            ])
        )
        await call.answer(); return

    try: interval = int(val)
    except ValueError: return
    await _finalize_smooth(call, interval, state)
    await call.answer()


@dp.message(OrderStates.waiting_smooth_custom_interval)
async def process_smooth_custom_interval(message: Message, state: FSMContext):
    txt = (message.text or "").strip().lower().replace(" ", "")
    try:
        if txt.endswith("м") or txt.endswith("мин"):
            val = int(txt.replace("м", "").replace("мин", ""))
            if val < 5 or val > 1440: raise ValueError
            interval = val
        elif txt.endswith("ч") or txt.endswith("час"):
            val = int(txt.replace("ч", "").replace("час", ""))
            if val < 1 or val > 24: raise ValueError
            interval = val * 60
        else:
            val = int(txt)
            if val < 1 or val > 24: raise ValueError
            interval = val * 60
    except (ValueError, AttributeError):
        await message.answer("⚠️ Неверный формат. Введите, например: `30м` или `2ч`")
        return

    data = await state.get_data()
    plat = data.get("plat"); key = data.get("key"); qty = data.get("quantity"); total = data.get("total")
    days = data.get("smooth_days", 7)
    if not plat or not key or not qty:
        await state.clear(); await message.answer("⚠️ Данные потеряны. /start"); return

    await state.update_data(priv_days=days, smooth_interval=interval)
    await state.set_state(OrderStates.waiting_link)
    item = SERVICES[plat]["items"][key]
    total_minutes = days * 24 * 60
    total_sends = max(1, total_minutes // interval)
    step = max(1, qty // total_sends)
    int_text = f"{interval} мин." if interval < 60 else f"{interval // 60} ч."
    await message.answer(
        f"✅ *Режим выбран!*\n\n"
        f"🐢 Плавно за *{days} дн.*\n"
        f"⏱ Интервал: *каждые {int_text}*\n"
        f"📦 ~{step} шт. за раз\n\n"
        f"📦 {item['name']} × {qty}\n"
        f"💸 Итого: *{total} ₽*\n\n"
        f"🔗 Укажите ссылку:"
    )


async def _finalize_smooth(call: CallbackQuery, interval: int, state: FSMContext):
    data = await state.get_data()
    plat = data.get("plat"); key = data.get("key"); qty = data.get("quantity"); total = data.get("total")
    days = data.get("smooth_days", 7)
    if not plat or not key or not qty:
        await call.message.edit_text("⚠️ Данные потеряны. /start")
        await call.answer(); return

    await state.update_data(priv_days=days, smooth_interval=interval)
    await state.set_state(OrderStates.waiting_link)
    item = SERVICES[plat]["items"][key]
    total_minutes = days * 24 * 60
    total_sends = max(1, total_minutes // interval)
    step = max(1, qty // total_sends)
    int_text = f"{interval} мин." if interval < 60 else f"{interval // 60} ч."
    await call.message.edit_text(
        f"✅ *Режим выбран!*\n\n"
        f"🐢 Плавно за *{days} дн.*\n"
        f"⏱ Интервал: *каждые {int_text}*\n"
        f"📦 ~{step} шт. за раз\n\n"
        f"📦 {item['name']} × {qty}\n"
        f"💸 Итого: *{total} ₽*\n\n"
        f"🔗 Укажите ссылку:"
    )
    
# ---------- ОБРАБОТЧИК КАТЕГОРИЙ (grp) ----------
GROUP_NAMES = {
    "views": "👀 Просмотры",
    "likes": "❤️ Лайки / Реакции",
    "subs": "👥 Подписчики",
    "starts": "🚀 Запуски",
    "live": "📡 Зрители / Стрим",
    "reposts": "🔁 Репосты",
    "saves": "⭐ Избранное",
    "reactions": "🔥 Реакции",
    "comments": "💬 Комментарии",
    "other": "📦 Прочее",
}

def _get_group_items(plat: str, group_name: str) -> list:
    data = SERVICES.get(plat, {})
    items_dict = data.get("items", data)
    valid_items = []
    for key, item in items_dict.items():
        if key in ("title", "items") or not isinstance(item, dict):
            continue
        if key.startswith("tg_report_") and key != "tg_report_menu":
            continue
        action = classify_service(key, item)
        g_name = "🚨 Жалобы" if key == "tg_report_menu" else GROUP_NAMES.get(action, "📦 Прочее")
        if g_name == group_name:
            valid_items.append((key, item))
    return valid_items

@dp.callback_query(F.data.startswith("grp|"))
async def cb_group_services(call: CallbackQuery):
    parts = call.data.split("|")
    if len(parts) != 3:
        await call.answer("Ошибка данных", show_alert=True)
        return

    _, plat, group_name = parts
    if plat not in SERVICES:
        await call.answer("Недоступно", show_alert=True)
        return

    valid_items = _get_group_items(plat, group_name)
    if not valid_items:
        await call.answer("В этой категории пока нет услуг", show_alert=True)
        return

    await show_services_page(call, plat, group_name, valid_items, 0)
    await call.answer()





# ---------- ОТРИСОВКА УСЛУГ (С ПАГИНАЦИЕЙ) ----------
async def show_services_page(call: CallbackQuery, plat: str, group_name: str, items_list: list, page: int):
    ITEMS_PER_PAGE = 8
    total_pages = (len(items_list) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    page = max(0, min(page, total_pages - 1))
    
    start = page * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    
    kb_rows = []
    for key, item in items_list[start:end]:
        kb_rows.append([InlineKeyboardButton(text=item["name"][:60], callback_data=f"srv|{plat}|{key}")])
        
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"pg_srv|{plat}|{group_name}|{page-1}"))
    nav_row.append(InlineKeyboardButton(text=f"📄 {page+1}/{total_pages}", callback_data="noop"))
    if page < total_pages - 1:
        nav_row.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"pg_srv|{plat}|{group_name}|{page+1}"))
    if nav_row:
        kb_rows.append(nav_row)
        
    kb_rows.append([InlineKeyboardButton(text="🔙 Назад в категории", callback_data=f"plat_{plat}")])
    
    text_msg = f"📂 *{group_name}*\n\n{SERVICES[plat].get('title', plat.upper())}\nВыберите услугу 👇"
    
    try:
        await call.message.edit_text(text_msg, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows))
    except Exception:
        await call.message.answer(text_msg, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows))

# ---------- НАЗАД К ПЛАТФОРМАМ ----------
@dp.callback_query(F.data == "back_platforms")
async def cb_back_platforms(call: CallbackQuery):
    await call.message.edit_text(T(call.from_user.id, "choose_platform"), reply_markup=platforms_kb())
    await call.answer()

# ---------- ОБРАБОТЧИК ВЫБОРА ПЛАТФОРМЫ ----------
@dp.callback_query(F.data.startswith("plat_"))
async def cb_platform(call: CallbackQuery):
    plat = call.data.replace("plat_", "")
    if plat not in SERVICES:
        await call.answer("Недоступно", show_alert=True)
        return
    await show_platform_services(call, plat)
    await call.answer()
    
@dp.callback_query(F.data == "back_platforms")
async def cb_back_platforms(call: CallbackQuery):
    await call.message.edit_text(T(call.from_user.id, "choose_platform"), reply_markup=platforms_kb())
    await call.answer()
    
# ---------- КОРЗИНА ----------
@dp.message(F.text == "🛒 Корзина")
async def msg_cart(message: Message, state: FSMContext):
    data = await state.get_data()
    cart = data.get("cart", [])
    if not cart:
        await message.answer("🛒 *Корзина пуста*\n\n💡 Добавляйте услуги через *«📦 Услуги»* — кнопка *«🛒 В корзину»*.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📦 К услугам", callback_data="back_platforms")]
        ]))
        return
    text = "🛒 *Ваша корзина:*\n\n"
    total = 0
    for i, item in enumerate(cart, 1):
        it = SERVICES[item["plat"]]["items"][item["key"]]
        unit = it["price"] / it["pack"]
        price = round(unit * item["qty"], 2)
        total += price
        text += f"{i}. 📦 {it['name']}\n   🔢 {item['qty']} шт · 🔗 {item['link'][:40]}\n   💸 {price:.2f} ₽\n\n"
    total = round(total, 2)
    discount = 10 if len(cart) >= 3 else 0
    final = round(total * (1 - discount / 100), 2)
    if discount:
        text += f"━━━━━━━━━━━━━━━\n💰 Сумма: *{total:.2f} ₽*\n"
        text += f"🎁 Скидка за 3+ услуги: *−{discount}%*\n"
        text += f"💎 Итого: *{final:.2f} ₽*\n"
    else:
        text += f"━━━━━━━━━━━━━━━\n💰 Итого: *{total:.2f} ₽*\n"
        text += f"💡 *Добавьте ещё {3 - len(cart)} услуг — скидка 10%!*"
    kb_rows = [
        [InlineKeyboardButton(text=f"✅ Оплатить корзину ({final:.0f} ₽)", callback_data="cart_checkout")],
        [InlineKeyboardButton(text="🗑 Очистить", callback_data="cart_clear")],
        [InlineKeyboardButton(text="📦 Добавить ещё", callback_data="back_platforms")]
    ]
    await message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows))

@dp.callback_query(F.data == "cart_clear")
async def cb_cart_clear(call: CallbackQuery, state: FSMContext):
    await state.update_data(cart=[])
    await call.message.edit_text("🗑 *Корзина очищена*")
    await call.answer("Очищено")

@dp.callback_query(F.data == "cart_add")
async def cb_cart_add(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    plat = data.get("cart_plat"); key = data.get("cart_key")
    if not plat or not key:
        await call.answer("Ошибка", show_alert=True); return
    await state.set_state(OrderStates.waiting_cart_qty)
    item = SERVICES[plat]["items"][key]
    await call.message.edit_text(f"🛒 *Добавить в корзину*\n\n📦 {item['name']}\n💸 {item['price']}₽ за {item['pack']} шт\n\n🔢 Введите количество:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_order")]
    ]))
    await call.answer()

@dp.message(OrderStates.waiting_cart_qty)
async def process_cart_qty(message: Message, state: FSMContext):
    if not message.text or not message.text.strip().isdigit():
        await message.answer("⚠️ Введите число"); return
    qty = int(message.text.strip())
    if qty < 1:
        await message.answer("⚠️ Минимум 1"); return
    await state.update_data(cart_qty=qty)
    await state.set_state(OrderStates.waiting_cart_link)
    await message.answer(f"✅ Количество: *{qty}*\n\n🔗 Введите ссылку:")

# ---------- ВЫБОР ДНЕЙ ПЛАВНОЙ НАКРУТКИ ----------
@dp.callback_query(F.data.startswith("smooth_"))
async def cb_smooth_choice(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    plat = data.get("plat")
    key = data.get("key")
    qty = data.get("quantity")
    
    if not plat or not key or not qty:
        await call.answer("⚠️ Данные потеряны. Начните заново.", show_alert=True)
        await state.clear()
        return
    
    choice = call.data.replace("smooth_", "")
    
    if choice == "0":
        # Моментальный режим (как было)
        await state.update_data(priv_days=0, smooth_interval=60)
        await state.set_state(OrderStates.waiting_link)
        await call.message.edit_text("⚡ Режим: Моментально.\n\n🔗 Отправьте ссылку на аккаунт/пост:")
        await call.answer()
        return
        
    # Если выбрали Плавно — спрашиваем СНАЧАЛА ДНИ
    await state.update_data(awaiting_smooth=True)
    await state.set_state(OrderStates.waiting_custom_days)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="3 дня", callback_data="set_days_3"), InlineKeyboardButton(text="7 дней", callback_data="set_days_7")],
        [InlineKeyboardButton(text="14 дней", callback_data="set_days_14"), InlineKeyboardButton(text="30 дней", callback_data="set_days_30")],
        [InlineKeyboardButton(text="✏️ Ввести своё число", callback_data="set_days_custom")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="back_platforms")]
    ])
    
    await call.message.edit_text(
        "🐢 *Плавная накрутка*\n\n"
        "📆 *Шаг 1:* На сколько дней растянуть заказ?\n\n"
        "Выберите из списка или введите своё число:",
        reply_markup=kb,
        parse_mode="Markdown"
    )
    await call.answer()
    
# Обработка кнопок с готовыми днями
@dp.callback_query(F.data.startswith("set_days_"))
async def process_set_days(call: CallbackQuery, state: FSMContext):
    val = call.data.replace("set_days_", "")
    
    if val == "custom":
        await call.message.edit_text(
            f"✏️ *Введите своё количество дней*\n\n"
            f"📆 От *{SMOOTH_MIN_DAYS}* до *{SMOOTH_MAX_DAYS}* дней.\n"
            f"Введите число (например: `21`):"
        )
        return
        
    try:
        days = int(val)
    except ValueError:
        return
        
    await state.update_data(smooth_days=days)
    await call.message.edit_text(
        f"✅ Выбрано: *{days} дней*\n\n"
        f"⏱ *Шаг 2:* Теперь выберите, как часто отправлять партии в панель?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⚡ Каждые 15 минут", callback_data="interval_15")],
            [InlineKeyboardButton(text="🕐 Каждые 30 минут", callback_data="interval_30")],
            [InlineKeyboardButton(text="🕒 Каждый час", callback_data="interval_60")],
            [InlineKeyboardButton(text="🕕 Каждые 3 часа", callback_data="interval_180")],
            [InlineKeyboardButton(text="🕛 Каждые 6 часов", callback_data="interval_360")],
            [InlineKeyboardButton(text="🌙 Раз в 12 часов", callback_data="interval_720")],
            [InlineKeyboardButton(text="🌅 Раз в 24 часа", callback_data="interval_1440")],
            [InlineKeyboardButton(text="✏️ Ввести своё число (мин/час)", callback_data="interval_custom")]
        ]),
        parse_mode="Markdown"
    )
    await call.answer()

# ---------- ВВОД СВОИХ ДНЕЙ ----------
# ---------- ВЫБОР РЕЖИМА ----------
@dp.callback_query(F.data.startswith("smooth_mode_"))
async def cb_smooth_mode(call: CallbackQuery, state: FSMContext):
    mode = call.data.replace("smooth_mode_", "")
    data = await state.get_data()
    plat = data.get("plat"); key = data.get("key")
    if not plat or not key:
        await call.answer("Данные потеряны", show_alert=True); return

    if mode == "0":
        # Моментально — сразу к ссылке
        await state.update_data(priv_days=0, smooth_interval=60)
        await state.set_state(OrderStates.waiting_link)
        await call.message.edit_text(
            "⚡ *Моментальный режим*\n\n🔗 Отправьте ссылку на аккаунт/пост:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_order")]
            ])
        )
        await call.answer(); return

    # Плавно — шаг 1: дни
    await state.set_state(OrderStates.waiting_smooth_days)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1 день", callback_data="sdays_1"),
         InlineKeyboardButton(text="7 дней", callback_data="sdays_7")],
        [InlineKeyboardButton(text="12 дней", callback_data="sdays_12"),
         InlineKeyboardButton(text="21 день", callback_data="sdays_21")],
        [InlineKeyboardButton(text="30 дней", callback_data="sdays_30"),
         InlineKeyboardButton(text="60 дней", callback_data="sdays_60")],
        [InlineKeyboardButton(text="✏️ Своё число", callback_data="sdays_custom")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_order")]
    ])
    await call.message.edit_text(
        "🐢 *Плавная накрутка*\n\n"
        "📆 *Шаг 1 из 2:* На сколько дней растянуть?\n\n"
        f"От *{SMOOTH_MIN_DAYS}* до *{SMOOTH_MAX_DAYS}* дней.",
        reply_markup=kb
    )
    await call.answer()


# ---------- ВЫБОР ДНЕЙ ----------
@dp.callback_query(F.data.startswith("sdays_"))
async def cb_smooth_days(call: CallbackQuery, state: FSMContext):
    val = call.data.replace("sdays_", "")
    if val == "custom":
        await state.set_state(OrderStates.waiting_smooth_custom_days)
        await call.message.edit_text(
            f"✏️ *Введите своё число дней*\n\n"
            f"📆 От *{SMOOTH_MIN_DAYS}* до *{SMOOTH_MAX_DAYS}*.\n"
            f"Например: `14`",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_order")]
            ])
        )
        await call.answer(); return

    try: days = int(val)
    except ValueError: return
    days = max(SMOOTH_MIN_DAYS, min(SMOOTH_MAX_DAYS, days))
    await state.update_data(smooth_days=days)
    await _ask_smooth_interval(call, days)
    await call.answer()


@dp.message(OrderStates.waiting_smooth_custom_days)
async def process_smooth_custom_days(message: Message, state: FSMContext):
    if not message.text or not message.text.strip().isdigit():
        await message.answer(f"⚠️ Введите число от {SMOOTH_MIN_DAYS} до {SMOOTH_MAX_DAYS}")
        return
    days = int(message.text.strip())
    if days < SMOOTH_MIN_DAYS or days > SMOOTH_MAX_DAYS:
        await message.answer(f"⚠️ От *{SMOOTH_MIN_DAYS}* до *{SMOOTH_MAX_DAYS}* дней. Попробуйте снова:")
        return
    await state.update_data(smooth_days=days)
    await _ask_smooth_interval_msg(message, days)


async def _ask_smooth_interval(call: CallbackQuery, days: int):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="15 минут", callback_data="sint_15"),
         InlineKeyboardButton(text="30 минут", callback_data="sint_30")],
        [InlineKeyboardButton(text="60 минут", callback_data="sint_60"),
         InlineKeyboardButton(text="3 часа", callback_data="sint_180")],
        [InlineKeyboardButton(text="9 часов", callback_data="sint_540"),
         InlineKeyboardButton(text="12 часов", callback_data="sint_720")],
        [InlineKeyboardButton(text="24 часа", callback_data="sint_1440")],
        [InlineKeyboardButton(text="✏️ Своё число (мин/час)", callback_data="sint_custom")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_order")]
    ])
    await call.message.edit_text(
        f"✅ Выбрано: *{days} дней*\n\n"
        f"⏱ *Шаг 2 из 2:* Как часто отправлять партии в панель?",
        reply_markup=kb
    )


async def _ask_smooth_interval_msg(message: Message, days: int):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="15 минут", callback_data="sint_15"),
         InlineKeyboardButton(text="30 минут", callback_data="sint_30")],
        [InlineKeyboardButton(text="60 минут", callback_data="sint_60"),
         InlineKeyboardButton(text="3 часа", callback_data="sint_180")],
        [InlineKeyboardButton(text="9 часов", callback_data="sint_540"),
         InlineKeyboardButton(text="12 часов", callback_data="sint_720")],
        [InlineKeyboardButton(text="24 часа", callback_data="sint_1440")],
        [InlineKeyboardButton(text="✏️ Своё число (мин/час)", callback_data="sint_custom")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_order")]
    ])
    await message.answer(
        f"✅ Выбрано: *{days} дней*\n\n"
        f"⏱ *Шаг 2 из 2:* Как часто отправлять партии в панель?",
        reply_markup=kb
    )


# ---------- ВЫБОР ИНТЕРВАЛА ----------
@dp.callback_query(F.data.startswith("sint_"))
async def cb_smooth_interval(call: CallbackQuery, state: FSMContext):
    val = call.data.replace("sint_", "")
    if val == "custom":
        await state.set_state(OrderStates.waiting_smooth_custom_interval)
        await call.message.edit_text(
            "✏️ *Введите свой интервал*\n\n"
            "Формат: `30м` или `2ч`\n"
            "📉 Минимум 5 минут, максимум 24 часа.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_order")]
            ])
        )
        await call.answer(); return

    try: interval = int(val)
    except ValueError: return
    await _finalize_smooth(call, interval, state)
    await call.answer()


@dp.message(OrderStates.waiting_smooth_custom_interval)
async def process_smooth_custom_interval(message: Message, state: FSMContext):
    txt = (message.text or "").strip().lower().replace(" ", "")
    try:
        if txt.endswith("м") or txt.endswith("мин"):
            val = int(txt.replace("м", "").replace("мин", ""))
            if val < 5 or val > 1440: raise ValueError
            interval = val
        elif txt.endswith("ч") or txt.endswith("час"):
            val = int(txt.replace("ч", "").replace("час", ""))
            if val < 1 or val > 24: raise ValueError
            interval = val * 60
        else:
            val = int(txt)
            if val < 1 or val > 24: raise ValueError
            interval = val * 60
    except (ValueError, AttributeError):
        await message.answer("⚠️ Неверный формат. Введите, например: `30м` или `2ч`")
        return

    data = await state.get_data()
    plat = data.get("plat"); key = data.get("key"); qty = data.get("quantity"); total = data.get("total")
    days = data.get("smooth_days", 7)
    if not plat or not key or not qty:
        await state.clear(); await message.answer("⚠️ Данные потеряны. /start"); return

    await state.update_data(priv_days=days, smooth_interval=interval)
    await state.set_state(OrderStates.waiting_link)
    item = SERVICES[plat]["items"][key]
    total_minutes = days * 24 * 60
    total_sends = max(1, total_minutes // interval)
    step = max(1, qty // total_sends)
    int_text = f"{interval} мин." if interval < 60 else f"{interval // 60} ч."
    await message.answer(
        f"✅ *Режим выбран!*\n\n"
        f"🐢 Плавно за *{days} дн.*\n"
        f"⏱ Интервал: *каждые {int_text}*\n"
        f"📦 ~{step} шт. за раз\n\n"
        f"📦 {item['name']} × {qty}\n"
        f"💸 Итого: *{total} ₽*\n\n"
        f"🔗 Укажите ссылку:"
    )


async def _finalize_smooth(call: CallbackQuery, interval: int, state: FSMContext):
    data = await state.get_data()
    plat = data.get("plat"); key = data.get("key"); qty = data.get("quantity"); total = data.get("total")
    days = data.get("smooth_days", 7)
    if not plat or not key or not qty:
        await call.message.edit_text("⚠️ Данные потеряны. /start")
        await call.answer(); return

    await state.update_data(priv_days=days, smooth_interval=interval)
    await state.set_state(OrderStates.waiting_link)
    item = SERVICES[plat]["items"][key]
    total_minutes = days * 24 * 60
    total_sends = max(1, total_minutes // interval)
    step = max(1, qty // total_sends)
    int_text = f"{interval} мин." if interval < 60 else f"{interval // 60} ч."
    await call.message.edit_text(
        f"✅ *Режим выбран!*\n\n"
        f"🐢 Плавно за *{days} дн.*\n"
        f"⏱ Интервал: *каждые {int_text}*\n"
        f"📦 ~{step} шт. за раз\n\n"
        f"📦 {item['name']} × {qty}\n"
        f"💸 Итого: *{total} ₽*\n\n"
        f"🔗 Укажите ссылку:"
    )
    
@dp.message(OrderStates.waiting_smooth_custom_days)
async def process_custom_days(message: Message, state: FSMContext):
    if not message.text or not message.text.strip().isdigit():
        await message.answer(f"⚠️ Введите число от {SMOOTH_MIN_DAYS} до {SMOOTH_MAX_DAYS}")
        return
    
    days = int(message.text.strip())
    if days < SMOOTH_MIN_DAYS or days > SMOOTH_MAX_DAYS:
        await message.answer(f"⚠️ От *{SMOOTH_MIN_DAYS}* до *{SMOOTH_MAX_DAYS}* дней. Попробуйте снова:", parse_mode="Markdown")
        return
    
    await state.update_data(smooth_days=days)
    
    await message.answer(
        f"✅ Выбрано: *{days} дней*\n\n"
        f"⏱ *Шаг 2:* Теперь выберите, как часто отправлять партии в панель?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⚡ Каждые 15 минут", callback_data="interval_15")],
            [InlineKeyboardButton(text="🕐 Каждые 30 минут", callback_data="interval_30")],
            [InlineKeyboardButton(text="🕒 Каждый час", callback_data="interval_60")],
            [InlineKeyboardButton(text="🕕 Каждые 3 часа", callback_data="interval_180")],
            [InlineKeyboardButton(text="🕛 Каждые 6 часов", callback_data="interval_360")],
            [InlineKeyboardButton(text="🌙 Раз в 12 часов", callback_data="interval_720")],
            [InlineKeyboardButton(text="🌅 Раз в 24 часа", callback_data="interval_1440")],
            [InlineKeyboardButton(text="✏️ Ввести своё число (мин/час)", callback_data="interval_custom")]
        ]),
        parse_mode="Markdown"
    )
    
# НОВЫЙ ОБРАБОТЧИК ДЛЯ ИНТЕРВАЛА
@dp.callback_query(F.data.startswith("interval_"))
async def process_smooth_interval(call: CallbackQuery, state: FSMContext):
    interval_val = call.data.replace("interval_", "")
    
    # Если пользователь хочет ввести своё число
    if interval_val == "custom":
        await call.message.edit_text(
            "✏️ *Введите свой интервал*\n\n"
            "Напишите число и единицу измерения (например: `45м` или `2ч`).\n"
            "📉 Минимум 5 минут, максимум 24 часа."
        )
        return

    interval_minutes = int(interval_val)
    data = await state.get_data()
    
    plat = data.get("plat")
    key = data.get("key")
    qty = data.get("quantity")
    total = data.get("total")
    days = data.get("smooth_days", 7)
    
    if not plat or not key or not qty:
        await call.answer("⚠️ Данные потеряны", show_alert=True)
        await state.clear()
        return
    
    await state.update_data(smooth_interval=interval_minutes, priv_days=days)
    await state.set_state(OrderStates.waiting_link)
    
    item = SERVICES[plat]["items"][key]
    
    total_minutes = days * 24 * 60
    total_sends = max(1, total_minutes // interval_minutes)
    step = max(1, qty // total_sends)
    
    if interval_minutes < 60:
        interval_text = f"{interval_minutes} мин."
    else:
        interval_text = f"{interval_minutes // 60} ч."
    
    await call.message.edit_text(
        f"✅ *Режим выбран!*\n\n"
        f"🐢 *Плавно за {days} дней*\n"
        f"⏱ Интервал: *каждые {interval_text}*\n"
        f"📦 ~{step} шт. за раз\n\n"
        f"📦 {item['name']} × {qty}\n"
        f"💸 Итого: *{total} ₽*\n\n"
        f"🔗 Укажите ссылку:",
        parse_mode="Markdown"
    )
    await call.answer()

# ---------- ПОЛУЧАЕМ ССЫЛКУ И ПОКАЗЫВАЕМ К ОПЛАТЕ ----------
@dp.message(OrderStates.waiting_link)
async def process_smooth_link(message: Message, state: FSMContext):
    link = (message.text or "").strip()
    data = await state.get_data()
    plat = data.get("plat")
    key = data.get("key")
    qty = data.get("quantity")
    total = data.get("total")
    priv_days = data.get("priv_days", 0)
    smooth_interval = data.get("smooth_interval", 60)

    if not plat or not key:
        await state.clear()
        await message.answer("⚠️ Данные заказа потеряны. /start")
        return

    # Проверяем ссылку
    ok, hint = validate_link_for_service(plat, key, link)
    if not ok:
        await message.answer(hint)
        return

    item = SERVICES[plat]["items"][key]
    
    # Считаем скидки
    loyalty = get_user_discount(message.from_user.id)
    first_disc = FIRST_ORDER_DISCOUNT if db_is_first_order(message.from_user.id) else 0
    weekend = get_weekend_discount()
    total_discount = loyalty + first_disc + weekend
    
    final_total = round(total * (1 - total_discount / 100), 2)
    
    await state.update_data(link=link, final_total=final_total)
    
    balance = db_get_balance(message.from_user.id)
    enough = balance >= final_total
    status_line = f"✅ Баланс: *{balance:.2f} ₽*" if enough else f"❌ Не хватает: *{round(final_total - balance, 2)} ₽*"
    
    smooth_text = f"\n🐢 Режим: *Плавно {priv_days} дн.*" if priv_days >= 3 else "\n⚡ Режим: *Моментально*"
    
    if not enough:
        await message.answer(
            f"📋 *Проверьте заказ:*\n\n"
            f"📱 {plat.capitalize()}\n📦 {item['name']}\n🔢 Количество: *{qty}*\n🔗 `{link}`\n"
            f"💸 Стоимость: *{total} ₽*{smooth_text}\n"
            f"💰 Итого: *{final_total} ₽*\n\n{status_line}", 
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🚀 Пополнить в Mini App", web_app=WebAppInfo(url=WEBAPP_URL))],
                [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_order")]
            ])
        )
        return
        
    await message.answer(
        f"📋 *Проверьте заказ:*\n\n"
        f"📱 {plat.capitalize()}\n📦 {item['name']}\n🔢 Количество: *{qty}*\n🔗 `{link}`\n"
        f"💸 Стоимость: *{total} ₽*{smooth_text}\n"
        f"💰 Итого: *{final_total} ₽*\n\n{status_status if 'status_status' in locals() else status_line}", 
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Заказать", callback_data="confirm_order")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_order")]
        ])
    )
    
# ---------- ЕДИНАЯ ФУНКЦИЯ СОЗДАНИЯ ЗАКАЗА ----------
async def create_order_and_send(user_id, plat, key, link, qty, final_total,
                                 promo_code=None, username=None, first_name=None,
                                 priv_days=0, smooth_interval=60):
    item = SERVICES[plat]["items"][key]
    panel_name = item.get("panel", DEFAULT_PANEL)
    db_user_add(user_id, username, first_name)

    days = int(priv_days or 0)
    use_smooth = can_be_smooth(plat, key) and days >= SMOOTH_MIN_DAYS

    if use_smooth:
        # ============================================================
        # 🐢 ПЛАВНЫЙ РЕЖИМ
        # ============================================================
        days = max(SMOOTH_MIN_DAYS, min(SMOOTH_MAX_DAYS, days))
        smooth_interval = max(5, min(1440, int(smooth_interval or 60)))

        total_minutes = days * 24 * 60
        total_sends = max(1, total_minutes // smooth_interval)
        step_qty = max(10, qty // total_sends)

        order_id = db_add_order(user_id, plat, item["name"], item["id"], qty, final_total, link, panel_name)
        db_set_panel_order_id(order_id, -1)

        conn = db_connect(); cur = conn.cursor()
        # первая партия уходит сразу → last_sent_at = сейчас - интервал
        first_send_time = (datetime.now() - timedelta(minutes=smooth_interval)).strftime("%Y-%m-%d %H:%M:%S")
        cur.execute(
            "INSERT INTO privat_orders (order_id, panel, service_id, link, quantity, total_qty, "
            "step_qty, days, interval_minutes, last_sent_at, created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (order_id, panel_name, item["id"], link, qty, qty, step_qty, days, smooth_interval,
             first_send_time, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit(); conn.close()

        db_add_spent(user_id, final_total)
        db_mark_first_order(user_id)
        if promo_code:
            db_promo_use(promo_code); db_promo_mark_user(user_id, promo_code)

        user = db_get_user(user_id)
        if user and user[5]:
            ref_bonus = round(final_total * REF_BONUS_PERCENT / 100, 2)
            db_add_balance(user[5], ref_bonus)
            try: await bot.send_message(user[5], f"🎁 *Реферальный бонус!*\n\nЗаказ на {final_total} ₽ → начислено *{ref_bonus} ₽*")
            except Exception: pass

        await log_to_channel(f"🐢 Плавный заказ #{order_id} | {item['name']} × {qty} | {final_total} ₽ | {days} дн., {step_qty} шт/раз")
        await notify_channel_new_order(order_id, user_id, username, item["name"], qty, final_total, panel_name)

        int_text = f"{smooth_interval} мин." if smooth_interval < 60 else f"{smooth_interval // 60} ч."
        try:
            await bot.send_message(
                user_id,
                f"🐢 *Плавная накрутка запущена!*\n\n"
                f"📦 {item['name']} × {qty}\n"
                f"📆 Растяжка: *{days} дней*\n"
                f"⏱ Отправка: *каждые {int_text}*\n"
                f"🎯 ~{step_qty} шт. за раз.\n\n"
                f"🔔 Уведомлю о прогрессе на 25%, 50%, 75% и 100%.\n"
                f"💡 Первая партия уходит в течение 5 минут.",
                parse_mode="Markdown"
            )
        except Exception: pass

        return order_id, -1, None

    # ============================================================
    # ⚡ МОМЕНТАЛЬНЫЙ РЕЖИМ
    # ============================================================
    order_id = db_add_order(user_id, plat, item["name"], item["id"], qty, final_total, link, panel_name)
    panel_order_id, panel_error = await panel_add_order(panel_name, item["id"], link, qty)

    if panel_order_id:
        db_set_panel_order_id(order_id, panel_order_id)
        db_add_spent(user_id, final_total)
        db_mark_first_order(user_id)
        if promo_code:
            db_promo_use(promo_code); db_promo_mark_user(user_id, promo_code)

        user = db_get_user(user_id)
        if user and user[5]:
            ref_bonus = round(final_total * REF_BONUS_PERCENT / 100, 2)
            db_add_balance(user[5], ref_bonus)
            try: await bot.send_message(user[5], f"🎁 *Реферальный бонус!*\n\nЗаказ на {final_total} ₽ → начислено *{ref_bonus} ₽*")
            except Exception: pass

        await log_to_channel(f"🆕 Заказ #{order_id} | {user_id} | {item['name']} × {qty} | {final_total} ₽ | ID в панели: {panel_order_id}")
        await notify_channel_new_order(order_id, user_id, username, item["name"], qty, final_total, panel_name)
        try:
            await bot.send_message(ADMIN_ID, f"🆕 *Заказ #{order_id}*\n\n👤 {user_id}\n📱 {plat}\n📦 {item['name']}\n🔢 {qty} | 💸 {final_total} ₽\n🔗 {link}\n🖥 Панель: *SMM*\n✅ ID: `#{panel_order_id}`")
        except Exception: pass
        return order_id, panel_order_id, None

    # --- ВОЗВРАТ + АЛЬТЕРНАТИВА (если панель выдала ошибку) ---
    db_update_order_status(order_id, "error")
    await notify_admin_error(panel_error, f"Заказ #{order_id} | панель {panel_name}")
    await notify_channel_error(panel_name, item["name"], panel_error)
    db_add_balance(user_id, final_total)

    alt_item = None; alt_plat = None; alt_key = None
    for p, pdata in SERVICES.items():
        for k, it in pdata["items"].items():
            if classify_service(k) == classify_service(key) and p != "privat" and it["price"] <= final_total:
                alt_item = it; alt_plat = p; alt_key = k; break
        if alt_item: break

    if alt_item:
        try:
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=f"🔄 Заменить на {alt_item['name'][:20]}", callback_data=f"srv|{alt_plat}|{alt_key}")],
                [InlineKeyboardButton(text="💬 Поддержка", url=f"https://t.me/{SUPPORT_USERNAME}")]
            ])
            await bot.send_message(user_id, f"⚠️ *Услуга временно недоступна*\n\nПоставщик отклонил заказ. Возврат *{final_total:.2f} ₽* на баланс.\n\n💡 Попробовать аналог?\n👉 {alt_item['name']}", reply_markup=kb)
        except Exception: pass
    else:
        try:
            await bot.send_message(user_id, f"⚠️ *Ошибка панели*\n\nВозврат *{final_total:.2f} ₽* на баланс.\n\n💬 @{SUPPORT_USERNAME}")
        except Exception: pass

    try:
        await bot.send_message(ADMIN_ID, f"⚠️ *Заказ #{order_id} НЕ ушёл*\n\n👤 {user_id}\nОшибка: `{panel_error}`\n💰 Возврат")
    except Exception: pass
    return order_id, None, panel_error

    # ============================================================
    # ⚡ МОМЕНТАЛЬНЫЙ РЕЖИМ
    # ============================================================
    order_id = db_add_order(user_id, plat, item["name"], item["id"], qty, final_total, link, panel_name)
    panel_order_id, panel_error = await panel_add_order(panel_name, item["id"], link, qty)

    if panel_order_id:
        db_set_panel_order_id(order_id, panel_order_id)
        db_add_spent(user_id, final_total)
        db_mark_first_order(user_id)
        if promo_code:
            db_promo_use(promo_code); db_promo_mark_user(user_id, promo_code)

        user = db_get_user(user_id)
        if user and user[5]:
            ref_bonus = round(final_total * REF_BONUS_PERCENT / 100, 2)
            db_add_balance(user[5], ref_bonus)
            try: await bot.send_message(user[5], f"🎁 *Реферальный бонус!*\n\nЗаказ на {final_total} ₽ → начислено *{ref_bonus} ₽*")
            except Exception: pass

        await log_to_channel(f"🆕 Заказ #{order_id} | {user_id} | {item['name']} × {qty} | {final_total} ₽ | ID в панели: {panel_order_id}")
        await notify_channel_new_order(order_id, user_id, username, item["name"], qty, final_total, panel_name)
        try:
            await bot.send_message(ADMIN_ID, f"🆕 *Заказ #{order_id}*\n\n👤 {user_id}\n📱 {plat}\n📦 {item['name']}\n🔢 {qty} | 💸 {final_total} ₽\n🔗 {link}\n🖥 Панель: *SMM*\n✅ ID: `#{panel_order_id}`")
        except Exception: pass
        return order_id, panel_order_id, None

    # --- ВОЗВРАТ + АЛЬТЕРНАТИВА (если панель выдала ошибку) ---
    db_update_order_status(order_id, "error")
    await notify_admin_error(panel_error, f"Заказ #{order_id} | панель {panel_name}")
    await notify_channel_error(panel_name, item["name"], panel_error)
    db_add_balance(user_id, final_total)

    alt_item = None; alt_plat = None; alt_key = None
    for p, pdata in SERVICES.items():
        for k, it in pdata["items"].items():
            if classify_service(k) == classify_service(key) and p != "privat" and it["price"] <= final_total:
                alt_item = it; alt_plat = p; alt_key = k; break
        if alt_item: break

    if alt_item:
        try:
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=f"🔄 Заменить на {alt_item['name'][:20]}", callback_data=f"srv|{alt_plat}|{alt_key}")],
                [InlineKeyboardButton(text="💬 Поддержка", url=f"https://t.me/{SUPPORT_USERNAME}")]
            ])
            await bot.send_message(user_id, f"⚠️ *Услуга временно недоступна*\n\nПоставщик отклонил заказ. Возврат *{final_total:.2f} ₽* на баланс.\n\n💡 Попробовать аналог?\n👉 {alt_item['name']}", reply_markup=kb)
        except Exception: pass
    else:
        try:
            await bot.send_message(user_id, f"⚠️ *Ошибка панели*\n\nВозврат *{final_total:.2f} ₽* на баланс.\n\n💬 @{SUPPORT_USERNAME}")
        except Exception: pass

    try:
        await bot.send_message(ADMIN_ID, f"⚠️ *Заказ #{order_id} НЕ ушёл*\n\n👤 {user_id}\nОшибка: `{panel_error}`\n💰 Возврат")
    except Exception: pass
    return order_id, None, panel_error
        
    # ============================================================
    # ⚡ МОМЕНТАЛЬНЫЙ РЕЖИМ
    # ============================================================
    order_id = db_add_order(user_id, plat, item["name"], item["id"], qty, final_total, link, panel_name)
    panel_order_id, panel_error = await panel_add_order(panel_name, item["id"], link, qty)
    
    if panel_order_id:
        db_set_panel_order_id(order_id, panel_order_id)
        db_add_spent(user_id, final_total)
        db_mark_first_order(user_id)
        if promo_code:
            db_promo_use(promo_code)
            db_promo_mark_user(user_id, promo_code)
            
        user = db_get_user(user_id)
        if user and user[5]:
            ref_bonus = round(final_total * REF_BONUS_PERCENT / 100, 2)
            db_add_balance(user[5], ref_bonus)
            try:
                await bot.send_message(user[5], f"🎁 *Реферальный бонус!*\n\nЗаказ на {final_total} ₽ → начислено *{ref_bonus} ₽*")
            except Exception: pass
            
        await log_to_channel(f"🆕 Заказ #{order_id} | {user_id} | {item['name']} × {qty} | {final_total} ₽ | ID в панели: {panel_order_id}")
        await notify_channel_new_order(order_id, user_id, username, item["name"], qty, final_total, panel_name)
        try:
            await bot.send_message(ADMIN_ID, f"🆕 *Заказ #{order_id}*\n\n👤 {user_id}\n📱 {plat}\n📦 {item['name']}\n🔢 {qty} | 💸 {final_total} ₽\n🔗 {link}\n🖥 Панель: *SMM*\n✅ ID: `#{panel_order_id}`")
        except Exception: pass
        return order_id, panel_order_id, None
    
    # --- УМНЫЙ ВОЗВРАТ С АЛЬТЕРНАТИВОЙ ---
    db_update_order_status(order_id, "error")
    await notify_admin_error(panel_error, f"Заказ #{order_id} | панель {panel_name}")
    await notify_channel_error(panel_name, item["name"], panel_error)
    
    db_add_balance(user_id, final_total)
    
    alt_item = None
    alt_plat = None
    alt_key = None
    for p, pdata in SERVICES.items():
        for k, it in pdata["items"].items():
            if classify_service(k) == classify_service(key) and p != "privat" and it["price"] <= final_total:
                alt_item = it; alt_plat = p; alt_key = k; break
        if alt_item: break
        
    if alt_item:
        try:
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=f"🔄 Заменить на {alt_item['name'][:20]}", callback_data=f"srv|{alt_plat}|{alt_key}")],
                [InlineKeyboardButton(text="💬 Поддержка", url=f"https://t.me/{SUPPORT_USERNAME}")]
            ])
            await bot.send_message(user_id, f"⚠️ *Услуга временно недоступна*\n\nПоставщик отклонил заказ. Мы вернули вам *{final_total:.2f} ₽* на баланс.\n\n💡 Хотите попробовать аналог за те же деньги?\n👉 {alt_item['name']}", reply_markup=kb)
        except Exception: pass
    else:
        try:
            await bot.send_message(user_id, f"⚠️ *Ошибка панели*\n\nЗаказ не выполнен. Мы вернули *{final_total:.2f} ₽* на баланс.\n\n💬 Поддержка: @{SUPPORT_USERNAME}")
        except Exception: pass

    try:
        await bot.send_message(ADMIN_ID, f"⚠️ *Заказ #{order_id} НЕ ушёл*\n\n👤 {user_id}\nОшибка: `{panel_error}`\n💰 Возврат + предложен аналог")
    except Exception: pass
    return order_id, None, panel_error
    
@dp.callback_query(F.data == "confirm_order")
async def cb_confirm_order(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    plat = data.get("plat")
    key = data.get("key")
    link = data.get("link")
    qty = data.get("quantity")
    total = data.get("final_total", data.get("total", 0))
    priv_days = data.get("priv_days", 0)
    smooth_interval = data.get("smooth_interval", 60)
    promo_code = data.get("promo_code")

    if not plat or not key or not link or not qty:
        await call.message.edit_text("⚠️ Данные потеряны. Попробуйте заказать заново.")
        await state.clear()
        await call.answer()
        return

    try:
        item = SERVICES[plat]["items"][key]
    except KeyError:
        await call.message.edit_text("⚠️ Услуга не найдена в базе.")
        await state.clear()
        await call.answer()
        return

    balance = db_get_balance(call.from_user.id)
    if balance < total:
        await call.message.edit_text(f"❌ Недостаточно средств\n\n💸 Нужно: *{total} ₽*\n💰 Есть: *{balance:.2f} ₽*", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🚀 Пополнить в Mini App", web_app=WebAppInfo(url=WEBAPP_URL))]
        ]))
        await call.answer()
        return

    if not db_charge_balance(call.from_user.id, total):
        await call.message.edit_text("⚠️ Ошибка списания")
        await call.answer()
        return

    # Вызываем функцию, которая отправит в панель (с учетом дней)
    order_id, panel_order_id, panel_error = await create_order_and_send(
    call.from_user.id, plat, key, link, qty, total, promo_code, 
    call.from_user.username, call.from_user.first_name,
    priv_days=priv_days, smooth_interval=smooth_interval
)

    if panel_error:
        await call.message.edit_text(f"⚠️ *Ошибка обработки*\n\n`{panel_error}`\n\n💰 *{total} ₽* возвращены.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🆘 Поддержка", url=f"https://t.me/{SUPPORT_USERNAME}")]
        ]))
        await call.answer()
        await state.clear()
        return

    await state.clear()
    new_balance = db_get_balance(call.from_user.id)
    
    # Красивое сообщение об успехе
    smooth_text = f"\n🐢 Режим: *Плавно {priv_days} дней*" if priv_days >= 3 else "\n⚡ Режим: *Моментально*"
    await call.message.edit_text(
        f"🎉 *Заказ #{order_id} создан!*\n\n"
        f"📱 {plat.capitalize()}\n📦 {item['name']}\n🔢 {qty} шт.\n"
        f"💸 Списано: *{total} ₽*\n💰 Остаток: *{new_balance:.2f} ₽*{smooth_text}\n\n"
        f"✅ Отправлен в работу\n🔔 Пришлю уведомление о выполнении",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⭐ Оставить отзыв", callback_data=f"review_{order_id}")],
            [InlineKeyboardButton(text="💬 Поддержка", url=f"https://t.me/{SUPPORT_USERNAME}")]
        ])
    )
    await call.answer("✅ Оплачено!")
    
@dp.message(OrderStates.waiting_cart_link)
async def process_cart_link(message: Message, state: FSMContext):
    link = (message.text or "").strip()
    if not link or not link.startswith(("http://", "https://")) or "." not in link:
        await message.answer("⚠️ Пришлите полную ссылку вида `https://...`"); return
    data = await state.get_data()
    plat = data.get("cart_plat"); key = data.get("cart_key"); qty = data.get("cart_qty")
    ok, hint = validate_link_for_service(plat, key, link)
    if not ok:
        await message.answer(hint); return
    cart = data.get("cart", [])
    cart.append({"plat": plat, "key": key, "qty": qty, "link": link})
    await state.update_data(cart=cart)
    await state.set_state(None)
    item = SERVICES[plat]["items"][key]
    await message.answer(f"✅ *Добавлено в корзину!*\n\n📦 {item['name']} × {qty}\n🔗 {link}\n\n🛒 Всего в корзине: *{len(cart)}* услуг\n\n💡 Добавьте ещё {3 - len(cart)} — и получите *−10%*!")
    
@dp.callback_query(F.data == "cart_checkout")
async def cb_cart_checkout(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    cart = data.get("cart", [])
    if not cart:
        await call.answer("Корзина пуста", show_alert=True); return
    total = 0
    for item in cart:
        it = SERVICES[item["plat"]]["items"][item["key"]]
        unit = it["price"] / it["pack"]
        total += unit * item["qty"]
    total = round(total, 2)
    discount = 10 if len(cart) >= 3 else 0
    final = round(total * (1 - discount / 100), 2)
    balance = db_get_balance(call.from_user.id)
    if balance < final:
        await call.message.edit_text(f"❌ *Недостаточно средств*\n\n💸 Нужно: *{final:.2f} ₽*\n💰 Есть: *{balance:.2f} ₽*", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💳 Пополнить", callback_data="topup")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_platforms")]
        ]))
        return
    if not db_charge_balance(call.from_user.id, final):
        await call.answer("⚠️ Ошибка списания", show_alert=True); return
    db_add_spent(call.from_user.id, final)
    db_mark_first_order(call.from_user.id)
    ok = 0; fail = 0
    for item in cart:
        plat = item["plat"]; key = item["key"]; qty = item["qty"]; link = item["link"]
        it = SERVICES[plat]["items"][key]
        panel_name = it.get("panel", DEFAULT_PANEL)
        unit = it["price"] / it["pack"]
        base = round(unit * qty, 2)
        price = round(base * (1 - discount / 100), 2)
        order_id = db_add_order(call.from_user.id, plat, it["name"], it["id"], qty, price, link, panel_name)
        panel_order_id, err = await panel_add_order(panel_name, it["id"], link, qty)
        if panel_order_id:
            db_set_panel_order_id(order_id, panel_order_id)
            ok += 1
            await log_to_channel(f"🛒 Корзина #{order_id} | {call.from_user.id} | {it['name']} × {qty} | {price} ₽ | ID: {panel_order_id}")
        else:
            db_add_balance(call.from_user.id, price)
            db_update_order_status(order_id, "error")
            fail += 1
            await log_to_channel(f"⚠️ Корзина #{order_id} НЕ ушла | {it['name']} × {qty} | {err}")
    await state.update_data(cart=[])
    new_balance = db_get_balance(call.from_user.id)
    text = f"🎉 *Корзина оплачена!*\n\n✅ Успешно: *{ok}*\n"
    if fail: text += f"⚠️ Ошибок: *{fail}*\n"
    text += f"\n💸 Списано: *{final:.2f} ₽*\n💰 Остаток: *{new_balance:.2f} ₽*"
    await call.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Мои заказы", callback_data="history_menu")]
    ]))
    await call.answer("✅ Оплачено!")

# ---------- ПАКЕТЫ ----------
@dp.message(F.text == "🎁 Пакеты")
async def msg_bundles(message: Message):
    text = "🎁 *Магазин и Услуги*\n\n🎯 *По типу действия* — накрутка соцсетей\n📦 *Готовые сборки* — комплекты для соцсетей\n🎮 *Игровые услуги* — донат и сопровождение 👇"
    kb_rows = [
        [InlineKeyboardButton(text="🎯 По типу действия", callback_data="action_menu")],
        [InlineKeyboardButton(text="📦 Готовые сборки", callback_data="bundles_menu")],
        [InlineKeyboardButton(text="🎮 Игры и Донат", callback_data="game_menu")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_platforms")],
    ]
    await message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows))

@dp.callback_query(F.data == "bundles_back_main")
async def cb_bundles_back_main(call: CallbackQuery):
    await msg_bundles(call.message)
    await call.answer()

@dp.callback_query(F.data == "bundles_menu")
async def cb_bundles_menu(call: CallbackQuery):
    text = "🎁 *Готовые сборки*\n\nВыберите категорию:"
    counts = {}
    for b in BUNDLES.values():
        cat = b.get("category", "universal")
        counts[cat] = counts.get(cat, 0) + 1
    kb_rows = []
    for cat_key, cat_data in BUNDLE_CATEGORIES.items():
        cnt = counts.get(cat_key, 0)
        if cnt == 0: continue
        kb_rows.append([InlineKeyboardButton(text=f"{cat_data['emoji']} {cat_data['name']} ({cnt})", callback_data=f"bcat_{cat_key}")])
    kb_rows.append([InlineKeyboardButton(text="🔙 Назад", callback_data="bundles_back_main")])
    try:
        await call.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows))
    except Exception:
        await call.message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows))
    await call.answer()

@dp.callback_query(F.data.startswith("bcat_"))
async def cb_bundle_category(call: CallbackQuery):
    cat = call.data.replace("bcat_", "")
    if cat not in BUNDLE_CATEGORIES:
        await call.answer("Категория недоступна", show_alert=True); return
    cat_bundles = {k: v for k, v in BUNDLES.items() if v.get("category") == cat}
    if not cat_bundles:
        await call.answer("В этой категории пока нет пакетов", show_alert=True); return
    cat_data = BUNDLE_CATEGORIES[cat]
    text = f"{cat_data['emoji']} *{cat_data['name']} — пакеты:*\n\n"
    kb_rows = []
    for bkey, bundle in cat_bundles.items():
        if "fixed_price" in bundle:
            final = bundle["fixed_price"]
        else:
            total = 0
            for plat, item_key, qty in bundle["items"]:
                it = SERVICES[plat]["items"][item_key]
                unit = it["price"] / it["pack"]
                total += unit * qty
            final = round(total * (1 - bundle["discount"] / 100), 2)
        text += f"*{bundle['name']}*\n{bundle['desc']}\n💰 {final:.2f} ₽ (скидка {bundle.get('discount', 0)}%)\n\n"
        kb_rows.append([InlineKeyboardButton(text=f"{bundle['name']} — {final:.0f} ₽", callback_data=f"bundle_{bkey}")])
    kb_rows.append([InlineKeyboardButton(text="🔙 К категориям", callback_data="bundles_menu")])
    try:
        await call.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows))
    except Exception:
        await call.message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows))
    await call.answer()
    
@dp.callback_query(F.data.startswith("bundle_"))
async def cb_bundle(call: CallbackQuery, state: FSMContext):
    if call.data == "bundleconfirm":
        return
    bundle_key = call.data.replace("bundle_", "")
    bundle = BUNDLES.get(bundle_key)
    if not bundle:
        await call.answer("Пакет недоступен", show_alert=True); return
    if "fixed_price" in bundle:
        total = bundle["fixed_price"]; final = bundle["fixed_price"]
        lines = [f"• {SERVICES[p]['items'][k]['name']} × {q}" for p, k, q in bundle["items"]]
    else:
        total = 0; lines = []
        for plat, item_key, qty in bundle["items"]:
            it = SERVICES[plat]["items"][item_key]
            unit = it["price"] / it["pack"]
            price = round(unit * qty, 2)
            total += price
            lines.append(f"• {it['name']} × {qty} — {price:.2f} ₽")
        total = round(total, 2)
        final = round(total * (1 - bundle["discount"] / 100), 2)
    if db_orders_last_hour(call.from_user.id) + len(bundle["items"]) > MAX_ORDERS_PER_HOUR:
        await call.answer("🚫 Слишком много заказов в час. Попробуйте позже.", show_alert=True); return
    if db_count_orders_today(call.from_user.id) + len(bundle["items"]) > MAX_ORDERS_PER_DAY:
        await call.answer("🚫 Дневной лимит заказов. Заходите завтра!", show_alert=True); return
    if db_sum_orders_last_hour(call.from_user.id) + final > MAX_SUM_PER_HOUR:
        await call.answer("🚫 Лимит суммы за час. Попробуйте позже.", show_alert=True); return
    balance = db_get_balance(call.from_user.id)
    if balance < final:
        await call.message.answer(f"❌ Недостаточно средств для пакета\n\n💸 Нужно: *{final:.2f} ₽*\n💰 Есть: *{balance:.2f} ₽*", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💳 Пополнить", callback_data="topup")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_order")]
        ]))
        await call.answer(); return
    await state.update_data(bundle_key=bundle_key, bundle_step=0, bundle_links=[])
    await state.set_state(OrderStates.bundle_waiting_link)
    first_plat, first_key, first_qty = bundle["items"][0]
    first_item = SERVICES[first_plat]["items"][first_key]
    await call.message.answer(f"🎁 *{bundle['name']}*\n\n" + "\n".join(lines) + f"\n\n💸 Итого: *{final:.2f} ₽* (скидка {bundle.get('discount', 0)}%)\n\n📌 *Шаг 1 из {len(bundle['items'])}:*\n🔗 Укажите ссылку для *{first_item['name']}* ({first_qty} шт)")
    await call.answer()
    
# ============ ОБРАБОТЧИК ДАННЫХ ИЗ MINI APP ============        
async def create_topup_invoice(user_id, amount_rub):
    try:
        amount_usdt = round(amount_rub / USDT_TO_RUB, 2)
        if amount_usdt < 0.1: amount_usdt = 0.1
            
        invoice = await crypto.create_invoice(
            asset="USDT",
            amount=amount_usdt,
            payload=str(user_id),
            description=f"Пополнение баланса Ismaboost на {amount_rub} ₽"
        )
        
        text = (
            f"✨💎 **СЧЕТ СОЗДАН!** 💎✨\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 Сумма пополнения: **{amount_rub} ₽**\n"
            f"💵 К оплате в крипте: **{amount_usdt} USDT**\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👇 Жми кнопку ниже, чтобы перейти к оплате 🚀"
        )
        
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"💳 Оплатить {amount_usdt} USDT", url=invoice.bot_invoice_url)],
            [InlineKeyboardButton(text="🔄 Я оплатил, проверить", callback_data="check_payment")]
        ])
        
        await bot.send_message(user_id, text, reply_markup=kb, parse_mode="Markdown")
    except Exception as e:
        await bot.send_message(user_id, f"⚠️ Ошибка при создании счета: {e}")


# --- ОБРАБОТЧИК КНОПКИ "ПОПОЛНИТЬ" ---
@dp.callback_query(F.data == "topup")
async def cb_topup_start(call: CallbackQuery, state: FSMContext):
    text = (
        "✨💎 **ПОПОЛНЕНИЕ БАЛАНСА** 💎✨\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "👋 Выбери удобный способ оплаты:\n\n"
        "🪙 **Криптовалюта (CryptoBot)** — мгновенное зачисление, без комиссий.\n"
        "🏦 **СБП (Перевод на карту)** — ручное подтверждение (до 15 минут).\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "👇 Жми на кнопку ниже 👇"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🪙 Оплатить Криптой (CryptoBot)", callback_data="topup_crypto")],
        [InlineKeyboardButton(text="🏦 Оплатить через СБП (Т-Банк)", callback_data="topup_sbp")],
        [InlineKeyboardButton(text="🔙 Отмена", callback_data="main_menu")]
    ])
    
    await call.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    await call.answer()
    
    # --- ВЫБОР КРИПТЫ ---
@dp.callback_query(F.data == "topup_crypto")
async def cb_topup_crypto(call: CallbackQuery, state: FSMContext):
    text = (
        "🪙 **ПОПОЛНЕНИЕ ЧЕРЕЗ КРИПТУ** 🪙\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "⚡️ Это самый быстрый и безопасный способ!\n"
        "🛡 Мы используем официального бота @CryptoBot.\n\n"
        "💵 Баланс зачисляется **автоматически** в течение 1-2 минут после перевода.\n"
        "📉 Комиссия сети оплачивается автоматически.\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "📝 Напиши в чат, на сколько рублей ты хочешь пополнить?\n"
        "💰 Например: `500`\n\n"
        "🔙 Чтобы отменить, напиши /start"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Назад", callback_data="topup")]])
    
    # Устанавливаем стейт с пометкой, что выбран КРИПТА
    await state.update_data(topup_type="crypto")
    await state.set_state(OrderStates.waiting_topup_amount)
    
    await call.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    await call.answer()

# --- ВЫБОР СБП ---
@dp.callback_query(F.data == "topup_sbp")
async def cb_topup_sbp(call: CallbackQuery, state: FSMContext):
    text = (
        "⚡️ **СБП ПЕРЕВОД** ⚡️\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "• 🏛 Банк: Т-Банк [Тинькофф] ✨\n"
        "• 👤 Юзер: Исмаил Б. ✨\n"
        "• 📱 Тел: `8 928 593-72-12` 🎯\n"
        "• ⭐ Статус: Ожидание оплаты 📥\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "⚠️ **ВАЖНО:**\n"
        "📉 Переводы **меньше 100 ₽** могут привести к блокировке карт! 🚫\n"
        "💡 Минимальная сумма — **100 ₽**.\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "📝 Напиши в чат, на сколько рублей ты сделал перевод?\n"
        "💰 Например: `500`\n\n"
        "🔙 Чтобы отменить, напиши /start"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📸 Я перевел(а), отправить чек", callback_data="send_sbp_receipt")]
    ])
    
    # Устанавливаем стейт с пометкой, что выбран СБП
    await state.update_data(topup_type="sbp")
    await state.set_state(OrderStates.waiting_topup_amount)
    
    await call.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    await call.answer()

# --- ПРОВЕРКА ОПЛАТЫ ---
@dp.callback_query(F.data == "check_payment")
async def cb_check_payment(call: CallbackQuery):
    await call.answer("⏳ Проверяю платеж... Если оплата прошла, баланс обновится в течение минуты. 🚀", show_alert=True)
    
@dp.message(F.web_app_data)
async def handle_webapp_data(message: Message, state: FSMContext):
    try:
        data = json.loads(message.web_app_data.data)
    except Exception as e:
        print(f"⚠️ webapp_data: не удалось распарсить JSON: {e}")
        await message.answer("⚠️ Не удалось разобрать данные из Mini App.\nПопробуйте ещё раз.")
        return
    
    action = data.get("action")
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name

    # --- СИНХРОНИЗАЦИЯ БАЛАНСА ---
    if action == "get_balance":
        db_user_add(user_id, username, first_name)
        balance = db_get_balance(user_id)
        url = f"{WEBAPP_URL}#balance_{balance:.2f}"
        await message.answer(
            f"💳 *Актуальный баланс:*\n\n💰 *{balance:.2f} ₽*\n\n👇 Нажмите кнопку ниже:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=f"🔄 Обновить (баланс: {balance:.2f} ₽)", web_app=WebAppInfo(url=url))]
            ])
        )
        return

    # --- ЗАКАЗ ИЗ MINI APP (ПОДТВЕРЖДЕНИЕ) ---
    if action == "order":
        plat = data.get("plat")
        key = data.get("service")
        name = data.get("name")
        link = (data.get("link") or "").strip()
        qty = int(data.get("qty", 0))
        price = float(data.get("price", 0))
        is_gift = data.get("is_gift", False)
        gift_target = data.get("gift_target")
        priv_days = int(data.get("priv_days", 0))  # Получаем выбранные дни

        if not plat or not key or not link or qty < 1:
            await message.answer("⚠️ Некорректные данные заказа из Mini App.")
            return
        if plat not in SERVICES or key not in SERVICES[plat]["items"]:
            await message.answer("⚠️ Услуга не найдена.")
            return
        ok, hint = validate_link_for_service(plat, key, link)
        if not ok:
            await message.answer(hint)
            return

        balance = db_get_balance(user_id)
        if balance < price:
            await message.answer(f"❌ *Недостаточно средств!*\n\n💸 Нужно: *{price:.2f} ₽*\n💰 У вас: *{balance:.2f} ₽*", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🚀 Пополнить", web_app=WebAppInfo(url=WEBAPP_URL))]
            ]), parse_mode="Markdown")
            return

        await state.update_data(
            pay_plat=plat, pay_key=key, pay_link=link,
            pay_qty=qty, pay_price=price, pay_name=name,
            pay_username=username, pay_first_name=first_name,
            pay_is_gift=is_gift, pay_gift_target=gift_target,
            pay_priv_days=priv_days
        )

        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Да, оплатить", callback_data="pay_yes")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="pay_no")]
        ])
        
        gift_line = f"\n🎁 *Подарок для:* {gift_target}" if is_gift else ""
        smooth_line = f"\n🐢 *Плавно:* {priv_days} дней" if priv_days >= 3 else "\n⚡ *Моментально*"
        
        await message.answer(
            f"💳 *Подтверждение заказа*\n\n"
            f"📱 Платформа: {plat.capitalize()}\n"
            f"📦 Услуга: {name}\n"
            f"🔢 Количество: {qty}\n"
            f"🔗 Ссылка: {link}\n"
            f"💰 К оплате: *{price:.2f} ₽*{gift_line}{smooth_line}\n\n"
            f"Подтверждаете покупку?",
            reply_markup=markup, parse_mode="Markdown"
        )
        return

    # --- КОМАНДЫ ---
    if action == "command":
        cmd_text = data.get("text", "")
        if cmd_text == "/orders": await msg_orders(message)
        elif cmd_text == "/top": await msg_top(message)
        elif cmd_text == "/profile": await msg_profile(message)
        elif cmd_text == "/help": await msg_ask(message)
        return

    # --- ПОПОЛНЕНИЕ ---
    if action == "topup":
        amount = int(data.get("amount", 0))
        if amount < 100:
            await message.answer("⚠️ Минимум 100 ₽")
            return
        await create_topup_invoice(user_id, amount)
        return

    # --- VIP ТЕМЫ ---
    if action == "buy_vip_15":
        price = 49
        if db_charge_balance(user_id, price):
            conn = db_connect(); cur = conn.cursor()
            cur.execute("UPDATE users SET theme_tier = 'vip15' WHERE user_id=?", (user_id,))
            conn.commit(); conn.close()
            await message.answer("⭐ *15 тем разблокированы!*")
        else:
            await message.answer("❌ Недостаточно средств для покупки 15 тем.")
        return

    if action == "buy_vip_30d":
        price = 150
        if db_charge_balance(user_id, price):
            expire_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
            conn = db_connect(); cur = conn.cursor()
            cur.execute("INSERT OR REPLACE INTO vip_users (user_id, expire_date) VALUES (?, ?)", (user_id, expire_date))
            cur.execute("UPDATE users SET theme_tier = 'all' WHERE user_id=?", (user_id,))
            conn.commit(); conn.close()
            await message.answer("👑 *VIP АКТИВИРОВАН!* Все 32 темы открыты.")
        else:
            await message.answer("❌ Недостаточно средств.")
        return
        
    # --- РУЛЕТКА ---
    if action == "buy_wheel_spin":
        wheel = data.get("wheel")
        price = float(data.get("price", 0))
        builder = InlineKeyboardBuilder()
        builder.button(text="✅ Да", callback_data=f"confirm_wheel|{wheel}|{price}")
        builder.button(text="❌ Нет", callback_data="cancel_wheel")
        builder.adjust(2)
        wheel_name = "Лёгкая" if wheel == "light" else "Про"
        await message.answer(f"🎰 Вы хотите купить попытку в рулетке *{wheel_name}* за *{price:.0f} ₽*?", reply_markup=builder.as_markup(), parse_mode="Markdown")
        return

    # --- КОРЗИНА ---
    if action == "order_cart":
        cart = data.get("cart", [])
        total = float(data.get("total", 0))
        if not cart:
            await message.answer("⚠️ Корзина пуста")
            return
        balance = db_get_balance(user_id)
        if balance < total:
            await message.answer(f"❌ *Недостаточно средств!*\n\n💸 Нужно: *{total:.2f} ₽*\n💰 У вас: *{balance:.2f} ₽*", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🚀 Пополнить", web_app=WebAppInfo(url=WEBAPP_URL))]
            ]), parse_mode="Markdown")
            return
        
        if not db_charge_balance(user_id, total):
            await message.answer("⚠️ Ошибка списания.")
            return
            
        db_add_spent(user_id, total)
        db_mark_first_order(user_id)
        ok, fail = 0, 0
        
        for item in cart:
            plat = item["plat"]
            key = item["key"]
            qty = item["qty"]
            link = item["link"]
            priv_days = item.get("priv_days", 0)
            
            it = SERVICES[plat]["items"][key]
            
            # Используем нашу новую функцию
            order_id, panel_id, err = await create_order_and_send(
                user_id, plat, key, link, qty, item["finalTotal"], 
                priv_days=priv_days, username=username, first_name=first_name
            )
            if err:
                fail += 1
            else:
                ok += 1
                
        new_balance = db_get_balance(user_id)
        text = f"🎉 *Корзина оплачена!*\n\n✅ Успешно: *{ok}*\n"
        if fail: text += f"⚠️ Ошибок: *{fail}*\n"
        text += f"\n💸 Списано: *{total:.2f} ₽*\n💰 Остаток: *{new_balance:.2f} ₽*"
        
        await message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📋 Мои заказы", callback_data="history_menu")]
        ]))
        return

    # --- НЕИЗВЕСТНОЕ ДЕЙСТВИЕ ---
    await message.answer(f"⚠️ Неизвестное действие: `{action}`")


# ===== ОБРАБОТЧИК КНОПКИ "ДА, ОПЛАТИТЬ" =====
@dp.callback_query(F.data == "pay_yes")
async def process_payment_yes(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    plat = data.get("pay_plat")
    key = data.get("pay_key")
    link = data.get("pay_link")
    qty = data.get("pay_qty")
    price = data.get("pay_price")
    is_gift = data.get("pay_is_gift", False)
    gift_target = data.get("pay_gift_target")
    priv_days = data.get("pay_priv_days", 0)
    smooth_interval = int(data.get("smooth_interval", 60))

    if not plat or not key or not link or not qty or not price:
        await call.message.edit_text("⚠️ Данные заказа устарели. Оформите заново.")
        await state.clear()
        await call.answer()
        return

    balance = db_get_balance(call.from_user.id)
    if balance < price:
        await call.message.edit_text(f"❌ *Недостаточно средств!*\n\n💸 Нужно: *{price:.2f} ₽*\n💰 У вас: *{balance:.2f} ₽*", parse_mode="Markdown")
        await state.clear()
        await call.answer()
        return

    if not db_charge_balance(call.from_user.id, price):
        await call.message.edit_text("⚠️ Ошибка списания.")
        await state.clear()
        await call.answer()
        return

    # ВЫЗОВ ФУНКЦИИ (с правильными отступами)
    order_id, panel_order_id, panel_error = await create_order_and_send(
    call.from_user.id, plat, key, link, qty, total, promo_code,
    call.from_user.username, call.from_user.first_name,
    priv_days=data.get("priv_days", 0), 
    smooth_interval=data.get("smooth_interval", 60)
)

    if panel_error:
        db_add_balance(call.from_user.id, price)
        await call.message.edit_text(
            f"⚠️ *Ошибка панели:*\n`{panel_error}`\n\n💰 *{price:.2f} ₽* возвращены на баланс.", 
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🆘 Поддержка", url=f"https://t.me/{SUPPORT_USERNAME}")]
            ]), 
            parse_mode="Markdown"
        )
        await state.clear()
        await call.answer()
        return

    item = SERVICES[plat]["items"][key]
    new_balance = db_get_balance(call.from_user.id)
    
    if is_gift and gift_target:
        try:
            friend = db_find_user_by_username(gift_target.lstrip("@"))
            if friend:
                await bot.send_message(friend[0], f"🎉 *Вам подарок!*\n\n👤 От: @{call.from_user.username or call.from_user.first_name}\n📦 {item['name']} × {qty}\n🔗 {link}\n\nЗаказ в работе 🚀")
        except Exception: 
            pass

    smooth_text = f"\n🐢 *Режим:* Плавно за {priv_days} дней" if priv_days >= 3 else "\n⚡ *Режим:* Моментально"
    
    url = f"{WEBAPP_URL}#balance_{new_balance:.2f}"
    success_text = (
        f"🎉🚀 *УСПЕХ! ЗАКАЗ ЗАПУЩЕН!* 🚀🎉\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 *Заказ:* `#{order_id}`\n"
        f"📱 *Платформа:* {plat.capitalize()}\n"
        f"📦 *Услуга:* {item['name']}\n"
        f"🔢 *Количество:* {qty} шт.\n"
        f"🔗 *Ссылка:* `{link}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💸 *Списано:* {price:.2f} ₽\n"
        f"💰 *Остаток:* {new_balance:.2f} ₽\n"
        f"🖥 *Статус:* ⏳ Ожидает начала\n{smooth_text}\n\n"
        f"✅ _Заказ передан в панель._"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"📱 Открыть Mini App (баланс: {new_balance:.2f} ₽)", web_app=WebAppInfo(url=url))],
        [InlineKeyboardButton(text="🆘 Поддержка", url=f"https://t.me/{SUPPORT_USERNAME}")]
    ])
    
    await call.message.edit_text(success_text, reply_markup=kb, parse_mode="Markdown")
    await state.clear()
    await call.answer("✅ Оплачено!")


@dp.callback_query(F.data == "pay_no")
async def process_payment_no(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text("❌ Заказ отменён.")
    await call.answer()
    
# ============ ИГРЫ ============
@dp.callback_query(F.data == "game_menu")
async def cb_game_menu(call: CallbackQuery):
    text = "🎮 *Выберите игру или услугу:*"
    kb_rows = [
        [InlineKeyboardButton(text="🏆 PUBG Сопровождение", callback_data="game_pubg_carry")],
        [InlineKeyboardButton(text="🔫 PUBG Mobile (UC)", callback_data="game_pubg")],
        [InlineKeyboardButton(text="👑 Metro (Сопровождение)", callback_data="game_metro")],
        [InlineKeyboardButton(text="⭐ Brawl Stars", callback_data="game_brawl")],
        [InlineKeyboardButton(text="🟥 Roblox (Robux)", callback_data="game_roblox")],
        [InlineKeyboardButton(text="🚗 Black Russia (Коины)", callback_data="game_br")],
        [InlineKeyboardButton(text="🌲 Скупка Голды (BR)", callback_data="game_gold_sell")],
        [InlineKeyboardButton(text="🅿️ Car Parking 2 (Аккаунты)", callback_data="game_car_parking")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="bundles_back_main")],
    ]
    await call.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows))
    await call.answer()
    
@dp.callback_query(F.data == "game_pubg")
async def cb_game_pubg(call: CallbackQuery):
    text = "🔫 *PUBG Mobile UC*\n\nВыберите количество UC.\n⚠️ *Внимание:* Для зачисления потребуется ID игрока.\n\nПосле оплаты с вами свяжется поддержка для уточнения ID."
    kb_rows = [
        [InlineKeyboardButton(text="60 UC — 92 ₽", callback_data="buy_game|PUBG 60 UC|92")],
        [InlineKeyboardButton(text="120 UC — 194 ₽", callback_data="buy_game|PUBG 120 UC|194")],
        [InlineKeyboardButton(text="325 UC — 468 ₽", callback_data="buy_game|PUBG 325 UC|468")],
        [InlineKeyboardButton(text="385 UC — 573 ₽", callback_data="buy_game|PUBG 385 UC|573")],
        [InlineKeyboardButton(text="660 UC — 921 ₽", callback_data="buy_game|PUBG 660 UC|921")],
        [InlineKeyboardButton(text="1320 UC — 1831 ₽", callback_data="buy_game|PUBG 1320 UC|1831")],
        [InlineKeyboardButton(text="1800 UC — 2363 ₽", callback_data="buy_game|PUBG 1800 UC|2363")],
        [InlineKeyboardButton(text="2460 UC — 3164 ₽", callback_data="buy_game|PUBG 2460 UC|3164")],
        [InlineKeyboardButton(text="3850 UC — 4500 ₽", callback_data="buy_game|PUBG 3850 UC|4500")],
        [InlineKeyboardButton(text="5650 UC — 6721 ₽", callback_data="buy_game|PUBG 5650 UC|6721")],
        [InlineKeyboardButton(text="8100 UC — 8921 ₽", callback_data="buy_game|PUBG 8100 UC|8921")],
        [InlineKeyboardButton(text="11950 UC — 13350 ₽", callback_data="buy_game|PUBG 11950 UC|13350")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="game_menu")],
    ]
    await call.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows))
    await call.answer()

@dp.callback_query(F.data == "game_pubg_carry")
async def cb_game_pubg_carry(call: CallbackQuery):
    text = f"🏆 *GOLD СОПРОВОЖДЕНИЕ | ELITE 8* 🏆\n\n🎒 *СТАРТОВЫЙ НАБОР:*\n• Фулл 6 сет (с рюкзаком)\n• Освинцованная ткань\n• Два ремня 🎗️\n• МК14 (высшая) + фулл обвесы 🔫\n\n💰 *ГАРАНТИЯ ВЫНОСА:*\n• ☢️ С радиации: от 9 000 000 до 15 000 000\n• 👥 С людей: от 10 до 15 высших пушек\n• 🎟️ Бонус: 5–10 золотых билетов!\n\n📜 *Правила:*\n1. Иметь динамик\n2. Слушать сопровождающих\n3. Не оскорблять\n4. Не пушить без разрешения\n⚠️ За нарушение — 3 предупреждения и отмена без возврата.\n\n💵 *Цена: 249 ₽*\n📝 Писать: @{SUPPORT_USERNAME}"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Написать для заказа", url=f"https://t.me/{SUPPORT_USERNAME}")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="game_menu")]
    ])
    await call.message.edit_text(text, reply_markup=kb)
    await call.answer()

@dp.callback_query(F.data == "game_metro")
async def cb_game_metro(call: CallbackQuery):
    text = f"👑 *IsmaShop — Metro*\n\n🔥 *СОПРОВОД — 12 ЛЯМ РАДИКА*\n💰 *ВСЕГО 149 ₽*\n\n🎁 *В СОПРОВОД ВХОДИТ:*\n🔷 Фулл 6\n🔷 МК ВК\n🔷 Вещи с типов\n🔷 Помощь на протяжении сопровода\n\n⚡ Быстро • Чётко • Без лишнего\n📩 Заказ: через бота!\n\n🔥 Хочешь лут — пиши прямо сейчас!"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Написать для заказа", url=f"https://t.me/{SUPPORT_USERNAME}")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="game_menu")]
    ])
    await call.message.edit_text(text, reply_markup=kb)
    await call.answer()

@dp.callback_query(F.data == "game_brawl")
async def cb_game_brawl(call: CallbackQuery):
    text = "⭐ *Brawl Stars*\n\nВыберите нужный пропуск.\n⚠️ *Важно:* После оплаты нужно будет прислать данные аккаунта (Supercell ID)."
    kb_rows = [
        [InlineKeyboardButton(text="Black Pass — 1194 ₽", callback_data="buy_game|Brawl Black Pass|1194")],
        [InlineKeyboardButton(text="Brawl Pass Plus — 1574 ₽", callback_data="buy_game|Brawl Pass Plus|1574")],
        [InlineKeyboardButton(text="Pro Pass — 3106 ₽", callback_data="buy_game|Brawl Pro Pass|3106")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="game_menu")],
    ]
    await call.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows))
    await call.answer()

@dp.callback_query(F.data == "game_roblox")
async def cb_game_roblox(call: CallbackQuery):
    text = "🟥 *Roblox (Robux)*\n\n💎 ПЕРЕД ОПЛАТОЙ ПРОВЕРЬТЕ СВОЙ ПАРОЛЬ\n💎 Если стоит 2FA и не знаете игры — отключите 2FA.\n💎 Время выполнения: быстрое.\n💎 После оплаты отправьте логин и пароль.\n💎 Я захожу на аккаунт и оплачиваю Робукс со своей карты.\n\n❤️ НУЖЕН ПОДТВЕРЖДЕННЫЙ ЛЮБОЙ ВОЗРАСТ!\n\nНе забудьте сменить пароль после заказа."
    kb_rows = [
        [InlineKeyboardButton(text="80 Robux (РФ) — 127 ₽", callback_data="buy_game|Roblox 80 Robux РФ|127")],
        [InlineKeyboardButton(text="500 Robux (РФ) — 763 ₽", callback_data="buy_game|Roblox 500 Robux РФ|763")],
        [InlineKeyboardButton(text="600 Robux (РФ) — 912 ₽", callback_data="buy_game|Roblox 600 Robux РФ|912")],
        [InlineKeyboardButton(text="800 Robux (РФ) — 1015 ₽", callback_data="buy_game|Roblox 800 Robux РФ|1015")],
        [InlineKeyboardButton(text="1000 Robux (США) — 1148 ₽", callback_data="buy_game|Roblox 1000 Robux США|1148")],
        [InlineKeyboardButton(text="1500 Robux (США) — 1489 ₽", callback_data="buy_game|Roblox 1500 Robux США|1489")],
        [InlineKeyboardButton(text="1200 Robux (РФ) — 1772 ₽", callback_data="buy_game|Roblox 1200 Robux РФ|1772")],
        [InlineKeyboardButton(text="1500 Robux (РФ) — 1899 ₽", callback_data="buy_game|Roblox 1500 Robux РФ|1899")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="game_menu")],
    ]
    await call.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows))
    await call.answer()
    

@dp.callback_query(F.data == "game_br")
async def cb_game_br(call: CallbackQuery, state: FSMContext):
    await state.set_state(OrderStates.waiting_br_server)
    await call.message.edit_text("🚗 *Black Russia (Коины)*\n\nДля начала доната выберите ваш сервер.\n\nНапишите номер или название сервера в чат (например: `1` или `Red`):", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="game_menu")]
    ]))
    await call.answer()
    
@dp.message(OrderStates.waiting_br_server)
async def process_br_server(message: Message, state: FSMContext):
    server = (message.text or "").strip()
    if not server:
        await message.answer("⚠️ Пожалуйста, напишите сервер:"); return
    await state.update_data(br_server=server)
    await state.set_state(OrderStates.waiting_br_nick)
    await message.answer(f"✅ Сервер: *{server}*\n\nТеперь напишите ваш *ник* (или ID) в Black Russia:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="game_menu")]
    ]))

@dp.message(OrderStates.waiting_br_nick)
async def process_br_nick(message: Message, state: FSMContext):
    nick = (message.text or "").strip()
    if not nick:
        await message.answer("⚠️ Пожалуйста, напишите ваш ник:"); return
    await state.update_data(br_nick=nick)
    await state.set_state(None)
    data = await state.get_data()
    server = data.get("br_server", "-")
    text = "🚗 *Black Russia (Коины)*\n\n" + f"📌 Сервер: *{server}*\n👤 Ник: *{nick}*\n\n🔴 Доначу на все сервера\n🔥 *Х2 Акция по выходным!*\n\n💸 *Цена: 1.50 ₽ за 1 шт.*\n⚠️ *Строго от 10 штук!*\n\n👇 Выберите готовый пакет или введите своё количество:"
    kb_rows = [
        [InlineKeyboardButton(text="10 коинов — 15 ₽", callback_data="buy_game|BR 10 коинов|15")],
        [InlineKeyboardButton(text="50 коинов — 75 ₽", callback_data="buy_game|BR 50 коинов|75")],
        [InlineKeyboardButton(text="100 коинов — 150 ₽", callback_data="buy_game|BR 100 коинов|150")],
        [InlineKeyboardButton(text="500 коинов — 750 ₽", callback_data="buy_game|BR 500 коинов|750")],
        [InlineKeyboardButton(text="1000 коинов — 1500 ₽", callback_data="buy_game|BR 1000 коинов|1500")],
        [InlineKeyboardButton(text="⌨️ Ввести своё количество", callback_data="game_br_custom")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="game_menu")],
    ]
    await message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows))

@dp.callback_query(F.data == "game_br_custom")
async def cb_game_br_custom(call: CallbackQuery, state: FSMContext):
    await state.set_state(OrderStates.waiting_game_amount)
    await state.update_data(game_name="Black Russia (Коины)", game_price_per_unit=1.50)
    await call.message.edit_text("⌨️ *Введите количество коинов*\n\nНапример: `25`\n⚠️ Минимум 10 штук\nЦена: 1.50 ₽ за 1 шт.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="game_br")]
    ]))
    await call.answer()

@dp.message(OrderStates.waiting_game_amount)
async def process_game_amount(message: Message, state: FSMContext):
    if not message.text or not message.text.strip().isdigit():
        await message.answer("⚠️ Введите число (например: 25)"); return
    qty = int(message.text.strip())
    data = await state.get_data()
    game_name = data.get("game_name", "Товар")
    price_per_unit = data.get("game_price_per_unit", 0)
    if qty < 10:
        await message.answer("⚠️ Минимум 10 штук. Введите снова:"); return
    total_price = round(qty * price_per_unit, 2)
    text = f"📋 *Проверьте заказ:*\n\n🎮 {game_name}\n🔢 Количество: *{qty}* шт.\n💸 К оплате: *{total_price} ₽*\n\n💰 Ваш баланс: *{db_get_balance(message.from_user.id):.2f} ₽*"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Оплатить товар", callback_data=f"confirm_custom_game|{game_name}|{qty}|{total_price}")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="game_br")]
    ])
    await state.set_state(None)
    await message.answer(text, reply_markup=kb)

@dp.callback_query(F.data == "game_gold_sell")
async def cb_game_gold_sell(call: CallbackQuery):
    text = f"🌲 *СКУПКА ГОЛДЫ (Standoff)* 🌲\n\n💎 Курс — *0.65 ₽* за 1 голду.\n✔️ Комиссии нету.\n🎈 Моментальная оплата.\n✨ Любые объёмы.\n\n❕ *ПИШИТЕ В ЛС* ❗️"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Продать голду", url=f"https://t.me/{SUPPORT_USERNAME}")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="game_menu")]
    ])
    await call.message.edit_text(text, reply_markup=kb)
    await call.answer()

@dp.callback_query(F.data == "game_car_parking")
async def cb_game_car_parking(call: CallbackQuery, state: FSMContext):
    await state.update_data(cp_ordered=0)
    text = "🅿️ *Car Parking — Аккаунты*\n\n👑 РАНГ: *KING*\n🔥 ПРОКАЧАННЫЙ АККАУНТ — ВСЁ ДЛЯ КОМФОРТА!\n\n🚗 Автомобили: от 14 до 20 шт. 🏎️\n👕 Одежда: открыта вся 👗\n💰 Игровая валюта: 50 000 000 💵\n🪙 Коины: 300 🟡\n🔓 Открыто всё, кроме гаража 🚫\n✅ Без Trade Ban — чисто! 🛡️\n\n📦 *В наличии: 31 шт.*\n\n💥 *ЦЕНА:*\n🛒 До 3 шт: *50 ₽* за шт.\n🛒 С 4-й шт: *25 ₽* за шт. (-50% 🔥)\n\n👇 Выберите количество или введите своё число:"
    kb_rows = [
        [InlineKeyboardButton(text="Купить 1 шт — 50 ₽", callback_data="buy_cp|1")],
        [InlineKeyboardButton(text="Купить 2 шт — 100 ₽", callback_data="buy_cp|2")],
        [InlineKeyboardButton(text="Купить 3 шт — 150 ₽", callback_data="buy_cp|3")],
        [InlineKeyboardButton(text="Купить 5 шт — 200 ₽", callback_data="buy_cp|5")],
        [InlineKeyboardButton(text="Купить 10 шт — 325 ₽", callback_data="buy_cp|10")],
        [InlineKeyboardButton(text="⌨️ Ввести своё количество", callback_data="cp_custom")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="game_menu")],
    ]
    await call.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows))
    await call.answer()

@dp.callback_query(F.data == "cp_custom")
async def cb_cp_custom(call: CallbackQuery, state: FSMContext):
    await state.set_state(OrderStates.waiting_cp_amount)
    await call.message.edit_text("⌨️ *Введите количество аккаунтов*\n\nНапример: `4`\n💡 Помните: с 4-й штуки цена снижается до 25 ₽!", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="game_car_parking")]
    ]))
    await call.answer()

@dp.message(OrderStates.waiting_cp_amount)
async def process_cp_amount(message: Message, state: FSMContext):
    if not message.text or not message.text.strip().isdigit():
        await message.answer("⚠️ Введите число"); return
    qty = int(message.text.strip())
    if qty < 1:
        await message.answer("⚠️ Минимум 1"); return
    if qty > 31:
        await message.answer("⚠️ В наличии только 31 аккаунт!"); return
    await state.set_state(None)
    if qty <= 3: total = qty * 50
    else: total = (3 * 50) + ((qty - 3) * 25)
    balance = db_get_balance(message.from_user.id)
    text = f"📋 *Проверьте заказ:*\n\n🅿️ Car Parking (KING) — *{qty} шт.*\n💰 К оплате: *{total} ₽*\n\n💰 Ваш баланс: *{balance:.2f} ₽*\n\n⚠️ *Внимание:* После оплаты администратор вручную отправит данные от аккаунта.\n⏳ *Ожидайте, выдача занимает от 2 до 15 минут!* 🚀"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Оплатить товар", callback_data=f"confirm_cp|{qty}|{total}")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="game_car_parking")]
    ])
    await message.answer(text, reply_markup=kb)

@dp.callback_query(F.data.startswith("buy_cp|"))
async def cb_buy_cp_btn(call: CallbackQuery, state: FSMContext):
    qty = int(call.data.split("|")[1])
    if qty <= 3: total = qty * 50
    else: total = (3 * 50) + ((qty - 3) * 25)
    balance = db_get_balance(call.from_user.id)
    text = f"📋 *Проверьте заказ:*\n\n🅿️ Car Parking (KING) — *{qty} шт.*\n💰 К оплате: *{total} ₽*\n\n💰 Ваш баланс: *{balance:.2f} ₽*\n\n⚠️ *Внимание:* После оплаты администратор вручную отправит данные от аккаунта.\n⏳ *Ожидайте, выдача занимает от 2 до 15 минут!* 🚀"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Оплатить товар", callback_data=f"confirm_cp|{qty}|{total}")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="game_car_parking")]
    ])
    await call.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows))
    await call.answer()
    

@dp.callback_query(F.data.startswith("confirm_cp|"))
async def cb_confirm_cp(call: CallbackQuery):
    _, qty_str, total_str = call.data.split("|")
    qty = int(qty_str)
    total = float(total_str)
    balance = db_get_balance(call.from_user.id)
    if balance < total:
        await call.answer("❌ Недостаточно средств", show_alert=True); return
    if not db_charge_balance(call.from_user.id, total):
        await call.answer("⚠️ Ошибка списания", show_alert=True); return
    
    display_name = f"Car Parking KING ({qty} шт.)"
    order_id = db_add_order(call.from_user.id, "games", display_name, "car_parking", qty, total, "manual", "panel_1")
    db_update_order_status(order_id, "in_progress")
    
    try:
        await bot.send_message(ADMIN_ID, f"🅿️ *Новый заказ (Car Parking)!*\n\n👤 Юзер: @{call.from_user.username or call.from_user.id} (ID: `{call.from_user.id}`)\n📦 Товар: {display_name}\n💸 Сумма: {total} ₽\n\n⚠️ Выдайте аккаунты.")
    except Exception: pass
    
    text = f"✅ *Оплата прошла успешно!*\n\n📦 Товар: *{display_name}*\n💸 Списано: *{total} ₽*\n💰 Остаток: *{db_get_balance(call.from_user.id):.2f} ₽*\n\n⏳ *Ожидайте:* оператор свяжется и выдаст данные от аккаунтов.\n\nЗаказ №{order_id}"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Написать оператору", url=f"https://t.me/{SUPPORT_USERNAME}")],
        [InlineKeyboardButton(text="🆕 В игры", callback_data="game_menu")]
    ])
    await call.message.edit_text(text, reply_markup=kb)
    await call.answer("✅ Оплачено")

@dp.callback_query(F.data.startswith("buy_game|"))
async def cb_buy_game(call: CallbackQuery):
    _, item_name, price_str = call.data.split("|")
    price = float(price_str)
    balance = db_get_balance(call.from_user.id)
    text = f"📋 *Подтверждение заказа:*\n\n📦 Товар: *{item_name}*\n💸 К оплате: *{price} ₽*\n\n💰 Ваш баланс: *{balance:.2f} ₽*"
    if balance < price:
        text += "\n\n❌ *Недостаточно средств!*"
    kb_rows = []
    if balance >= price:
        kb_rows.append([InlineKeyboardButton(text="✅ Оплатить товар", callback_data=f"confirm_game|{item_name}|{price}")])
    kb_rows.append([InlineKeyboardButton(text="🔙 Назад", callback_data="game_menu")])
    try:
        await call.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows))
    except Exception:
        await call.message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows))
    await call.answer()

@dp.callback_query(F.data.startswith("confirm_game|"))
async def cb_confirm_game(call: CallbackQuery):
    _, item_name, price_str = call.data.split("|")
    price = float(price_str)
    balance = db_get_balance(call.from_user.id)
    if balance < price:
        await call.answer("❌ Недостаточно средств", show_alert=True); return
    if not db_charge_balance(call.from_user.id, price):
        await call.answer("⚠️ Ошибка списания", show_alert=True); return
    
    order_id = db_add_order(call.from_user.id, "games", item_name, "game_service", 1, price, "manual", "panel_1")
    db_update_order_status(order_id, "in_progress")
    
    try:
        await bot.send_message(ADMIN_ID, f"🎮 *Новый заказ игры!*\n\n👤 Юзер: @{call.from_user.username or call.from_user.id} (`{call.from_user.id}`)\n📦 Товар: {item_name}\n💸 Сумма: {price} ₽\n\n⚠️ Свяжитесь с юзером для получения данных.")
    except Exception: pass
    
    await finish_game_order(call, item_name, price, order_id)

@dp.callback_query(F.data.startswith("confirm_custom_game|"))
async def cb_confirm_custom_game(call: CallbackQuery):
    _, item_name, qty, price_str = call.data.split("|")
    price = float(price_str)
    qty = int(qty)
    balance = db_get_balance(call.from_user.id)
    if balance < price:
        await call.answer("❌ Недостаточно средств", show_alert=True); return
    if not db_charge_balance(call.from_user.id, price):
        await call.answer("⚠️ Ошибка списания", show_alert=True); return
    
    display_name = f"{item_name} ({qty} шт.)"
    order_id = db_add_order(call.from_user.id, "games", display_name, "game_custom", qty, price, "manual", "panel_1")
    db_update_order_status(order_id, "in_progress")
    
    try:
        await bot.send_message(ADMIN_ID, f"🎮 *Новый заказ игры (своё кол-во)!*\n\n👤 Юзер: @{call.from_user.username or call.from_user.id} (`{call.from_user.id}`)\n📦 Товар: {display_name}\n💸 Сумма: {price} ₽\n\n⚠️ Свяжитесь с юзером.")
    except Exception: pass
    
    await finish_game_order(call, display_name, price, order_id)

async def finish_game_order(call: CallbackQuery, item_name: str, price: float, order_id: int):
    text = f"✅ *Оплата прошла успешно!*\n\n📦 Товар: *{item_name}*\n💸 Списано: *{price} ₽*\n💰 Остаток: *{db_get_balance(call.from_user.id):.2f} ₽*\n\n⚠️ *Что делать дальше?*\nНажмите кнопку ниже и напишите оператору данные вашего аккаунта (ID, Логин/Пароль, Сервер), чтобы мы выдали заказ.\n\nЗаказ №{order_id}"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Отправить данные", url=f"https://t.me/{SUPPORT_USERNAME}")],
        [InlineKeyboardButton(text="🆕 В игры", callback_data="game_menu")]
    ])
    await call.message.edit_text(text, reply_markup=kb)
    try:
        await call.answer("✅ Оплачено")
    except Exception: pass

# ============ ФОНОВЫЕ ЗАДАЧИ ============
async def check_panel_statuses_loop():
    STATUS_TEXT = {
        "pending": ("⏳", "Ожидает"), "in_progress": ("🚀", "В работе"),
        "partial": ("⚠️", "Частично"), "completed": ("✅", "Выполнен!"),
        "canceled": ("❌", "Отменён"), "error": ("⚠️", "Ошибка"),
    }
    while True:
        try:
            orders = db_get_orders_with_panel()
            for order in orders:
                (order_id, user_id, panel_order_id, sname, qty, link, old_status, platform, panel_name) = order
                new_status, start_count, remains = await panel_check_status(panel_name, panel_order_id)
                if not new_status or new_status == old_status: continue
                db_update_panel_status(order_id, new_status)
                emoji, title = STATUS_TEXT.get(new_status, ("ℹ️", new_status))
                progress = ""
                if new_status == "partial" and remains is not None:
                    try:
                        done = max(0, qty - int(remains or 0))
                        progress = f"\n📊 {progress_bar(done, qty)}  {done}/{qty}"
                    except (ValueError, TypeError): pass
                text = (f"{emoji} *Заказ #{order_id}*\n\n📱 {platform.capitalize()}\n📦 {sname}\n🔢 *{qty}*{progress}\n🔗 [Ссылка]({link})\n\n📌 *{title}*")
                kb = None
                if new_status in ("completed", "canceled", "error"):
                    kb = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="⭐ Отзыв", callback_data=f"review_{order_id}")],
                        [InlineKeyboardButton(text="⚡ Повторить", callback_data=f"repeat_{order_id}")]
                    ])
                try:
                    await bot.send_message(user_id, text, reply_markup=kb, disable_web_page_preview=True)
                except Exception: pass
                await asyncio.sleep(0.5)
        except Exception as e:
            print(f"Ошибка проверки: {e}")
        await asyncio.sleep(PANEL_CHECK_INTERVAL)


async def check_payments_loop():
    while True:
        try:
            invoices = await crypto.get_invoices(count=100)
            if not isinstance(invoices, list): invoices = [invoices]
            for inv in invoices:
                if inv.status != "paid": continue
                try: user_id = int(inv.payload)
                except (ValueError, TypeError): continue
                if not db_save_payment(user_id, inv.invoice_id, inv.amount, inv.amount * USDT_TO_RUB): continue
                rub_credit = round(inv.amount * USDT_TO_RUB, 2)
                db_user_add(user_id, "", "")
                db_add_balance(user_id, rub_credit)
                try:
                    await bot.send_message(user_id, f"✅ *Баланс пополнен!*\n\n💰 Зачислено: *{rub_credit} ₽*", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="🚀 Открыть Mini App", web_app=WebAppInfo(url=f"{WEBAPP_URL}#balance_{db_get_balance(user_id):.2f}"))]
                    ]))
                except Exception: pass
                await log_to_channel(f"💳 Пополнение: {user_id} — {rub_credit} ₽")
        except Exception as e:
            print(f"Ошибка проверки платежей: {e}")
        await asyncio.sleep(30)


async def process_privat_orders_loop():
    NOTIFY_THRESHOLDS = [25, 50, 75, 100]
    while True:
        try:
            conn = db_connect(); cur = conn.cursor()
            cur.execute("""
                SELECT id, order_id, panel, service_id, link, quantity, step_qty,
                       days, interval_minutes, last_sent_at, last_notified_percent, total_qty
                FROM privat_orders WHERE status='active'
            """)
            rows = cur.fetchall(); conn.close()

            now = datetime.now()
            for row in rows:
                (p_id, order_id, panel, service_id, link, qty_left, step,
                 days, interval_minutes, last_sent, last_notified, total_qty) = row

                # --- ЗАВЕРШЕНИЕ ---
                if qty_left <= 0:
                    conn = db_connect(); cur = conn.cursor()
                    cur.execute("UPDATE privat_orders SET status='done' WHERE id=?", (p_id,))
                    cur.execute("UPDATE orders SET status='completed' WHERE id=?", (order_id,))
                    conn.commit(); conn.close()
                    try:
                        user_row = db_get_order_admin(order_id)
                        if user_row:
                            await bot.send_message(user_row[1],
                                f"✅ *Плавный заказ #{order_id} полностью выполнен!*\n\n"
                                f"📦 {user_row[3]}\n🔢 *{total_qty or qty_left} шт.*\n📆 {days} дней\n\n"
                                f"💬 @{SUPPORT_USERNAME}", parse_mode="Markdown")
                    except Exception: pass
                    continue

                # --- ПРОВЕРКА ИНТЕРВАЛА ---
                if last_sent:
                    try: last_dt = datetime.strptime(last_sent, "%Y-%m-%d %H:%M:%S")
                    except Exception: last_dt = now - timedelta(hours=24)
                else:
                    last_dt = now - timedelta(hours=24)

                minutes_passed = (now - last_dt).total_seconds() / 60
                if minutes_passed < (interval_minutes or 60):
                    continue

                # --- ОТПРАВКА ПАРТИИ ---
                send_qty = min(step, qty_left)
                if send_qty > 5000: send_qty = 5000

                panel_order_id, err = await panel_add_order(panel, service_id, link, send_qty)

                if panel_order_id:
                    qty_left -= send_qty
                    conn = db_connect(); cur = conn.cursor()
                    cur.execute("UPDATE privat_orders SET quantity=?, last_sent_at=? WHERE id=?",
                                (qty_left, now.strftime("%Y-%m-%d %H:%M:%S"), p_id))
                    conn.commit(); conn.close()

                    await log_to_channel(f"🐢 Партия #{order_id}: {send_qty} шт. | осталось {qty_left}")

                    # --- УВЕДОМЛЕНИЕ О ПРОГРЕССЕ ---
                    try:
                        sent_total = (total_qty or 0) - qty_left
                        percent = int((sent_total / total_qty) * 100) if total_qty else 0
                        crossed = None
                        for th in NOTIFY_THRESHOLDS:
                            if percent >= th and (last_notified or 0) < th:
                                crossed = th; break
                        
                        if crossed is not None:
                            user_row = db_get_order_admin(order_id)
                            if user_row:
                                uid = user_row[1]
                                filled = int(10 * percent / 100)
                                bar = "█" * filled + "░" * (10 - filled)
                                
                                if crossed == 100:
                                    msg = f"🎉 *Заказ #{order_id} — 100%!*\n\n📦 {user_row[3]}\n📊 `{bar}` *{percent}%*\n\n✅ Полностью выполнен! 🙏"
                                else:
                                    msg = f"📊 *Прогресс #{order_id}*\n\n📦 {user_row[3]}\n📊 `{bar}` *{percent}%* ({sent_total}/{total_qty})\n\n⏳ Продолжаем 👌"
                                
                                await bot.send_message(uid, msg, parse_mode="Markdown")
                                
                                conn = db_connect(); cur = conn.cursor()
                                cur.execute("UPDATE privat_orders SET last_notified_percent=? WHERE id=?", (crossed, p_id))
                                conn.commit(); conn.close()
                    except Exception as e:
                        print(f"Ошибка уведомления о прогрессе: {e}")
                else:
                    await notify_admin_error(err, f"Партия #{order_id} ({send_qty} шт)")
                    conn = db_connect(); cur = conn.cursor()
                    cur.execute("UPDATE privat_orders SET last_sent_at=? WHERE id=?",
                                ((now + timedelta(minutes=interval_minutes or 60)).strftime("%Y-%m-%d %H:%M:%S"), p_id))
                    conn.commit(); conn.close()

        except Exception as e:
            print(f"Ошибка приват-цикла: {e}")
        await asyncio.sleep(300)  # проверяем каждые 5 минут
        
# ============ АДМИН-ПАНЕЛЬ ============
def admin_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔥 Управление Акциями", callback_data="adm_promo_custom")],
        [InlineKeyboardButton(text="💰 Цены услуг", callback_data="adm_prices")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="adm_stats")],
        [InlineKeyboardButton(text="📈 За сегодня", callback_data="adm_today_stats")],
        [InlineKeyboardButton(text="📦 Заказы за сегодня", callback_data="adm_orders_today")],
        [InlineKeyboardButton(text="👥 Пользователи", callback_data="adm_users")],
        [InlineKeyboardButton(text="📦 Все заказы", callback_data="adm_orders")],
        [InlineKeyboardButton(text="🎟 Промокоды", callback_data="adm_promos")],
        [InlineKeyboardButton(text="📨 Тикеты", callback_data="adm_tickets")],
        [InlineKeyboardButton(text="⭐ Отзывы", callback_data="adm_reviews")],
        [InlineKeyboardButton(text="🗑 Удалить отзыв", callback_data="adm_review_del")],
        [InlineKeyboardButton(text="🔍 Найти заказ", callback_data="adm_find_order")],
        [InlineKeyboardButton(text="🔍 Найти юзера", callback_data="adm_find_user")],
        [InlineKeyboardButton(text="✏️ Изменить цену", callback_data="adm_edit_price")],
        [InlineKeyboardButton(text="💾 Бэкап", callback_data="adm_backup")],
        [InlineKeyboardButton(text="📤 Экспорт CSV", callback_data="adm_csv")],
        [InlineKeyboardButton(text="✏️ Статус заказа", callback_data="adm_set_status")],
        [InlineKeyboardButton(text="💰 Изменить баланс", callback_data="adm_balance")],
        [InlineKeyboardButton(text="📢 Рассылка", callback_data="adm_broadcast")]
    ])

@dp.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    await state.clear()
    await message.answer("🛡 *Админ-панель*\n\nВыберите действие:", reply_markup=admin_menu_kb())
    
@dp.callback_query(F.data == "adm_stats")
async def cb_adm_stats(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID: return await call.answer("Нет доступа", show_alert=True)
    users, orders, total, today, today_sum = db_stats()
    rc, ravg = db_reviews_avg()
    await call.message.answer(f"📊 *Статистика*\n\n👥 Юзеров: *{users}*\n📦 Заказов: *{orders}*\n💰 Оборот: *{total:.2f} ₽*\n\n📅 *Сегодня:*\n📦 {today} | 💰 {today_sum:.2f} ₽\n\n⭐ Рейтинг: *{ravg}/5* ({rc})", parse_mode="Markdown")
    await call.answer()

@dp.callback_query(F.data == "adm_today_stats")
async def cb_adm_today_stats(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID: return await call.answer("Нет доступа", show_alert=True)
    top, top_users = db_top_today()
    users, orders, total, today, today_sum = db_stats()
    text = f"📈 *Сводка за сегодня*\n\n📦 Заказов: *{today}*\n💰 Выручка: *{today_sum:.2f} ₽*\n\n"
    if top:
        text += "🔥 *Топ-3 услуги:*\n"
        for sname, cnt, ssum in top: text += f"• {sname} — {cnt} шт, {ssum:.2f} ₽\n"
    await call.message.answer(text, parse_mode="Markdown")
    await call.answer()

@dp.callback_query(F.data == "adm_orders_today")
async def cb_adm_orders_today(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID: return await call.answer("Нет доступа", show_alert=True)
    rows = db_orders_today()
    if not rows: return await call.message.answer("📭 Заказов сегодня нет.")
    text = f"📦 *Заказы за сегодня* ({len(rows)})\n\n"
    for o in rows[:30]:
        oid, uid, plat, sname, qty, price, status, link, created = o
        text += f"#{oid} | `{uid}` | {plat} | {qty} | {(price or 0):.0f}₽ | `{status}`\n"
    await call.message.answer(text, parse_mode=None)
    await call.answer()

@dp.callback_query(F.data == "adm_orders")
async def cb_adm_orders(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID: return await call.answer("Нет доступа", show_alert=True)
    orders = db_all_orders(20)
    text = "📦 *Все заказы (20):*\n\n"
    for o in orders:
        oid, uid, plat, sname, qty, price, status, link, created = o
        text += f"#{oid} | `{uid}` | {plat} | {qty} | {(price or 0):.0f}₽ | `{status}`\n"
    await call.message.answer(text, parse_mode=None)
    await call.answer()

@dp.callback_query(F.data == "adm_users")
async def cb_adm_users(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID: return await call.answer("Нет доступа", show_alert=True)
    users = db_get_users()
    text = "👥 *Пользователи (последние 30):*\n\n"
    for u in users[-30:]: text += f"• `{u[0]}` | @{u[1] or '-'} | {(u[3] or 0):.2f}₽\n"
    await call.message.answer(text, parse_mode=None)
    await call.answer()
    

@dp.callback_query(F.data == "adm_tickets")
async def cb_adm_tickets(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID: return await call.answer("Нет доступа", show_alert=True)
    tickets = db_open_tickets()
    if not tickets: return await call.message.answer("Нет открытых тикетов")
    text = "📨 *Открытые тикеты:*\n\n"
    for t in tickets: text += f"#{t[0]} | `{t[1]}` | @{t[2] or '-'}\n💬 {t[3]}\n\n"
    await call.message.answer(text, parse_mode=None)
    await call.answer()

@dp.callback_query(F.data == "adm_reviews")
async def cb_adm_reviews(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID: return await call.answer("Нет доступа", show_alert=True)
    count, avg = db_reviews_avg()
    reviews = db_reviews_list(50)
    if not reviews: return await call.message.answer("📭 Отзывов пока нет.")
    text = f"⭐ *Отзывы*\n\n📊 Средний: {avg}/5\n💬 Всего: {count}\n\n"
    for rid, uid, rating, comment, created in reviews: text += f"🆔 `{rid}` | {'⭐' * rating} | `{uid}`\n{comment or '(без комментария)'}\n{created}\n\n"
    await call.message.answer(text, parse_mode=None)
    await call.answer()
    
@dp.callback_query(F.data == "adm_backup")
async def cb_adm_backup(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID: return await call.answer("Нет доступа", show_alert=True)
    try:
        with open(DB_PATH, "rb") as f: data = f.read()
        doc = BufferedInputFile(data, filename=f"backup_{datetime.now():%Y%m%d_%H%M}.db")
        await call.message.answer_document(doc, caption="💾 Бэкап базы")
    except Exception as e: await call.message.answer(f"❌ {e}")
    await call.answer()

@dp.callback_query(F.data == "adm_csv")
async def cb_adm_csv(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID: return await call.answer("Нет доступа", show_alert=True)
    try:
        conn = db_connect(); cur = conn.cursor()
        cur.execute("SELECT * FROM orders")
        rows = cur.fetchall(); conn.close()
        output = io.StringIO(); writer = csv.writer(output)
        writer.writerow(["id", "user_id", "platform", "service_name", "service_id", "quantity", "price", "link", "status", "created_at", "panel", "panel_order_id", "panel_status"])
        for r in rows: writer.writerow(r)
        data = output.getvalue().encode("utf-8")
        doc = BufferedInputFile(data, filename=f"orders_{datetime.now():%Y%m%d}.csv")
        await call.message.answer_document(doc, caption="📤 Экспорт заказов")
    except Exception as e: await call.message.answer(f"❌ {e}")
    await call.answer()

@dp.callback_query(F.data == "adm_prices")
async def cb_adm_prices(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID: 
        return await call.answer("Нет доступа", show_alert=True)
    
    text = "💰 *ЦЕНЫ УСЛУГ*\n\n"
    for plat, pdata in SERVICES.items():
        text += f"*{pdata.get('title', plat.upper())}*\n"
        
        # Безопасно получаем список услуг
        items_dict = pdata.get('items', pdata)
        
        for key, item in items_dict.items():
            if key in ("tg_report_menu", "title", "items"): 
                continue
            
            # Эти строки с отступом (внутри цикла)
            text += f"• {item['name'][:40]}\n"
            text += f"`{key}` | ID `{item['id']}` | {item['price']}₽/{item['pack']}\n"
            
        text += "\n" # Эта строка без отступа, она разделяет платформы
        
    if len(text) > 4000:
        for chunk in [text[i:i+4000] for i in range(0, len(text), 4000)]: 
            await call.message.answer(chunk, parse_mode=None)
    else: 
        await call.message.answer(text, parse_mode=None)
        
    await call.answer()

@dp.callback_query(F.data == "adm_find_order")
async def cb_adm_find_order(call: CallbackQuery, state: FSMContext):
    if call.from_user.id != ADMIN_ID: return await call.answer("Нет доступа", show_alert=True)
    await state.set_state(AdminStates.waiting_order_find)
    await call.message.answer("🔍 *Поиск заказа*\n\nВведите ID заказа или панельный ID")
    await call.answer()

@dp.message(AdminStates.waiting_order_find)
async def adm_process_find_order(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: await state.clear(); return
    try:
        oid = int((message.text or "").strip().lstrip("#"))
        row = db_get_order_admin(oid)
        if not row: await message.answer("❌ Заказ не найден"); await state.clear(); return
        (id_, uid, plat, sname, sid, qty, price, link, status, created, panel, panel_id, panel_status) = row
        await message.answer(
            f"📦 *Заказ #{id_}*\n\n👤 `{uid}`\n📱 {plat}\n📦 {sname}\n"
            f"🆔 Услуги: `{sid}`\n🔢 {qty} | 💸 {(price or 0):.2f} ₽\n"
            f"🔗 {link}\n📌 `{status}` | 🕒 {created}\n"
            f"🖥 Панель: *{panel}*\n✅ ID в панели: `#{panel_id}` | `{panel_status}`", parse_mode="Markdown"
        )
    except Exception: await message.answer("⚠️ Введите числовой ID")
    await state.clear()

@dp.callback_query(F.data == "adm_find_user")
async def cb_adm_find_user(call: CallbackQuery, state: FSMContext):
    if call.from_user.id != ADMIN_ID: return await call.answer("Нет доступа", show_alert=True)
    await state.set_state(AdminStates.waiting_user_find)
    await call.message.answer("🔍 *Поиск юзера*\n\nВведите @username или ID")
    await call.answer()

@dp.message(AdminStates.waiting_user_find)
async def adm_process_find_user(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: await state.clear(); return
    txt = (message.text or "").strip()
    if txt.isdigit() and len(txt) >= 6:
        user = db_get_user(int(txt))
    elif txt.startswith("@") or not txt.isdigit():
        user = db_find_user_by_username(txt)
    else:
        user = None
        
    if not user:
        await message.answer("❌ Юзер не найден")
    else:
        cnt, total = db_user_orders_count(user[0])
        await message.answer(
            f"👤 *Юзер найден*\n\n🆔 `{user[0]}`\n👤 @{user[1] or '-'} | {user[2] or '-'}\n"
            f"💰 Баланс: *{(user[3] or 0):.2f} ₽*\n💸 Потрачено: *{(user[6] or 0):.2f} ₽*\n"
            f"📦 Заказов: *{cnt}* на *{total:.2f} ₽*", parse_mode="Markdown"
        )
    await state.clear()
    

@dp.callback_query(F.data == "adm_set_status")
async def cb_adm_set_status(call: CallbackQuery, state: FSMContext):
    if call.from_user.id != ADMIN_ID: return await call.answer("Нет доступа", show_alert=True)
    await state.set_state(AdminStates.waiting_status)
    await call.message.answer("Формат: `<order_id> <статус>`\nНапример: `5 completed`", parse_mode="Markdown")
    await call.answer()

@dp.message(AdminStates.waiting_status)
async def adm_process_status(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    try:
        oid_str, status = (message.text or "").strip().split(maxsplit=1)
        db_update_order_status(int(oid_str), status.strip())
        await message.answer(f"✅ Заказ `{oid_str}` → `{status}`", parse_mode="Markdown")
    except Exception: await message.answer("⚠️ Формат: `5 completed`")
    await state.clear()

@dp.callback_query(F.data == "adm_balance")
async def cb_adm_balance(call: CallbackQuery, state: FSMContext):
    if call.from_user.id != ADMIN_ID: return await call.answer("Нет доступа", show_alert=True)
    await state.set_state(AdminStates.waiting_balance)
    await call.message.answer("Формат: `<user_id> <сумма>`\nНапример: `123456789 500`")
    await call.answer()

@dp.message(AdminStates.waiting_balance)
async def adm_process_balance(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    try:
        uid_str, amount_str = (message.text or "").strip().split()
        db_set_balance(int(uid_str), float(amount_str))
        await message.answer(f"✅ Баланс `{uid_str}` = {amount_str} ₽", parse_mode="Markdown")
    except Exception: await message.answer("⚠️ Формат: `123456789 500`")
    await state.clear()

@dp.callback_query(F.data == "adm_broadcast")
async def cb_adm_broadcast(call: CallbackQuery, state: FSMContext):
    if call.from_user.id != ADMIN_ID: return await call.answer("Нет доступа", show_alert=True)
    await state.set_state(AdminStates.waiting_broadcast)
    await call.message.answer("📢 Отправьте текст для рассылки:")
    await call.answer()

@dp.message(AdminStates.waiting_broadcast)
async def adm_process_broadcast(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    text = message.text
    conn = db_connect(); cur = conn.cursor()
    cur.execute("SELECT user_id FROM users")
    users = [r[0] for r in cur.fetchall()]
    conn.close()
    ok, fail = 0, 0
    await message.answer(f"📢 Начинаю рассылку на {len(users)} юзеров...")
    for uid in users:
        try:
            await bot.send_message(uid, text)
            ok += 1
            await asyncio.sleep(0.05)
        except Exception: fail += 1
    await message.answer(f"✅ Отправлено: {ok}\n❌ Ошибок: {fail}")
    await state.clear()

@dp.callback_query(F.data == "adm_review_del")
async def cb_adm_review_del(call: CallbackQuery, state: FSMContext):
    if call.from_user.id != ADMIN_ID: return await call.answer("Нет доступа", show_alert=True)
    await state.set_state(AdminStates.waiting_review_delete)
    await call.message.answer("🗑 *Удаление отзыва*\n\nВведите ID отзыва.")
    await call.answer()

@dp.message(AdminStates.waiting_review_delete)
async def adm_process_review_delete(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    try:
        rid = int((message.text or "").strip())
        db_review_delete(rid)
        await message.answer(f"✅ Отзыв `#{rid}` удалён", parse_mode="Markdown")
    except (ValueError, AttributeError):
        await message.answer("⚠️ Введите ID числом")
    await state.clear()

@dp.message(Command("delreview"))
async def cmd_delreview(message: Message):
    if message.from_user.id != ADMIN_ID: return
    try:
        _, rid = message.text.split()
        db_review_delete(int(rid))
        await message.answer(f"✅ Отзыв `#{rid}` удалён", parse_mode="Markdown")
    except Exception:
        await message.answer("Формат: `/delreview 5`")

@dp.callback_query(F.data == "adm_edit_price")
async def cb_adm_edit_price(call: CallbackQuery, state: FSMContext):
    if call.from_user.id != ADMIN_ID: return await call.answer("Нет доступа", show_alert=True)
    await state.set_state(AdminStates.waiting_edit_price)
    await call.message.answer("Формат: `<platform> <service_key> <новая_цена>`\nНапример: `telegram tg_views 7`")
    await call.answer()

@dp.message(AdminStates.waiting_edit_price)
async def adm_process_edit_price(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    try:
        parts = message.text.split()
        if len(parts) != 3: raise ValueError
        plat, key, new_price = parts[0], parts[1], float(parts[2])
        if plat not in SERVICES or key not in SERVICES[plat]["items"]: raise KeyError
        old = SERVICES[plat]["items"][key]["price"]
        SERVICES[plat]["items"][key]["price"] = new_price
        await message.answer(f"✅ Цена изменена\n\n📦 {SERVICES[plat]['items'][key]['name']}\n💰 Старая: {old} ₽ → Новая: {new_price} ₽")
        await log_to_channel(f"✏️ Изменена цена {plat}.{key}: {old} → {new_price}")
    except Exception:
        await message.answer("⚠️ Формат: `telegram tg_views 7`")
    await state.clear()
    
# --- УПРАВЛЕНИЕ АКЦИЯМИ ---
@dp.callback_query(F.data == "adm_promo_custom")
async def cb_adm_promo_custom(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID: return await call.answer("Нет доступа", show_alert=True)
    promos = db_get_active_promos()
    text = "🔥 *Активные акции:*\n\n"
    if not promos: text += "Нет активных акций.\n"
    for p in promos: text += f"• {p[1]} (Скидка {p[4]}%) — до {p[5]}\n"
    text += "\nДобавить: `/addpromo Название platform key скидка часы`"
    await call.message.answer(text, parse_mode=None)
    await call.answer()

@dp.message(Command("addpromo"))
async def cmd_addpromo(message: Message):
    if message.from_user.id != ADMIN_ID: 
        return await message.answer("У вас нет прав.")
    try:
        _, title, plat, key, disc, hours = message.text.split()
        disc_val = int(disc)
        hours_val = int(hours)
        
        db_add_custom_promo(title, plat, key, disc_val, hours_val)
        
        base_url = WEBAPP_URL.split('?')[0] 
        promo_link = f"{base_url}?promo_key={key}&promo_disc={disc_val}&promo_hours={hours_val}"
        
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔥 Открыть Mini App со скидкой", url=promo_link)]
        ])
        
        await message.answer(
            f"✅ *Акция '{title}' создана!*\n\n"
            f"📦 Услуга: `{key}`\n"
            f"🔥 Скидка: *{disc_val}%*\n"
            f"⏳ Длительность: *{hours_val} часов*\n\n"
            f"👇 Нажми кнопку, чтобы проверить:",
            reply_markup=markup,
            parse_mode="Markdown"
        )
    except ValueError:
        await message.answer("⚠️ *Неверный формат!*\n\nПравильно:\n`/addpromo Название платформа ключ скидка часы`\n\nПример:\n`/addpromo Просмотры_IG instagram ig_views 94 48`", parse_mode="Markdown")
    except Exception as e:
        await message.answer(f"⚠️ Ошибка: {e}")

# ============ КНОПКИ РУЛЕТКИ ============
@dp.callback_query(F.data.startswith("confirm_wheel|"))
async def confirm_wheel_buy(call: CallbackQuery):
    try:
        _, wheel, price_str = call.data.split("|")
        price = float(price_str)
        user_id = call.from_user.id
        balance = db_get_balance(user_id)
        if balance < price:
            await call.message.edit_text(f"❌ *Недостаточно средств!*\n\nНужно: *{price:.2f} ₽*", parse_mode="Markdown")
            await call.answer(); return
        if not db_charge_balance(user_id, price):
            await call.message.edit_text("⚠️ Ошибка списания."); await call.answer(); return
        ticket_url = f"{WEBAPP_URL}&wheel_ticket={wheel}"
        builder = InlineKeyboardBuilder()
        builder.button(text="🎰 Крутить!", web_app=WebAppInfo(url=ticket_url))
        await call.message.edit_text(f"✅ *Попытка куплена!*\n\n💰 Списано: *{price:.2f} ₽*\n\n👇 Нажмите кнопку ниже:", reply_markup=builder.as_markup(), parse_mode="Markdown")
        await call.answer("Успешно!")
    except Exception as e:
        await call.answer(f"Ошибка: {e}", show_alert=True)

@dp.callback_query(F.data == "cancel_wheel")
async def cancel_wheel_buy(call: CallbackQuery):
    await call.message.edit_text("❌ Покупка отменена.")
    await call.answer()

# ============ РЕГИСТРАЦИЯ MIDDLEWARE И ЗАПУСК ============
dp.message.middleware(FloodMessageMiddleware())
dp.callback_query.middleware(FloodCallbackMiddleware())

# ============ ДИНАМИЧЕСКИЙ КАТАЛОГ VEXBOOST ============
class VexForm(StatesGroup):
    calc_quantity = State()

def get_vex_rate(s: dict) -> float:
    try:
        raw_rate = float(s.get("rate", 0))
        return round(raw_rate * (1 + VEX_MARGIN / 100), 2)
    except:
        return 0.0

async def fetch_vex_services():
    global VEX_CACHE
    payload = {"key": VEX_API_KEY, "action": "services"}
    try:
        async with aiohttp.ClientSession() as s:
            async with s.post(VEX_PROVIDER_URL, data=payload, timeout=15) as r:
                data = await r.json(content_type=None)
                if isinstance(data, list):
                    VEX_CACHE = data
                    return data
    except Exception as e:
        print(f"Ошибка VEX API: {e}")
    return []

@dp.message(F.text == "⚡ Услуги из VexBoost")
async def msg_vex_menu(message: Message):
    if not VEX_CACHE:
        msg = await message.answer("⏳ Загружаю услуги из VexBoost...")
        await fetch_vex_services()
        await msg.delete()
        
    if not VEX_CACHE:
        await message.answer("❌ Ошибка связи с API VexBoost")
        return
        
    text = (
        "✨ <b>КАТАЛОГ VEXBOOST</b>\n"
        "╭────────────────────────\n"
        "│ 🎯 Выберите соцсеть:\n"
        "╰────────────────────────"
    )
    # Формируем кнопки площадок
    platforms = {}
    for s in VEX_CACHE:
        cat = str(s.get("category", "")).lower()
        plat = "other"
        if "tiktok" in cat: plat = "tiktok"
        elif "telegram" in cat or "tg" in cat: plat = "tg"
        elif "instagram" in cat: plat = "ig"
        elif "youtube" in cat or "yt" in cat: plat = "yt"
        elif "vk" in cat: plat = "vk"
        
        if plat not in platforms: platforms[plat] = 0
        platforms[plat] += 1
        
    plat_names = {"tiktok": "🎵 TikTok", "tg": "✈️ Telegram", "ig": "📸 Instagram", "yt": "▶️ YouTube", "vk": "🅱️ ВКонтакте", "other": "📦 Другое"}
    kb_rows = []
    for p_key, count in platforms.items():
        kb_rows.append([InlineKeyboardButton(text=f"{plat_names[p_key]} ({count})", callback_data=f"vex_plat:{p_key}:0")])
    
    kb_rows.append([InlineKeyboardButton(text="🔙 В меню", callback_data="main_menu_back")])
    await message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows), parse_mode="HTML")

@dp.callback_query(F.data.startswith("vex_plat:"))
async def nav_vex_platform(call: CallbackQuery):
    parts = call.data.split(":")
    plat_key = parts[1]
    page = int(parts[2]) if len(parts) > 2 else 0
    
    # Фильтруем услуги только этой платформы
    services = []
    for s in VEX_CACHE:
        cat = str(s.get("category", "")).lower()
        if plat_key == "tiktok" and "tiktok" in cat: services.append(s)
        elif plat_key == "tg" and ("telegram" in cat or "tg" in cat): services.append(s)
        elif plat_key == "ig" and "instagram" in cat: services.append(s)
        elif plat_key == "yt" and ("youtube" in cat or "yt" in cat): services.append(s)
        elif plat_key == "vk" and "vk" in cat: services.append(s)
        elif plat_key == "other" and not any(x in cat for x in ["tiktok", "telegram", "tg", "instagram", "youtube", "yt", "vk"]): services.append(s)
        
    if not services:
        await call.answer("Нет услуг", show_alert=True)
        return
        
    # Пагинация по 8 услуг
    ITEMS = 8
    total_pages = math.ceil(len(services) / ITEMS)
    page = max(0, min(page, total_pages - 1))
    start = page * ITEMS
    end = start + ITEMS
    
    kb_rows = []
    for s in services[start:end]:
        s_id = s.get("service")
        s_name = s.get("name", "Услуга")
        rate = get_vex_rate(s)
        kb_rows.append([InlineKeyboardButton(text=f"#{s_id} | {s_name[:20]}.. | {rate}₽", callback_data=f"vex_srv:{s_id}")])
        
    nav = []
    if page > 0: nav.append(InlineKeyboardButton(text="⬅️", callback_data=f"vex_plat:{plat_key}:{page-1}"))
    nav.append(InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="noop"))
    if page < total_pages - 1: nav.append(InlineKeyboardButton(text="➡️", callback_data=f"vex_plat:{plat_key}:{page+1}"))
    kb_rows.append(nav)
    kb_rows.append([InlineKeyboardButton(text="🔙 К соцсетям", callback_data="vex_back")])
    
    await call.message.edit_text(f"📂 <b>Услуги {plat_key.upper()}</b>\nВыберите тариф:", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows), parse_mode="HTML")
    await call.answer()

@dp.callback_query(F.data == "vex_back")
async def cb_vex_back(call: CallbackQuery):
    # Имитируем нажатие кнопки "Услуги из VexBoost" чтобы обновить меню
    fake_msg = call.message
    fake_msg.text = "⚡ Услуги из VexBoost"
    await msg_vex_menu(fake_msg)
    await call.answer()

@dp.callback_query(F.data.startswith("vex_srv:"))
async def nav_vex_service(call: CallbackQuery):
    srv_id = call.data.split(":")[1]
    service = next((s for s in VEX_CACHE if str(s.get("service")) == srv_id), None)
    if not service:
        await call.answer("Не найдено", show_alert=True)
        return
        
    rate = get_vex_rate(service)
    text = (
        f"🔮 <b>ТАРИФ #{service.get('service')}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🏷 <b>Услуга:</b>\n<i>{service.get('name')}</i>\n\n"
        f"💸 <b>Цена за 1000:</b> <code>{rate} ₽</code>\n"
        f"📈 <b>Лимиты:</b> <code>{service.get('min')}</code> ➔ <code>{service.get('max')}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💡 <i>Нажмите кнопку для расчета</i>"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧮 Рассчитать", callback_data=f"vex_calc:{srv_id}")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="vex_back")]
    ])
    await call.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await call.answer()

@dp.callback_query(F.data.startswith("vex_calc:"))
async def vex_calc_start(call: CallbackQuery, state: FSMContext):
    srv_id = call.data.split(":")[1]
    service = next((s for s in VEX_CACHE if str(s.get("service")) == srv_id), None)
    if not service:
        return
        
    rate = get_vex_rate(service)
    await state.update_data(vex_srv_id=srv_id)
    await state.set_state(VexForm.calc_quantity)
    
    text = (
        f"🧮 <b>КАЛЬКУЛЯТОР // УСЛУГА #{srv_id}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💸 <b>Цена:</b> <code>{rate} ₽</code> за 1000 шт.\n"
        f"📊 <b>Лимиты:</b> от <code>{service.get('min')}</code> до <code>{service.get('max')}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"✍️ <b>Введите количество в чат:</b>"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Отмена", callback_data="vex_back")]])
    await call.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await call.answer()

@dp.message(VexForm.calc_quantity)
async def vex_calc_process(msg: Message, state: FSMContext):
    data = await state.get_data()
    srv_id = data.get("vex_srv_id")
    service = next((s for s in VEX_CACHE if str(s.get("service")) == srv_id), None)
    
    if not service:
        await msg.answer("❌ Услуга не найдена")
        await state.clear()
        return
        
    raw_text = msg.text.strip().replace(" ", "")
    if not raw_text.isdigit():
        await msg.answer("⚠️ Введите целое число (например: 1000):")
        return
        
    qty = int(raw_text)
    min_v = int(service.get("min", 1))
    max_v = int(service.get("max", 1000000))
    rate = get_vex_rate(service)
    total = round((qty * rate) / 1000, 2)
    
    warn = ""
    if qty < min_v: warn = f"\n⚠️ <i>Меньше минимума ({min_v})</i>"
    elif qty > max_v: warn = f"\n⚠️ <i>Больше максимума ({max_v})</i>"
    
    res_text = (
        f"📊 <b>РАСЧЕТ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 <b>ID услуги:</b> <code>#{srv_id}</code>\n"
        f"🏷 <b>Тариф:</b> <i>{service.get('name')}</i>\n\n"
        f"🔢 <b>Количество:</b> <code>{qty:,} шт.</code>\n"
        f"💵 <b>Цена за 1000:</b> <code>{rate} ₽</code>\n"
        f"{warn}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 <b>К оплате:</b> <code>{total:.2f} ₽</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💡 <i>Скопируйте ID услуги и оформите заказ в Mini App.</i>"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📱 Открыть Mini App", web_app=WebAppInfo(url=WEBAPP_URL))],
        [InlineKeyboardButton(text="🔙 В каталог VexBoost", callback_data="vex_back")]
    ])
    await msg.answer(res_text, reply_markup=kb, parse_mode="HTML")
    await state.clear()

@dp.callback_query(F.data == "noop")
async def nav_noop(call: CallbackQuery):
    await call.answer()
    
# ============ ДИНАМИЧЕСКИЙ КАТАЛОГ VEXBOOST ============
class VexForm(StatesGroup):
    calc_quantity = State()

# НОВЫЕ СЛОВАРИ ДЛЯ VEXBOOST (ДОБАВЛЯЕМ ИХ СЮДА)
PLATFORMS = {
    "tiktok": {"title": "TikTok", "icon": "🎵", "include": [r"tiktok", r"тикток", r"тик ток", r"\btt\b"], "exclude": []},
    "telegram": {"title": "Telegram", "icon": "✈️", "include": [r"telegram", r"телеграм", r"\btg\b", r"\bтг\b"], "exclude": []},
    "instagram": {"title": "Instagram", "icon": "📸", "include": [r"instagram", r"инстаграм", r"инст", r"\big\b"], "exclude": []},
    "vk": {"title": "ВКонтакте", "icon": "🔵", "include": [r"\bvk\b", r"вконтакте", r"\bвк\b"], "exclude": []},
    "youtube": {"title": "YouTube", "icon": "▶️", "include": [r"youtube", r"ютуб", r"\byt\b"], "exclude": []},
    "likee": {"title": "Likee", "icon": "🧡", "include": [r"\blikee\b", r"лайки апп", r"лайки видео"], "exclude": [r"facebook", r"twitter", r"\bvk\b", r"вконтакте", r"instagram", r"инстаграм", r"tiktok", r"youtube"]},
    "twitter": {"title": "Twitter / X", "icon": "🐦", "include": [r"twitter", r"твиттер", r"\bx\.com\b", r"\bx\b"], "exclude": []},
    "discord": {"title": "Discord", "icon": "👾", "include": [r"discord", r"дискорд"], "exclude": []},
    "twitch": {"title": "Twitch", "icon": "🟣", "include": [r"twitch", r"твич"], "exclude": []},
    "facebook": {"title": "Facebook", "icon": "🌐", "include": [r"facebook", r"фейсбук", r"\bfb\b"], "exclude": []},
    "threads": {"title": "Threads", "icon": "🧵", "include": [r"threads", r"тредс"], "exclude": []},
    "spotify": {"title": "Spotify", "icon": "🟢", "include": [r"spotify", r"спотифай"], "exclude": []},
    "rutube": {"title": "Rutube", "icon": "🔴", "include": [r"rutube", r"рутуб"], "exclude": []},
    "dzen": {"title": "Дзен", "icon": "⚡", "include": [r"dzen", r"дзен", r"yandex", r"яндекс"], "exclude": []},
    "avito": {"title": "Авито", "icon": "🟢", "include": [r"avito", r"авито"], "exclude": []}
}

ACTION_TYPES = {
    "subs": {"title": "Подписчики", "icon": "👥", "keys": ["подпис", "фоллов", "sub", "fol", "участник", "мембер", "member", "читател"]},
    "views": {"title": "Просмотры", "icon": "👁", "keys": ["просмотр", "view", "охват", "глаз"]},
    "likes": {"title": "Лайки", "icon": "❤️", "keys": ["лайк", "like", "heart", "сердеч", "нравит"]},
    "live": {"title": "Зрители / Стрим", "icon": "📡", "keys": ["зрител", "live", "стрим", "эфир", "stream", "онлайн"]},
    "favs": {"title": "Избранное", "icon": "⭐", "keys": ["избран", "сохран", "save", "fav", "заклад"]},
    "shares": {"title": "Репосты", "icon": "🔁", "keys": ["репост", "share", "поделит", "ретвит", "retweet"]},
    "battle": {"title": "Баттл Поинты", "icon": "⚔️", "keys": ["battle", "батл", "баттал", "point", "поинт", "pk"]},
    "comments": {"title": "Комментарии", "icon": "💬", "keys": ["коммент", "comm", "отзыв"]},
    "reactions": {"title": "Реакции", "icon": "🔥", "keys": ["реакц", "react", "эмодзи", "голос", "vote", "опрос"]}
}

def get_vex_rate(s: dict) -> float:
    try: return round(float(s.get("rate", 0)) * (1 + VEX_MARGIN / 100), 2)
    except: return 0.0

def check_service_health(s: dict) -> tuple[str, str]:
    try:
        rate, min_v, max_v = float(s.get("rate", 0)), int(s.get("min", 0)), int(s.get("max", 0))
    except: return "🔴", "Тех. работы"
    name = str(s.get("name", "")).lower()
    if rate <= 0 or max_v <= 0 or min_v > max_v: return "🔴", "Отключена"
    if any(w in name for w in ["disabled", "off", "отключ", "closed", "не работает", "drop"]): return "🟡", "Нестабильно"
    return "🟢", "Работает стабильно"

async def fetch_vex_services() -> list:
    global VEX_CACHE
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(VEX_PROVIDER_URL, data={"key": VEX_API_KEY, "action": "services"}) as resp:
                data = await resp.json(content_type=None)
                if isinstance(data, list):
                    VEX_CACHE = data
                    return data
        except: pass
    return []

def get_platform_services(platform_key: str) -> list:
    cfg = PLATFORMS.get(platform_key)
    if not cfg: return []
    res = []
    for s in VEX_CACHE:
        cat, name = str(s.get("category", "")).lower(), str(s.get("name", "")).lower()
        full = f"{cat} {name}"
        if cfg["exclude"] and any(re.search(ex, full) for ex in cfg["exclude"]): continue
        matched = False
        for pat in cfg["include"]:
            if re.search(pat, cat) or (re.search(pat, name) and platform_key != "likee"):
                matched = True; break
        if platform_key == "likee":
            matched = "likee" in cat or "лайки видео" in cat or "likee" in name
        if matched: res.append(s)
    return res

def filter_by_action(services: list, action_key: str) -> list:
    if action_key == "other":
        all_keys = [k for v in ACTION_TYPES.values() for k in v["keys"]]
        return [s for s in services if not any(k in str(s.get("name", "")).lower() for k in all_keys)]
    cfg = ACTION_TYPES.get(action_key)
    return [s for s in services if any(k in str(s.get("name", "")).lower() for k in cfg["keys"])] if cfg else []

@dp.message(F.text == "⚡ Каталог VexBoost")
async def msg_vex_menu(message: Message):
    if not VEX_CACHE:
        msg = await message.answer("⏳ Загружаю услуги из VexBoost...")
        await fetch_vex_services()
        await msg.delete()
    if not VEX_CACHE: return await message.answer("❌ Ошибка связи с API VexBoost")
    
    kb_rows = [[InlineKeyboardButton(text=f"{val['icon']} {val['title']} ({len(get_platform_services(k))})", callback_data=f"vex_plt:{k}")] for k, val in PLATFORMS.items() if get_platform_services(k)]
    kb_rows.append([InlineKeyboardButton(text="🔙 В меню", callback_data="main_menu_back")])
    await message.answer("✨ <b>КАТАЛОГ VEXBOOST</b>\n╭────────────────────────\n│ 🎯 Выберите соцсеть:\n╰────────────────────────", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows), parse_mode="HTML")

@dp.callback_query(F.data.startswith("vex_plt:"))
async def nav_vex_platform(call: CallbackQuery):
    plat_key = call.data.split(":")[1]
    plat_info = PLATFORMS.get(plat_key, {"title": "Категория", "icon": "🌐"})
    plat_services = get_platform_services(plat_key)
    if not plat_services: return await call.answer("❌ В этой категории пока нет услуг", show_alert=True)
    
    buttons = []; row = []; categorized_ids = set()
    for act_key, act_val in ACTION_TYPES.items():
        matched = filter_by_action(plat_services, act_key)
        if matched:
            for s in matched: categorized_ids.add(s.get("service"))
            row.append(InlineKeyboardButton(text=f"{act_val['icon']} {act_val['title']} ({len(matched)})", callback_data=f"vex_act:{plat_key}:{act_key}:0"))
            if len(row) == 2: buttons.append(row); row = []
    if row: buttons.append(row)
    other_services = [s for s in plat_services if s.get("service") not in categorized_ids]
    if other_services: buttons.append([InlineKeyboardButton(text=f"📦 Другие услуги ({len(other_services)})", callback_data=f"vex_act:{plat_key}:other:0")])
    buttons.append([InlineKeyboardButton(text="🔙 Выбор платформы", callback_data="vex_back")])
    
    await call.message.edit_text(f"{plat_info['icon']} <b>{plat_info['title'].upper()} // ЧТО ВАМ НУЖНО?</b>\n╭────────────────────────\n│ 🎯 Выберите тип услуги:\n│ 📊 Всего в разделе: <b>{len(plat_services)} шт.</b>\n╰────────────────────────", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode="HTML")
    await call.answer()

@dp.callback_query(F.data.startswith("vex_act:"))
async def nav_vex_action(call: CallbackQuery):
    parts = call.data.split(":")
    plat_key, act_key, page = parts[1], parts[2], int(parts[3]) if len(parts) > 3 else 0
    plat_services = get_platform_services(plat_key)
    filtered = filter_by_action(plat_services, act_key)
    if not filtered: return await call.answer("Услуг не найдено", show_alert=True)
    
    total_pages = math.ceil(len(filtered) / ITEMS_PER_PAGE)
    start_idx, end_idx = page * ITEMS_PER_PAGE, (page + 1) * ITEMS_PER_PAGE
    buttons = []
    for s in filtered[start_idx:end_idx]:
        h_icon, _ = check_service_health(s)
        buttons.append([InlineKeyboardButton(text=f"{h_icon} #{s.get('service')} ⬝ {s.get('name', 'Услуга')[:22]}", callback_data=f"vex_srv:{s.get('service')}:{plat_key}:{act_key}:{page}")])
    
    nav_row = []
    if page > 0: nav_row.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"vex_act:{plat_key}:{act_key}:{page - 1}"))
    nav_row.append(InlineKeyboardButton(text=f"📄 {page + 1}/{total_pages}", callback_data="vex_noop"))
    if page < total_pages - 1: nav_row.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"vex_act:{plat_key}:{act_key}:{page + 1}"))
    buttons.append(nav_row)
    buttons.append([InlineKeyboardButton(text="🔙 К выбору действия", callback_data=f"vex_plt:{plat_key}")])
    
    await call.message.edit_text(f"📂 <b>Услуги {plat_key.upper()}</b>\nВыберите тариф:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode="HTML")
    await call.answer()

@dp.callback_query(F.data.startswith("vex_srv:"))
async def nav_vex_service(call: CallbackQuery):
    srv_id = call.data.split(":")[1]
    service = next((s for s in VEX_CACHE if str(s.get("service")) == srv_id), None)
    if not service: return await call.answer("Не найдено", show_alert=True)
    
    text = (f"🔮 <b>ТАРИФ #{service.get('service')}</b>\n━━━━━━━━━━━━━━━━━━━━━━\n🏷 <b>Услуга:</b>\n<i>{service.get('name')}</i>\n\n💸 <b>Цена за 1000:</b> <code>{get_vex_rate(service)} ₽</code>\n📈 <b>Лимиты:</b> <code>{service.get('min')}</code> ➔ <code>{service.get('max')}</code>\n━━━━━━━━━━━━━━━━━━━━━━\n💡 <i>Нажмите кнопку для расчета</i>")
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🧮 Рассчитать", callback_data=f"vex_calc:{srv_id}")], [InlineKeyboardButton(text="🔙 Назад", callback_data="vex_back")]])
    await call.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await call.answer()

# ============ ОБРАБОТЧИК ВЫБОРА КОНКРЕТНОЙ УСЛУГИ (srv) ============
@dp.callback_query(F.data.startswith("srv|"))
async def cb_service_selected(call: CallbackQuery, state: FSMContext):
    parts = call.data.split("|")
    if len(parts) != 3:
        await call.answer("Ошибка данных", show_alert=True)
        return
        
    _, plat, key = parts
    data = SERVICES.get(plat, {})
    items_dict = data.get("items", data)
    item = items_dict.get(key)
    
    if not item:
        await call.answer("Услуга не найдена", show_alert=True)
        return
        
    # --- КРАСИВОЕ ОПИСАНИЕ С ЭМОДЗИ ---
    # Убираем упоминания панелей из описания
    clean_desc = item.get('desc', 'Без описания')
    for p in ["panel_1", "panel_2", "panel_3", "panel_4", "SMM"]:
        clean_desc = clean_desc.replace(p, "")
    
    # Берем иконку платформы
    plat_icons = {
        "telegram": "✈️", "tiktok": "🎵", "youtube": "▶️", 
        "instagram": "📸", "vk": "🅱️", "twitch": "🎮",
        "twitter": "🐦", "likee": "🎬", "facebook": "📘",
        "rutube": "🟣", "max": "💠", "whatsapp": "🟢"
    }
    icon = plat_icons.get(plat, "📦")
    
    # Формируем красивый текст
    text = (
        f"✨ <b>ВЫБРАННАЯ УСЛУГА</b> ✨\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{icon} <b>Платформа:</b> {plat.upper()}\n"
        f"🏷 <b>Название:</b>\n<i>{item['name']}</i>\n\n"
        f"📝 <b>Описание:</b>\n<i>{clean_desc.strip()}</i>\n\n"
        f"💰 <b>Цена:</b> <code>{item['price']} ₽</code> за {item.get('pack', 1000)} шт.\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔢 <b>Введите количество в чат</b> (например: <code>1000</code>):"
    )
    
    await state.update_data(plat=plat, key=key)
    await state.set_state(OrderStates.waiting_quantity)
    
    # --- ДОБАВЛЯЕМ КНОПКУ НАЗАД ---
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад к категориям", callback_data=f"plat_{plat}")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="back_platforms")]
    ])
    
    try:
        await call.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        await call.message.answer(text, reply_markup=kb, parse_mode="HTML")
        
    await call.answer()
    
@dp.callback_query(F.data.startswith("vex_calc:"))
async def vex_calc_start(call: CallbackQuery, state: FSMContext):
    srv_id = call.data.split(":")[1]
    service = next((s for s in VEX_CACHE if str(s.get("service")) == srv_id), None)
    if not service: return
    await state.update_data(vex_srv_id=srv_id)
    await state.set_state(VexForm.calc_quantity)
    text = (f"🧮 <b>КАЛЬКУЛЯТОР // УСЛУГА #{srv_id}</b>\n━━━━━━━━━━━━━━━━━━━━━━\n💸 <b>Цена:</b> <code>{get_vex_rate(service)} ₽</code> за 1000 шт.\n📊 <b>Лимиты:</b> от <code>{service.get('min')}</code> до <code>{service.get('max')}</code>\n━━━━━━━━━━━━━━━━━━━━━━\n✍️ <b>Введите количество в чат:</b>")
    await call.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Отмена", callback_data="vex_back")]]), parse_mode="HTML")
    await call.answer()

@dp.message(VexForm.calc_quantity)
async def vex_calc_process(msg: Message, state: FSMContext):
    data = await state.get_data()
    srv_id = data.get("vex_srv_id")
    service = next((s for s in VEX_CACHE if str(s.get("service")) == srv_id), None)
    if not service: await state.clear(); return await msg.answer("❌ Услуга не найдена")
    if not msg.text.strip().isdigit(): return await msg.answer("⚠️ Введите целое число (например: 1000):")
    
    qty = int(msg.text.strip())
    rate = get_vex_rate(service)
    total = round((qty * rate) / 1000, 2)
    
    warn = ""
    if qty < int(service.get("min", 1)): warn = f"\n⚠️ <i>Меньше минимума</i>"
    elif qty > int(service.get("max", 1000000)): warn = f"\n⚠️ <i>Больше максимума</i>"
    
    res_text = (f"📊 <b>РАСЧЕТ</b>\n━━━━━━━━━━━━━━━━━━━━━━\n🏷 <b>Тариф:</b> <i>{service.get('name')}</i>\n\n🔢 <b>Количество:</b> <code>{qty:,} шт.</code>\n💵 <b>Цена за 1000:</b> <code>{rate} ₽</code>{warn}\n━━━━━━━━━━━━━━━━━━━━━━\n💰 <b>К оплате:</b> <code>{total:.2f} ₽</code>\n━━━━━━━━━━━━━━━━━━━━━━\n💡 <i>Оформите заказ в Mini App, указав ID: {srv_id}</i>")
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="📱 Открыть Mini App", web_app=WebAppInfo(url=WEBAPP_URL))], [InlineKeyboardButton(text="🔙 В каталог", callback_data="vex_back")]])
    await msg.answer(res_text, reply_markup=kb, parse_mode="HTML")
    await state.clear()

@dp.callback_query(F.data == "vex_back")
async def cb_vex_back(call: CallbackQuery):
    fake_msg = call.message; fake_msg.text = "⚡ Каталог VexBoost"
    await msg_vex_menu(fake_msg); await call.answer()

@dp.callback_query(F.data == "main_menu_back")
async def cb_main_menu_back(call: CallbackQuery):
    await call.message.edit_text("🏠 Главное меню", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⚡ Каталог VexBoost", callback_data="vex_back")]]))
    await call.answer()

@dp.callback_query(F.data == "vex_noop")
async def nav_vex_noop(call: CallbackQuery): await call.answer()

# ============ КОМАНДА ДЛЯ ОСТАНОВКИ ПЛАВНОЙ НАКРУТКИ ============
@dp.message(Command("stop"))
async def cmd_stop_order(message: Message):
    # Проверяем, что это админ (чтобы клиенты не баловались)
    # Если хочешь, чтобы клиенты сами могли останавливать, убери проверку if message.from_user.id != ADMIN_ID:
    
    args = message.text.split()
    if len(args) != 2:
        await message.answer("⚠️ Формат: `/stop <ID_заказа>`\n\nНапример: `/stop 2`")
        return
        
    try:
        order_id = int(args[1])
    except ValueError:
        await message.answer("⚠️ ID заказа должен быть числом.")
        return

    # Ищем заказ в базе плавных заказов
    conn = db_connect(); cur = conn.cursor()
    cur.execute("SELECT id, status FROM privat_orders WHERE order_id = ?", (order_id,))
    row = cur.fetchone()
    
    if not row:
        await message.answer(f"❌ Плавный заказ #{order_id} не найден или уже завершен.")
        conn.close()
        return
        
    if row[1] != 'active':
        await message.answer(f"ℹ️ Заказ #{order_id} уже имеет статус `{row[1]}`.")
        conn.close()
        return

    # Меняем статус на canceled (или done)
    cur.execute("UPDATE privat_orders SET status = 'canceled' WHERE order_id = ?", (order_id,))
    cur.execute("UPDATE orders SET status = 'canceled' WHERE id = ?", (order_id,))
    conn.commit()
    conn.close()

    await message.answer(
        f"🛑 *Заказ #{order_id} остановлен!*\n\n"
        f"Бот больше не будет отправлять партии в панель.\n"
        f"⚠️ _Примечание: Если ты хочешь вернуть деньги за неотправленную услугу, напиши в подержку и я верну вам ._",
        parse_mode="Markdown"
    )
    await log_to_channel(f"🛑 Админ остановил плавный заказ #{order_id}")
    
async def main():
    db_init()
    
    # КРАСИВЫЙ СТАРТОВЫЙ ЭКРАН
    print("\n" + "="*50)
    
    # ДОБАВЬ ЭТУ СТРОКУ, ЧТОБЫ ЗАГРУЗИТЬ УСЛУГИ ПРИ СТАРТЕ
    print("⏳ Загрузка услуг из VexBoost...")
    await fetch_vex_services()
    
    print("🚀 ISMABOOST ULTRA — БОТ ЗАПУЩЕН 🚀")
    print("="*50)
    print("="*50)
    print(f"👤 Админ ID: {ADMIN_ID}")
    print(f"🌐 Mini App: {WEBAPP_URL}")
    print(f"🗄 База данных: {DB_PATH}")
    print("-" * 50)
    print(f"🎁 Пакетов загружено: {len(BUNDLES)}")
    print(f"📦 Всего услуг в каталоге: {sum(len(p.get('items', p)) for p in SERVICES.values())}")
    print(f"💳 Панелей SMM: {len(PANELS)}")
    print(f"🛡 Антифлуд: {FLOOD_MSG_LIMIT} msg / {FLOOD_CB_LIMIT} cb")
    print("-" * 50)
    print("⚙️ АКТИВНЫЕ МОДУЛИ:")
    print("  ✅ Выдача заказов в панели (VingBoost, VexBoost)")
    print("  ✅ Пополнение CryptoBot (Авто)")
    print("  ✅ Пополнение СБП / Т-Банк")
    print("  ✅ Система рефералов (5%)")
    print("  ✅ Промокоды и Скидки (Первый заказ, Выходные)")
    print("  ✅ Умный подбор (Квиз)")
    print("  ✅ Игры (PUBG, Roblox, Brawl Stars, BR)")
    print("  ✅ Рулетка и Слепая коробка")
    print("  ✅ Аукцион")
    print("  ✅ Система Тикетов и Поддержки")
    print("  ✅ Плавная накрутка (3-60 дней, прогресс-уведомления)")
    print("="*50)
    print("🟢 БОТ ГОТОВ К ПРИЕМУ ЗАКАЗОВ! Ожидание сообщений...\n")

    while True:
        try:
            await bot.delete_webhook(drop_pending_updates=True)
            asyncio.create_task(check_payments_loop())
            asyncio.create_task(check_panel_statuses_loop())
            asyncio.create_task(process_privat_orders_loop())
            await dp.start_polling(bot)
        except Exception as e:
            print(f"⚠️ Бот упал: {e}. Перезапуск через 15 сек...")
            await asyncio.sleep(15)    

# ============ ОБРАБОТЧИК ВЫБОРА КОНКРЕТНОЙ УСЛУГИ (srv) ============
@dp.callback_query(F.data.startswith("srv|"))
async def cb_service_selected(call: CallbackQuery, state: FSMContext):
    parts = call.data.split("|")
    if len(parts) != 3:
        await call.answer("Ошибка данных", show_alert=True)
        return
        
    _, plat, key = parts
    data = SERVICES.get(plat, {})
    items_dict = data.get("items", data)
    item = items_dict.get(key)
    
    if not item:
        await call.answer("Услуга не найдена", show_alert=True)
        return
        
    # --- КРАСИВОЕ ОПИСАНИЕ С ЭМОДЗИ ---
    clean_desc = item.get('desc', 'Без описания')
    for p in ["panel_1", "panel_2", "panel_3", "panel_4", "SMM"]:
        clean_desc = clean_desc.replace(p, "")
    
    # Берем иконку платформы
    plat_icons = {
        "telegram": "✈️", "tiktok": "🎵", "youtube": "▶️", 
        "instagram": "📸", "vk": "🅱️", "twitch": "🎮",
        "twitter": "🐦", "likee": "🎬", "facebook": "📘",
        "rutube": "🟣", "max": "💠", "whatsapp": "🟢"
    }
    icon = plat_icons.get(plat, "📦")
    
    # Формируем красивый текст
    text = (
        f"✨ <b>ВЫБРАННАЯ УСЛУГА</b> ✨\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{icon} <b>Платформа:</b> {plat.upper()}\n"
        f"🏷 <b>Название:</b>\n<i>{item['name']}</i>\n\n"
        f"📝 <b>Описание:</b>\n<i>{clean_desc.strip()}</i>\n\n"
        f"💰 <b>Цена:</b> <code>{item['price']} ₽</code> за {item.get('pack', 1000)} шт.\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔢 <b>Введите количество в чат</b> (например: <code>1000</code>):"
    )
    
    await state.update_data(plat=plat, key=key)
    await state.set_state(OrderStates.waiting_quantity)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад к категориям", callback_data=f"plat_{plat}")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="back_platforms")]
    ])
    
    try:
        await call.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        await call.message.answer(text, reply_markup=kb, parse_mode="HTML")
        
    await call.answer()
    
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("⛔ Бот остановлен")